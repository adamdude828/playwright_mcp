from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_new_page(arguments: dict) -> list[TextContent]:
    """Handle new-page tool."""
    logger.info(f"Handling new-page request with args: {arguments}")
    try:
        response = await send_to_manager("new_page", arguments)

        if "error" in response:
            logger.error(f"New page creation failed: {response['error']}")
            raise ValueError(response["error"])

        logger.info("New page created successfully")
        return [
            TextContent(
                type="text",
                text=f"Created new page with ID: {response['page_id']}"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_new_page: {e}")
        logger.error(traceback.format_exc())
        raise
