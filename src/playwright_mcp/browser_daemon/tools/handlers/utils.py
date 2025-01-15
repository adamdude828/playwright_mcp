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
import subprocess
import sys
from mcp.types import TextContent
from ....utils.logging import setup_logging


# Configure logging
logger = setup_logging("handler_utils")


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
    env['LOG_LEVEL'] = 'INFO'  # Use INFO level by default
    
    # Create logs directory if needed
    logs_dir = os.path.join(project_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Start the daemon as a background process
    try:
        process = subprocess.Popen(
            [sys.executable, '-m', 'playwright_mcp.browser_daemon.browser_manager'],
            stdout=subprocess.DEVNULL,  # Don't capture output to avoid blocking
            stderr=subprocess.DEVNULL,
            env=env,
            cwd=project_root
        )
        
        logger.info("Daemon start command issued")
        
        # Give the process a moment to start
        await asyncio.sleep(1)
        
        # Verify the process is still running
        if process.poll() is not None:
            raise Exception(f"Daemon process exited immediately with code {process.returncode}")
            
        # Wait for the socket to become available (up to 5 seconds)
        socket_path = os.path.join(os.getenv('TMPDIR', '/tmp'), 'playwright_mcp.sock')
        for _ in range(10):
            if os.path.exists(socket_path):
                # Verify we can connect
                if await check_daemon_running():
                    logger.info("Daemon started successfully")
                    return
            await asyncio.sleep(0.5)
            
        raise Exception("Daemon started but socket connection could not be established")
            
    except Exception as e:
        logger.error(f"Error starting daemon: {str(e)}")
        raise Exception(f"Failed to start daemon: {str(e)}")


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
        reader, writer = await asyncio.open_unix_connection(socket_path)
        logger.debug("Connected to browser manager")

        # Send request with delimiter
        request = {"command": command, "args": args}
        logger.debug(f"Sending request: {request}")
        writer.write(json.dumps(request).encode() + b'\n')
        await writer.drain()

        # Read response with a large buffer size
        response = await reader.read(1024 * 1024)  # 1MB buffer
        if b'\n' in response:
            response = response.split(b'\n')[0]  # Take everything up to first newline
        response_data = json.loads(response.decode())
        logger.debug(f"Received response: {response_data}")

        writer.close()
        await writer.wait_closed()
        
        if "error" in response_data:
            raise ValueError(response_data["error"])
            
        return response_data
    except (ConnectionRefusedError, FileNotFoundError):
        raise Exception("Browser daemon is not running. Please call the 'start-daemon' tool first.")
    except Exception as e:
        raise Exception(str(e))


def create_response(text: str | dict, is_error: bool = False) -> dict:
    """Create a standard MCP-compliant response.
    
    Formats the given text or data into an MCP protocol response object with
    appropriate content type and error status.
    
    Args:
        text: The response text or data dictionary to format
        is_error: Whether this response represents an error condition
        
    Returns:
        dict: An MCP-compliant response object with structure:
            {
                "isError": bool,
                "content": [
                    {
                        "type": "text",
                        "text": str
                    }
                ]
            }
            
    Note:
        Dictionary inputs are automatically serialized to JSON strings.
        All responses use type="text" as per MCP protocol requirements.
    """
    if isinstance(text, dict):
        content = [TextContent(type="text", text=json.dumps(text, indent=2))]
    else:
        content = [TextContent(type="text", text=str(text))]
        
    return {
        "isError": is_error,
        "content": content
    }
