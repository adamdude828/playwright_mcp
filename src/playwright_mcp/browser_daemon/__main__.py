"""Main entry point for the browser daemon."""
import asyncio
from playwright_mcp.utils.logging import setup_logging
from .browser_manager import BrowserManager


# Configure logging
logger = setup_logging("browser_daemon")


async def main():
    """Start and run the browser manager."""
    logger.info("Starting browser manager")
    manager = BrowserManager()
    await manager.start_server()
    logger.info("Browser manager started")


def run():
    """Run the browser manager."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down browser manager...")


if __name__ == "__main__":
    run() 