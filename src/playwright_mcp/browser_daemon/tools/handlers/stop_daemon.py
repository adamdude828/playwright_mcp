from typing import Dict, List
import asyncio
import os
import signal
import subprocess
from mcp.types import TextContent
from .utils import logger


async def handle_stop_daemon(arguments: Dict) -> List[TextContent]:
    """Handle stop-daemon command by stopping the browser daemon if it's running."""
    try:
        # Find daemon process first
        result = subprocess.run(
            ["pgrep", "-f", "playwright_mcp.browser_daemon$"],
            capture_output=True,
            text=True
        )
        
        if not result.stdout:
            # Also try to remove the socket file in case it exists
            socket_path = os.path.join(os.getenv('TMPDIR', '/tmp'), 'playwright_mcp.sock')
            try:
                os.unlink(socket_path)
            except OSError:
                pass
            return [TextContent(type="text", text="Browser daemon stopped successfully")]
            
        # Kill each matching process
        for pid in result.stdout.strip().split('\n'):
            try:
                os.kill(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
                
        # Wait for processes to terminate (up to 5 seconds)
        for _ in range(10):
            # Check if process is still running
            check_result = subprocess.run(
                ["pgrep", "-f", "playwright_mcp.browser_daemon$"],
                capture_output=True,
                text=True
            )
            if not check_result.stdout:
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
        logger.error(f"Error in handle_stop_daemon: {e}")
        return [TextContent(type="text", text=str(e))] 