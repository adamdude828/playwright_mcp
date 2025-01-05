from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_close_browser(arguments: dict) -> list[TextContent]:
    """Handle close-browser tool."""
    logger.info(f"Handling close-browser request with args: {arguments}")
    try:
        response = await send_to_manager("close", arguments)

        if "error" in response:
            logger.error(f"Close browser failed: {response['error']}")
            raise ValueError(response["error"])

        logger.info("Browser closed successfully")
        return [
            TextContent(
                type="text",
                text=f"Browser session {arguments['session_id']} closed successfully"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_close_browser: {e}")
        logger.error(traceback.format_exc())
        raise
