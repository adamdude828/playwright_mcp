from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_goto(arguments: dict) -> list[TextContent]:
    """Handle goto tool."""
    logger.info(f"Handling goto request with args: {arguments}")
    try:
        response = await send_to_manager("goto", arguments)

        if "error" in response:
            logger.error(f"Navigation failed: {response['error']}")
            raise ValueError(response["error"])

        logger.info("Navigation successful")
        return [
            TextContent(
                type="text",
                text=f"Navigated to {arguments['url']} successfully"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_goto: {e}")
        logger.error(traceback.format_exc())
        raise
