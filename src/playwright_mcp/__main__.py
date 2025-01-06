"""Main entry point for the package."""
import asyncio
import subprocess
import sys
import argparse
from .utils.logging import setup_logging
from .mcp_server.server import start_server

# Configure logging
logger = setup_logging("playwright_mcp")


async def run_both():
    """Run both the MCP server and browser daemon.
    
    This function starts the browser daemon in a separate process and then
    runs the MCP server in the current process. It handles graceful shutdown
    of both services on interruption or error.
    """
    daemon_process = None
    try:
        # Start browser daemon in a separate process
        daemon_process = await asyncio.create_subprocess_exec(
            sys.executable, 
            "-c", 
            "from playwright_mcp.browser_daemon.browser_manager import main; asyncio.run(main())",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info("Browser daemon started")

        # Run the MCP server
        await start_server()
    except KeyboardInterrupt:
        logger.info("Shutting down services...")
        if daemon_process:
            daemon_process.terminate()
            await daemon_process.wait()
    except Exception as e:
        logger.error("Server error: %s", str(e))
        if daemon_process:
            daemon_process.terminate()
            await daemon_process.wait()
        raise


async def run_server_only():
    """Run only the MCP server without the browser daemon."""
    try:
        await start_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error: %s", str(e))
        raise


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Playwright MCP Server")
    parser.add_argument(
        "--mode",
        choices=["server", "both"],
        default="both",
        help="Run mode: server-only or both server and daemon"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "server":
            asyncio.run(run_server_only())
        else:
            asyncio.run(run_both())
    except KeyboardInterrupt:
        logger.info("Services stopped by user")
    except Exception as e:
        logger.error("Error: %s", str(e))
        raise


if __name__ == "__main__":
    main()
