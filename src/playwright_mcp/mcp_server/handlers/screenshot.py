"""Handler for screenshot requests."""
from typing import Dict
from .utils import send_to_manager, logger, create_response


async def handle_screenshot(arguments: Dict) -> list:
    """Handle screenshot tool."""
    logger.debug(f"Handling screenshot request with args: {arguments}")
    
    # Get required arguments
    page_id = arguments.get("page_id")
    path = arguments.get("path")
    
    if not all([page_id, path]):
        raise Exception("page_id and path are required")
    
    # Take screenshot
    response = await send_to_manager("screenshot", {
        "page_id": page_id,
        "save_path": path,
        "full_page": arguments.get("full_page", False)
    })
    
    if "error" in response:
        raise Exception(f"Error taking screenshot: {response['error']}")
    
    return create_response(f"Screenshot saved to: {path}") 