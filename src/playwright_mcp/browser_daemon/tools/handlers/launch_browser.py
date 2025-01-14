from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_launch_browser(arguments: dict) -> dict:
    """Handle launch-browser tool."""
    logger.info(f"Handling launch-browser request with args: {arguments}")
    try:
        response = await send_to_manager("launch-browser", arguments)

        if "error" in response:
            logger.error(f"Browser launch failed: {response['error']}")
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
        logger.error(f"Error in handle_launch_browser: {e}")
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
