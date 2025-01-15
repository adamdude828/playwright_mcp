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
from mcp.types import Tool

# Configure logging
logger = setup_logging("mcp_server")

logger.debug("Server module loaded!")

# Initialize server
server = Server("playwright")

# Debug: Log available tools
tools = get_tool_definitions()
logger.debug(f"Available tools: {[t.name for t in tools]}")
logger.debug(f"Registered handlers: {list(TOOL_HANDLERS.keys())}")

TOOLS = [
    Tool(
        name="start-daemon",
        description="Start the browser daemon if it's not running",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="stop-daemon",
        description="Stop the browser daemon",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="navigate",
        description="Navigate to a URL",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to navigate to"
                },
                "wait_until": {
                    "type": "string",
                    "description": "When to consider navigation complete",
                    "enum": ["load", "domcontentloaded", "networkidle"]
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="close-browser",
        description="Close a browser session",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session ID to close"
                }
            },
            "required": ["session_id"]
        }
    ),
    Tool(
        name="new-tab",
        description="Open a new tab in an existing browser session",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session ID to open tab in"
                }
            },
            "required": ["session_id"]
        }
    ),
    Tool(
        name="close-tab",
        description="Close a tab",
        inputSchema={
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "Page ID to close"
                }
            },
            "required": ["page_id"]
        }
    ),
    Tool(
        name="execute-js",
        description="Execute JavaScript in a page context",
        inputSchema={
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "Page ID to execute in"
                },
                "script": {
                    "type": "string",
                    "description": "JavaScript code to execute"
                }
            },
            "required": ["page_id", "script"]
        }
    ),
    Tool(
        name="screenshot",
        description="Take a screenshot of the current page",
        inputSchema={
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "Page ID to take screenshot of"
                },
                "save_path": {
                    "type": "string",
                    "description": "Path where to save the screenshot"
                }
            },
            "required": ["page_id", "save_path"]
        }
    ),
    Tool(
        name="analyze-page",
        description="Analyze the current page for interactive elements",
        inputSchema={
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "Page ID to analyze"
                }
            },
            "required": ["page_id"]
        }
    ),
    Tool(
        name="explore-dom",
        description="Explore immediate children of a DOM element",
        inputSchema={
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "Page ID to explore"
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector to explore (defaults to body)"
                }
            },
            "required": ["page_id"]
        }
    )
]


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    tools = get_tool_definitions()
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Available tools: {[t.name for t in tools]}")
    return tools


def is_mcp_content(item) -> bool:
    """Check if an item is an MCP content type."""
    return isinstance(item, (types.TextContent, types.ImageContent, types.EmbeddedResource))


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
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    try:
        result = await TOOL_HANDLERS[name](arguments or {})
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Tool call successful - name: {name}, result: {result}")
            
        # If result is already a list of MCP content types, return it directly
        if isinstance(result, list) and all(is_mcp_content(item) for item in result):
            return result
            
        # If it's a string or other type, wrap it in TextContent
        if not isinstance(result, list):
            return [types.TextContent(type="text", text=str(result))]
            
        # Convert list items to TextContent if needed
        return [types.TextContent(type="text", text=str(item)) for item in result]
    except Exception as e:
        logger.error(f"Tool call failed - name: {name}, error: {e}")
        return [types.TextContent(type="text", text=str(e))]


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