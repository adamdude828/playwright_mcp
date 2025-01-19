"""Main entry point for the browser daemon."""
import asyncio
from playwright_mcp.utils.logging import setup_logging
from .browser_manager import BrowserManager


# Configure logging
logger = setup_logging("browser_daemon")


async def main():
    """Start and run the browser manager."""
    logger.info("Starting server initialization")
    try:
        manager = BrowserManager()
        logger.info("Starting browser manager service")
        await manager.start()
        logger.info("Browser manager started successfully")
        await asyncio.Event().wait()  # Keep the daemon running
    except Exception as e:
        logger.error(f"Failed to start browser manager: {e}", exc_info=True)
        raise


def run():
    """Run the browser manager."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down browser manager...")
    except Exception as e:
        logger.error(f"Unhandled exception in browser manager: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run() 