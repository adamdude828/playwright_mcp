"""Core server functionality."""
import logging
import logging.handlers
import os

from mcp.server import Server


def setup_logging():
    """Set up logging configuration."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "mcp_server.log")

    # Configure logging
    logger = logging.getLogger("mcp_server")
    logger.setLevel(logging.DEBUG)

    # File handler with rotation
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logging()
server = Server("playwright")


async def main():
    """Start and run the MCP server."""
    logger.info("Starting MCP server")
    await server.initialize()
    logger.info("MCP server initialized, waiting for commands")
    await server.run() 