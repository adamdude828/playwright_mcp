from typing import List
from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_new_tab(arguments: dict) -> List[TextContent]:
    """Handle new-tab tool."""
    logger.info(f"Handling new-tab request with args: {arguments}")
    try:
        response = await send_to_manager("new-tab", arguments)

        if "error" in response:
            logger.error(f"New tab creation failed: {response['error']}")
            raise ValueError(response["error"])

        logger.info("New tab created successfully")
        return [
            TextContent(
                type="text",
                text=f"Created new tab with ID: {response['page_id']}"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_new_tab: {e}")
        logger.error(traceback.format_exc())
        raise 