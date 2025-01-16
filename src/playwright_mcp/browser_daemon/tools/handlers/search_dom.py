from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_search_dom(arguments: dict) -> dict:
    """Handle search-dom tool."""
    logger.info(f"Handling search-dom request with args: {arguments}")
    try:
        response = await send_to_manager("search-dom", arguments)

        if "error" in response:
            logger.error(f"DOM search failed: {response['error']}")
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
        logger.error(f"Error in handle_search_dom: {e}")
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