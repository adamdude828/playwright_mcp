import asyncio
import os
import sys
from typing import List
from mcp.types import TextContent
from ....utils.logging import setup_logging


logger = setup_logging("start_daemon_handler")


async def handle_start_daemon(args: dict = None) -> List[TextContent]:
    """Handle the start-daemon tool request."""
    try:
        # Start the daemon as a module in the background using nohup
        os.system(f"nohup {sys.executable} -m playwright_mcp.browser_daemon.browser_manager > /dev/null 2>&1 &")
        
        # Wait for daemon to start (max 5 seconds)
        socket_path = os.path.join(os.getenv('TMPDIR', '/tmp'), 'playwright_mcp.sock')
        for _ in range(10):
            if os.path.exists(socket_path):
                return [TextContent(type="text", text="Browser daemon started successfully")]
            await asyncio.sleep(0.5)
        
        raise Exception("Failed to start browser daemon (timeout)")
    except Exception as e:
        logger.error(f"Failed to start daemon: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")] 