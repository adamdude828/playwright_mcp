from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_new_page(arguments: dict) -> dict:
    """Handle new-page tool."""
    logger.info(f"Handling new-page request with args: {arguments}")
    try:
        response = await send_to_manager("new-page", arguments)

        if "error" in response:
            logger.error(f"New page creation failed: {response['error']}")
            return {
                "isError": True,
                "content": [
                    TextContent(
                        type="text",
                        text=response["error"]
                    )
                ]
            }

        return {
            "content": [
                TextContent(
                    type="text",
                    text=str(response)
                )
            ]
        }
    except Exception as e:
        logger.error(f"Error in handle_new_page: {e}")
        logger.error(traceback.format_exc())
        return {
            "isError": True,
            "content": [
                TextContent(
                    type="text",
                    text=str(e)
                )
            ]
        }
