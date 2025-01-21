"""Handler for closing browser tabs."""
from typing import Dict
from .utils import send_to_manager, logger, create_response


async def handle_close_tab(arguments: Dict) -> list:
    """Handle close-tab tool."""
    logger.debug(f"Handling close-tab request with args: {arguments}")
    
    # Get required arguments
    session_id = arguments.get("session_id")
    page_id = arguments.get("page_id")
    
    if not all([session_id, page_id]):
        raise Exception("session_id and page_id are required")
    
    # Close the tab
    response = await send_to_manager("close-tab", {
        "session_id": session_id,
        "page_id": page_id
    })
    
    if "error" in response:
        raise Exception(f"Error closing tab: {response['error']}")
    
    return create_response("Tab closed successfully") 