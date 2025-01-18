"""Utility functions for MCP tool handlers and browser daemon communication.

This module provides core utilities for:
1. Browser daemon management (checking status, starting daemon)
2. Inter-process communication with the browser daemon
3. MCP-compliant response formatting

The browser daemon is a long-running process that manages browser instances and
handles browser automation commands. Communication happens over a Unix domain socket.

Example:
    ```python
    # Check if daemon is running
    is_running = await check_daemon_running()
    if not is_running:
        await start_daemon()
        
    # Send command to daemon
    result = await send_to_manager("launch_browser", {"browser_type": "chromium"})
    
    # Format MCP response
    response = create_response(result)
    ```
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any
from playwright.async_api import Page
from mcp.types import TextContent
from ....utils.logging import setup_logging


# Configure logging
logger = setup_logging("handler_utils")

# Store page instances
_page_instances: Dict[str, Page] = {}


def get_page(page_id: str) -> Page:
    """Get a Playwright page instance by its ID.
    
    Args:
        page_id: The unique identifier for the page
        
    Returns:
        Page: The Playwright page instance
        
    Raises:
        ValueError: If the page_id is not found
    """
    if page_id not in _page_instances:
        raise ValueError(f"Page {page_id} not found")
    return _page_instances[page_id]


def register_page(page_id: str, page: Page) -> None:
    """Register a Playwright page instance.
    
    Args:
        page_id: The unique identifier for the page
        page: The Playwright page instance
    """
    _page_instances[page_id] = page


async def check_daemon_running() -> bool:
    """Check if the browser daemon is running by attempting to ping it.
    
    Makes a connection attempt to the daemon's Unix domain socket and sends
    a ping command. The daemon is considered running if it responds with 'pong'.
    
    Returns:
        bool: True if daemon is running and responsive, False otherwise
    
    Note:
        This function handles its own exceptions and always returns a boolean.
        Failed connections, timeouts, etc. all result in False.
    """
    socket_path = os.path.join(os.getenv('TMPDIR', '/tmp'), 'playwright_mcp.sock')
    logger.debug(f"Checking if daemon is running at socket: {socket_path}")
    
    # First check if the socket file exists
    if not os.path.exists(socket_path):
        logger.debug("Socket file does not exist")
        return False
        
    try:
        logger.debug("Socket exists, attempting to connect...")
        reader, writer = await asyncio.open_unix_connection(socket_path)
        writer.write(json.dumps({"command": "ping"}).encode() + b'\n')
        await writer.drain()
        
        response = await reader.readline()
        writer.close()
        await writer.wait_closed()
        
        response_data = json.loads(response.decode())
        is_running = response_data.get("result") == "pong"
        logger.debug(f"Daemon running check result: {is_running}")
        return is_running
    except (OSError, asyncio.TimeoutError, json.JSONDecodeError) as e:
        logger.debug(f"Error checking if daemon running: {e}")
        return False


async def start_daemon() -> None:
    """Start the browser daemon if it's not running."""
    logger.info("Starting browser daemon...")
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    src_dir = os.path.join(project_root, 'src')
    
    # Set up the Python path to include the src directory
    env = os.environ.copy()
    env['PYTHONPATH'] = src_dir
    
    # Load .env file from project root
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env[key.strip()] = value.strip().strip('"\'')
    
    # Ensure LOG_LEVEL is set for the daemon process
    if 'LOG_LEVEL' in os.environ:
        logger.debug(f"Setting daemon LOG_LEVEL to {os.environ['LOG_LEVEL']}")
        env['LOG_LEVEL'] = os.environ['LOG_LEVEL']
    else:
        logger.debug("No LOG_LEVEL set, defaulting to INFO")
        env['LOG_LEVEL'] = 'INFO'
    
    # Create logs directory if needed
    logs_dir = os.path.join(project_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Open log files for the daemon process
    debug_log = open(os.path.join(logs_dir, 'debug.log'), 'a', buffering=1)  # Line buffered
    error_log = open(os.path.join(logs_dir, 'error.log'), 'a', buffering=1)  # Line buffered
    
    try:
        # Start process with file descriptors for logs
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            '-m',
            'playwright_mcp.browser_daemon',
            stdout=debug_log.fileno(),
            stderr=error_log.fileno(),
            env=env,
            cwd=project_root
        )
        
        logger.info("Daemon start command issued")
        
        # Give the process a moment to start
        await asyncio.sleep(1)
        
        # Verify the process is still running
        if process.returncode is not None:
            raise Exception(f"Daemon process exited immediately with code {process.returncode}")
            
        # Wait for the socket to become available (up to 5 seconds)
        socket_path = os.path.join(os.getenv('TMPDIR', '/tmp'), 'playwright_mcp.sock')
        for _ in range(10):
            if os.path.exists(socket_path):
                # Verify we can connect
                if await check_daemon_running():
                    logger.info("Daemon started successfully")
                    debug_log.flush()  # Ensure logs are written
                    error_log.flush()
                    return
            await asyncio.sleep(0.5)
            
        raise Exception("Daemon started but socket connection could not be established")
            
    except Exception as e:
        logger.error(f"Error starting daemon: {str(e)}")
        raise Exception(f"Failed to start daemon: {str(e)}")
    finally:
        # Flush and close log files
        debug_log.flush()
        error_log.flush()
        debug_log.close()
        error_log.close()


async def send_to_manager(command: str, args: dict) -> dict:
    """Send a command to the browser manager service.
    
    Establishes a connection to the browser daemon's Unix domain socket and sends
    a JSON-encoded command with arguments. Waits for and parses the response.
    
    Args:
        command: The command name to execute
        args: Dictionary of arguments for the command
        
    Returns:
        dict: The parsed response data from the daemon
        
    Raises:
        Exception: If daemon is not running or connection fails
        ValueError: If daemon returns an error response
        
    Note:
        The connection is closed after receiving the response. For long-running
        operations, the daemon maintains state independently of this connection.
    """
    socket_path = os.path.join(os.getenv('TMPDIR', '/tmp'), 'playwright_mcp.sock')
    logger.info(f"Attempting to connect to browser manager at {socket_path}")

    # Check if socket exists first
    if not os.path.exists(socket_path):
        raise Exception("Browser daemon is not running. Please call the 'start-daemon' tool first.")

    try:
        logger.debug("Attempting to connect to browser manager")
        logger.debug(f"Socket path: {socket_path}")
        logger.debug(f"Socket exists: {os.path.exists(socket_path)}")
        
        try:
            reader, writer = await asyncio.open_unix_connection(socket_path)
            logger.debug("Connected to browser manager")
        except ConnectionRefusedError as e:
            logger.error(f"Connection refused to socket {socket_path}. Socket file exists but no process is listening.")
            raise Exception(f"Browser daemon socket exists but is not accepting connections: {e}")
        except PermissionError as e:
            logger.error(f"Permission denied accessing socket {socket_path}")
            raise Exception(f"Permission denied accessing browser daemon socket: {e}")
        except OSError as e:
            logger.error(f"OS error connecting to socket {socket_path}: {e}")
            raise Exception(f"Failed to connect to browser daemon socket: {e}")

        # Send request with delimiter
        request = {"command": command, "args": args}
        logger.debug(f"Sending request: {request}")
        writer.write(json.dumps(request).encode() + b'\n')
        await writer.drain()

        # Read response with a large buffer size
        response = await reader.read(1024 * 1024)  # 1MB buffer
        if b'\n' in response:
            response = response.split(b'\n')[0]  # Take everything up to first newline
            
        writer.close()
        await writer.wait_closed()

        # Parse response
        try:
            response_text = response.decode()
            logger.debug(f"Received response: {response_text}")
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to fix Python-style single quotes
            response_text = response_text.replace("'", '"')
            return json.loads(response_text)

    except Exception as e:
        logger.error(f"Error sending command to browser manager: {e}")
        raise


def create_response(data: Any, is_error: bool = False) -> dict:
    """Create a standardized MCP response dictionary.
    
    Args:
        data: The response data or error message
        is_error: Whether this is an error response
        
    Returns:
        dict: A standardized MCP response with isError and content array
    """
    response = {
        "isError": is_error,
        "content": []
    }

    if isinstance(data, dict):
        # For dictionaries, convert to JSON string
        response["content"].append(TextContent(
            type="text",
            text=json.dumps(data)
        ))
    else:
        # For everything else, convert to string
        response["content"].append(TextContent(
            type="text",
            text=str(data)
        ))

    return response
