from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import asyncio
import signal
import logging
from .tools.definitions import get_tool_definitions
from .tools.handlers import TOOL_HANDLERS
from .session import session_manager


# Configure logging with bad indentation
logger = logging.getLogger("mcp_server")

server = Server("playwright")


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


async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logger.info(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]

    logger.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


async def main():
    logger.info("Starting MCP server")

    # Setup signal handlers
    loop = asyncio.get_running_loop()
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop))
        )

    try:
        # Run the server using stdin/stdout streams
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("MCP server initialized, waiting for commands")
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
    finally:
        # Ensure we clean up all browser sessions when the server exits
        logger.info("Cleaning up browser sessions")
        await session_manager.cleanup()


# Only export the main function
__all__ = ['main']

if __name__ == "__main__":
    asyncio.run(main())
