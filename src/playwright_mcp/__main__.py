"""Main entry point for the package."""
import asyncio
from .utils.logging import setup_logging
from .mcp_server.core import main


# Configure logging
logger = setup_logging("playwright_mcp")


def run():
    """Run the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    run()
