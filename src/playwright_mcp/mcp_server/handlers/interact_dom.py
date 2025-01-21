"""Handler for DOM interaction requests."""
from typing import Dict
from .utils import send_to_manager, logger, create_response


async def handle_interact_dom(arguments: Dict) -> list:
    """Handle interact-dom tool."""
    logger.debug(f"Handling interact-dom request with args: {arguments}")
    
    # Get required arguments
    page_id = arguments.get("page_id")
    selector = arguments.get("selector")
    action = arguments.get("action")
    
    if not all([page_id, selector, action]):
        raise Exception("page_id, selector, and action are required")
    
    # Perform the interaction
    response = await send_to_manager("interact-dom", arguments)
    
    if "error" in response:
        raise Exception(f"Error interacting with DOM: {response['error']}")
    
    # Format success message based on the action
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
    
    return create_response(message) 