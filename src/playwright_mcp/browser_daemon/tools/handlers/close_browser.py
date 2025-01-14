from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_close_browser(arguments: dict) -> dict:
    """Handle close-browser tool."""
    logger.info(f"Handling close-browser request with args: {arguments}")
    try:
        response = await send_to_manager("close-browser", arguments)

        if "error" in response:
            logger.error(f"Browser close failed: {response['error']}")
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
        logger.error(f"Error in handle_close_browser: {e}")
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
