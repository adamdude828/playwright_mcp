"""Tool handlers for the MCP server."""
import logging
import mcp.types as types
from .core import server
from ..browser_daemon.tools.definitions import get_tool_definitions
from ..browser_daemon.tools.handlers import TOOL_HANDLERS

logger = logging.getLogger("mcp_server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    logger.info("Listing available tools")
    tools = get_tool_definitions()
    logger.debug(f"Available tools: {[t.name for t in tools]}")
    return tools


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can control browser automation via Playwright.
    """
    logger.info(f"Tool call received - name: {name}, arguments: {arguments}")

    if not arguments:
        logger.error("Missing arguments")
        raise ValueError("Missing arguments")

    if name not in TOOL_HANDLERS:
        logger.error(f"Unknown tool: {name}")
        raise ValueError(f"Unknown tool: {name}")

    try:
        result = await TOOL_HANDLERS[name](arguments)
        logger.info(f"Tool call successful - name: {name}, result: {result}")
        return result
    except Exception as e:
        logger.error(f"Tool call failed - name: {name}, error: {e}")
        raise
