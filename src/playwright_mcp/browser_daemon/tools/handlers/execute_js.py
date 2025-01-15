from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_execute_js(arguments: dict) -> list:
    """Handle execute-js tool."""
    logger.info(f"Handling execute-js request with args: {arguments}")
    try:
        response = await send_to_manager("execute-js", arguments)

        if "error" in response:
            error_msg = response["error"]
            logger.error(f"JavaScript execution failed: {error_msg}")
            return [
                TextContent(
                    type="text",
                    text=error_msg
                )
            ]

        # Format the result
        result = response.get("result")
        return [
            TextContent(
                type="text",
                text=str(result)
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_execute_js: {e}")
        logger.error(traceback.format_exc())
        return [
            TextContent(
                type="text",
                text=str(e)
            )
        ] 