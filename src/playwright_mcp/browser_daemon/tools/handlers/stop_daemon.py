from typing import Dict, List
import asyncio
import os
import signal
import subprocess
from mcp.types import TextContent
from .utils import check_daemon_running


async def handle_stop_daemon(arguments: Dict) -> List[TextContent]:
    """Handle stop-daemon command by stopping the browser daemon if it's running."""
    try:
        # Check if daemon is running
        if not await check_daemon_running():
            return [TextContent(type="text", text="No running daemon found")]
            
        # Find and kill daemon process
        result = subprocess.run(
            ["pgrep", "-f", "playwright_mcp.browser_daemon.browser_manager"],
            capture_output=True,
            text=True
        )
        
        if not result.stdout:
            return [TextContent(type="text", text="No daemon process found")]
            
        # Kill each matching process
        for pid in result.stdout.strip().split('\n'):
            try:
                os.kill(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
                
        # Wait for processes to terminate (up to 5 seconds)
        for _ in range(10):
            if not await check_daemon_running():
                # Also try to remove the socket file
                socket_path = os.path.join(os.getenv('TMPDIR', '/tmp'), 'playwright_mcp.sock')
                try:
                    os.unlink(socket_path)
                except OSError:
                    pass
                return [TextContent(type="text", text="Browser daemon stopped successfully")]
            await asyncio.sleep(0.5)
            
        return [TextContent(type="text", text="Failed to stop browser daemon: timeout waiting for daemon to stop")]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Failed to stop browser daemon: {str(e)}")] 