import os
import signal
import subprocess
from typing import List
from mcp.types import TextContent
from ....utils.logging import setup_logging


logger = setup_logging("stop_daemon_handler")


async def handle_stop_daemon(args: dict = None) -> List[TextContent]:
    """Handle the stop-daemon tool request."""
    try:
        # Find any running daemon processes
        result = subprocess.run(
            ["pgrep", "-f", "playwright_mcp.browser_daemon.browser_manager"],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            # Kill each process
            for pid in result.stdout.strip().split('\n'):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    logger.info(f"Sent SIGTERM to process {pid}")
                except ProcessLookupError:
                    pass  # Process already gone
            
            return [TextContent(type="text", text="Browser daemon stopped successfully")]
        else:
            return [TextContent(type="text", text="No running daemon found")]
            
    except Exception as e:
        logger.error(f"Failed to stop daemon: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")] 