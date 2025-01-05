from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_close_page(arguments: dict) -> list[TextContent]:
    """Handle close-page tool."""
    logger.info(f"Handling close-page request with args: {arguments}")
    try:
        response = await send_to_manager("close_page", arguments)

        if "error" in response:
            logger.error(f"Close page failed: {response['error']}")
            raise ValueError(response["error"])

        logger.info("Page closed successfully")
        return [
            TextContent(
                type="text",
                text=f"Page {arguments['page_id']} closed successfully"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_close_page: {e}")
        logger.error(traceback.format_exc())
        raise
