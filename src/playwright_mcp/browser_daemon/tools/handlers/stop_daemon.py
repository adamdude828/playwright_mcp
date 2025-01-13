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
            ["ps", "-o", "pid,etime", "-p", subprocess.check_output(
                ["pgrep", "-f", "playwright_mcp.browser_daemon.browser_manager"],
                text=True
            ).strip()],
            capture_output=True,
            text=True
        )
        
        # Parse the output to find processes running for more than 2 seconds
        daemon_pids = []
        if result.stdout:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    pid = parts[0]
                    elapsed = parts[1]
                    # Only consider it a daemon if it's been running for more than 2 seconds
                    if ':' in elapsed or int(elapsed) > 2:
                        daemon_pids.append(pid)
        
        if daemon_pids:
            # Kill each daemon process
            for pid in daemon_pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    logger.info(f"Sent SIGTERM to process {pid}")
                except ProcessLookupError:
                    pass  # Process already gone
            
            return [TextContent(type="text", text="Browser daemon stopped successfully")]
        else:
            return [TextContent(type="text", text="No running daemon found")]
            
    except subprocess.CalledProcessError:
        # No processes found by pgrep
        return [TextContent(type="text", text="No running daemon found")]
    except Exception as e:
        logger.error(f"Failed to stop daemon: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")] 