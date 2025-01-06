from typing import List
from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_close_tab(arguments: dict) -> List[TextContent]:
    """Handle close-tab tool."""
    logger.info(f"Handling close-tab request with args: {arguments}")
    try:
        response = await send_to_manager("close-tab", arguments)

        if "error" in response:
            logger.error(f"Close tab failed: {response['error']}")
            raise ValueError(response["error"])

        logger.info("Tab closed successfully")
        return [
            TextContent(
                type="text",
                text=f"Tab {arguments['page_id']} closed successfully"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_close_tab: {e}")
        logger.error(traceback.format_exc())
        raise 