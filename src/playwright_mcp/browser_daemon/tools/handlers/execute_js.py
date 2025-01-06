from mcp.types import TextContent
import traceback
import json
from .utils import send_to_manager, logger


async def handle_execute_js(arguments: dict) -> list[TextContent]:
    """Handle execute-js tool."""
    logger.info(f"Handling execute-js request with args: {arguments}")
    try:
        response = await send_to_manager("execute-js", arguments)

        if "error" in response:
            error_msg = response["error"]
            logger.error(f"JavaScript execution failed: {error_msg}")
            return [TextContent(
                type="text",
                text=f"Error executing JavaScript: {error_msg}"
            )]

        # Format the result nicely
        result = response.get("result")
        if isinstance(result, (dict, list)):
            formatted_result = json.dumps(result, indent=2)
        else:
            formatted_result = str(result)

        logger.info("JavaScript execution successful")
        return [
            TextContent(
                type="text",
                text=f"JavaScript execution result:\n{formatted_result}"
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_execute_js: {e}")
        logger.error(traceback.format_exc())
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )] 