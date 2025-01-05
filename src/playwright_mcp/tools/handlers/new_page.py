import mcp.types as types
import traceback
from .utils import send_to_manager, logger


async def handle_new_page(arguments: dict) -> list[types.TextContent]:
    """Handle new-page tool."""
    logger.info(f"Handling new-page request with args: {arguments}")
    try:
        response = await send_to_manager("new_page", arguments)
        
        if "error" in response:
            logger.error(f"New page failed: {response['error']}")
            raise ValueError(response["error"])
        
        logger.info(f"New page created successfully: {response}")
        return [
            types.TextContent(
                type="text",
                text=f"New page created with ID: {response['page_id']}"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_new_page: {e}")
        logger.error(traceback.format_exc())
        raise 