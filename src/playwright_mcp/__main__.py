"""Main entry point for the package."""
import asyncio
import logging
from .server import main


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def run():
    """Run the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    run()
