from typing import Dict, List
import asyncio
from mcp.types import TextContent
from .utils import check_daemon_running, start_daemon


async def handle_start_daemon(arguments: Dict) -> List[TextContent]:
    """Handle start-daemon command by starting the browser daemon if it's not running."""
    try:
        # Check if daemon is already running
        if await check_daemon_running():
            return [TextContent(
                type="text",
                text="Browser daemon is already running"
            )]
            
        # Start daemon
        await start_daemon()
        
        # Wait for daemon to start (up to 5 seconds)
        for _ in range(10):
            if await check_daemon_running():
                return [TextContent(
                    type="text",
                    text="Browser daemon started successfully"
                )]
            await asyncio.sleep(0.5)
            
        return [TextContent(
            type="text",
            text="Failed to start browser daemon: timeout waiting for daemon to start"
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Failed to start browser daemon: {str(e)}"
        )] 