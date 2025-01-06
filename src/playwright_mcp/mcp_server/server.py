"""Server instance module."""
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server.stdio import stdio_server
from ..browser_daemon.tools.definitions import get_tool_definitions
from ..browser_daemon.tools.handlers import TOOL_HANDLERS
from ..utils.logging import setup_logging
import asyncio
import logging
import sys

# Configure logging
logger = setup_logging("mcp_server")

print("Server module loaded!", file=sys.stderr)  # Immediate feedback

# Initialize server
server = Server("playwright")

# Debug: Print available tools
tools = get_tool_definitions()
print(f"Available tools: {[t.name for t in tools]}", file=sys.stderr)
print(f"Registered handlers: {list(TOOL_HANDLERS.keys())}", file=sys.stderr)


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    tools = get_tool_definitions()
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Available tools: {[t.name for t in tools]}")
    return tools


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Tool call received - name: {name}, arguments: {arguments}")

    if name not in TOOL_HANDLERS:
        logger.error(f"Unknown tool: {name}")
        raise ValueError(f"Unknown tool: {name}")

    try:
        result = await TOOL_HANDLERS[name](arguments or {})
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Tool call successful - name: {name}")
        return result
    except Exception as e:
        logger.error(f"Tool call failed - name: {name}, error: {e}")
        raise


async def start_server():
    """Start the server with stdio transport."""
    logger.info("Starting server initialization...")  # Early logging
    try:
        # Run the server using stdin/stdout streams
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP server initialized")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="playwright",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except asyncio.CancelledError:
        logger.info("Server shutdown initiated")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    print("Running server directly!", file=sys.stderr)  # Immediate feedback
    asyncio.run(start_server()) 