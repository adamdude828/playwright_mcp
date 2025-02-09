"""Server instance module."""
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server.stdio import stdio_server
from ..browser_daemon.tools.definitions import get_tool_definitions
from .handlers import TOOL_HANDLERS
from ..utils.logging import setup_logging
from ..browser_daemon.core.session import session_manager
import asyncio
import logging
import sys
from mcp.types import Tool

# Configure logging
logger = setup_logging("mcp_server")

logger.debug("Server module loaded!")

# Initialize server with shared session manager
server = Server("playwright")

# Debug: Log available tools
tools = get_tool_definitions()
logger.debug(f"Available tools: {[t.name for t in tools]}")
logger.debug(f"Registered handlers: {list(TOOL_HANDLERS.keys())}")
logger.debug(f"Using session manager instance: {id(session_manager)}")

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
        name="get-ai-result",
        description="Get the result of an AI agent job",
        inputSchema={
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "ID of the job to get result for"
                }
            },
            "required": ["job_id"]
        }
    ),
    Tool(
        name="search-dom",
        description=(
            "Search the entire DOM for elements matching the search text in ids, "
            "classes, or attributes using BeautifulSoup"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "Page ID to search in"
                },
                "search_text": {
                    "type": "string",
                    "description": "Text to search for in the DOM"
                }
            },
            "required": ["page_id", "search_text"]
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

    result = await TOOL_HANDLERS[name](arguments or {})
    logger.debug(f"result before return: {result}")
    return result


async def start_server():
    """Start the server with stdio transport."""
    logger.info("Starting MCP server initialization...")  # More explicit about MCP server
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