from typing import Dict
import asyncio
import os
import signal
import subprocess
from .utils import create_response, check_daemon_running


async def handle_stop_daemon(arguments: Dict) -> Dict:
    """Handle stop-daemon command by stopping the browser daemon if it's running."""
    try:
        # Check if daemon is running
        if not await check_daemon_running():
            return create_response("No running daemon found")
            
        # Find and kill daemon process
        result = subprocess.run(
            ["pgrep", "-f", "playwright_mcp.browser_daemon.browser_manager"],
            capture_output=True,
            text=True
        )
        
        if not result.stdout:
            return create_response("No daemon process found")
            
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
                return create_response("Browser daemon stopped successfully")
            await asyncio.sleep(0.5)
            
        return create_response("Failed to stop browser daemon: timeout waiting for daemon to stop", is_error=True)
        
    except Exception as e:
        return create_response(f"Failed to stop browser daemon: {str(e)}", is_error=True) 