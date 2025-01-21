from typing import Dict
import asyncio
from .utils import check_daemon_running, start_daemon, create_response


async def handle_start_daemon(arguments: Dict) -> list:
    """Handle start-daemon command by starting the browser daemon if it's not running."""
    # Check if daemon is already running
    if await check_daemon_running():
        return create_response("Browser daemon is already running")
        
    # Start daemon
    await start_daemon()
    
    # Wait for daemon to start (up to 5 seconds)
    for _ in range(10):
        if await check_daemon_running():
            return create_response("Browser daemon started successfully")
        await asyncio.sleep(0.5)
        
    raise Exception("Failed to start browser daemon: timeout waiting for daemon to start") 