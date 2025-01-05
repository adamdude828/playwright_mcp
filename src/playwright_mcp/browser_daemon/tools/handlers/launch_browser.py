from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_launch_browser(arguments: dict) -> list[TextContent]:
    """Handle launch-browser tool."""
    logger.info(f"Handling launch-browser request with args: {arguments}")
    try:
        response = await send_to_manager("launch", arguments)

        if "error" in response:
            logger.error(f"Launch browser failed: {response['error']}")
            raise ValueError(response["error"])

        logger.info(f"Browser launched successfully: {response}")
        return [
            TextContent(
                type="text",
                text=f"Browser launched with session ID: {response['session_id']}"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_launch_browser: {e}")
        logger.error(traceback.format_exc())
        raise
