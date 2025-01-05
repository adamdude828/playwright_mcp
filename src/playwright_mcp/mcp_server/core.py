"""Core MCP server module."""
import logging
from .server import start_server

# Configure logging
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.ERROR)

# Add console handler if not already added
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    logger.addHandler(console_handler)


async def main():
    """Start the MCP server."""
    logger.info("Starting MCP server")
    try:
        await start_server()
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise 