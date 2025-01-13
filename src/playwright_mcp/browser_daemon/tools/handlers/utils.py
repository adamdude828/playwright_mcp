import asyncio
import json
import os
import subprocess
import sys
from ....utils.logging import setup_logging


# Configure logging
logger = setup_logging("mcp_server")


async def check_daemon_running() -> bool:
    """Check if the browser daemon is running by attempting to ping it."""
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
    
    # Run the daemon module directly in background
    cmd = f"nohup {sys.executable} -m playwright_mcp.browser_daemon.browser_manager > daemon.log 2>&1 &"
    logger.debug(f"Running command: {cmd}")
    subprocess.Popen(cmd, shell=True)
    
    logger.info("Daemon start command issued")


async def send_to_manager(command: str, args: dict) -> dict:
    """Send a command to the browser manager service."""
    socket_path = os.path.join(os.getenv('TMPDIR', '/tmp'), 'playwright_mcp.sock')
    logger.info(f"Attempting to connect to browser manager at {socket_path}")

    # Check if socket exists first
    if not os.path.exists(socket_path):
        raise Exception("Browser daemon is not running. Please call the 'start-daemon' tool first.")

    try:
        reader, writer = await asyncio.open_unix_connection(socket_path)
        logger.debug("Connected to browser manager")

        # Send request
        request = {"command": command, "args": args}
        logger.debug(f"Sending request: {request}")
        writer.write(json.dumps(request).encode() + b'\n')
        await writer.drain()

        # Get response
        logger.debug("Waiting for response...")
        response = await reader.readline()
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
