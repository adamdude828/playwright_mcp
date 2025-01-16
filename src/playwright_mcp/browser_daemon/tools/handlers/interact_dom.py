from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger


async def handle_interact_dom(arguments: dict) -> dict:
    """Handle interact-dom tool."""
    logger.info(f"Handling interact-dom request with args: {arguments}")
    try:
        response = await send_to_manager("interact-dom", arguments)

        if "error" in response:
            logger.error(f"DOM interaction failed: {response['error']}")
            return {
                "isError": True,
                "content": [
                    TextContent(
                        type="text",
                        text=response["error"]
                    )
                ]
            }

        # Format success message based on the action
        action = arguments.get("action", "unknown")
        selector = arguments.get("selector", "unknown")
        
        if action == "type":
            message = f"Successfully typed text into element matching '{selector}'"
        elif action == "click":
            message = f"Successfully clicked element matching '{selector}'"
        elif action == "hover":
            message = f"Successfully hovered over element matching '{selector}'"
        elif action == "focus":
            message = f"Successfully focused element matching '{selector}'"
        elif action == "press":
            key = arguments.get("value", "")
            message = f"Successfully pressed key '{key}' on element matching '{selector}'"
        elif action == "select":
            message = f"Successfully selected option in element matching '{selector}'"
        else:
            message = f"Successfully performed {action} on element matching '{selector}'"

        return {
            "content": [
                TextContent(
                    type="text",
                    text=message
                )
            ]
        }

    except Exception as e:
        logger.error(f"Error in handle_interact_dom: {e}")
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