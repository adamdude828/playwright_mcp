import asyncio
import os
import sys
import tempfile
from typing import List
from mcp.types import TextContent
from ....utils.logging import setup_logging


logger = setup_logging("launch_browser_handler")


async def check_daemon_running() -> bool:
    """Check if the browser daemon is running by attempting to ping it."""
    try:
        reader, writer = await asyncio.open_unix_connection(
            os.path.join(tempfile.gettempdir(), 'playwright_mcp.sock')
        )
        writer.write(b"ping\n")
        await writer.drain()
        
        response = await reader.readline()
        writer.close()
        await writer.wait_closed()
        
        return response.decode().strip() == "pong"
    except (OSError, asyncio.TimeoutError):
        return False


async def start_daemon() -> None:
    """Start the browser daemon if it's not running."""
    # Start the daemon as a module in the background using nohup
    os.system(f"nohup {sys.executable} -m playwright_mcp.browser_daemon.browser_manager > /dev/null 2>&1 &")
    
    # Wait for daemon to start (max 5 seconds)
    for _ in range(10):
        if await check_daemon_running():
            return
        await asyncio.sleep(0.5)
    
    raise Exception("Failed to start browser daemon")


async def handle_launch_browser(args: dict) -> List[TextContent]:
    """Handle the launch-browser tool request."""
    try:
        # First check if daemon is running
        if not await check_daemon_running():
            logger.info("Browser daemon not running, attempting to start via MCP...")
            try:
                # Try using the MCP tool first
                reader, writer = await asyncio.open_unix_connection(
                    os.path.join(tempfile.gettempdir(), 'playwright_mcp.sock')
                )
                writer.write(b"start-daemon\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except (OSError, asyncio.TimeoutError) as e:
                # If MCP connection fails, start directly
                logger.info(f"Starting daemon directly (MCP connection failed: {e})...")
                await start_daemon()
        
        # Now try to connect and launch browser (with retries)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Connect to daemon
                reader, writer = await asyncio.open_unix_connection(
                    os.path.join(tempfile.gettempdir(), 'playwright_mcp.sock')
                )
                
                # Get browser parameters
                browser_type = args.get("browser_type", "chromium")
                headless = args.get("headless", True)
                
                # Send launch command
                command = f"launch:{browser_type}:{headless}\n"
                writer.write(command.encode())
                await writer.drain()
                
                # Get response
                response = await reader.readline()
                writer.close()
                await writer.wait_closed()
                
                response_text = response.decode().strip()
                if response_text.startswith("ok:"):
                    session_id = response_text.split(":")[1]
                    return [TextContent(type="text", text=f"Browser launched with session ID: {session_id}")]
                else:
                    raise Exception(f"Failed to launch browser: {response_text}")
                    
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise
                logger.warning(f"Launch attempt {attempt + 1} failed: {e}, retrying...")
                await asyncio.sleep(1)  # Wait before retry
                
    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
