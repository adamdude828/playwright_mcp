from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_screenshot(arguments: dict) -> dict:
    """Handle screenshot tool."""
    logger.info(f"Handling screenshot request with args: {arguments}")
    try:
        response = await send_to_manager("screenshot", arguments)

        if "error" in response:
            logger.error(f"Screenshot failed: {response['error']}")
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
        logger.error(f"Error in handle_screenshot: {e}")
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