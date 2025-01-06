"""Core MCP server module."""
from ..utils.logging import setup_logging
from .server import start_server

# Configure logging
logger = setup_logging("mcp_server")


async def main():
    """Start the MCP server."""
    logger.info("Starting MCP server")
    try:
        await start_server()
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise 