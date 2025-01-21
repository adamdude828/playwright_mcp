"""Handler for highlight element requests."""
from typing import Dict
from .utils import send_to_manager, logger, create_response


async def handle_highlight_element(arguments: Dict) -> list:
    """Handle highlight-element command by highlighting an element."""
    logger.debug(f"Handling highlight-element request with args: {arguments}")
    
    # Get required arguments
    page_id = arguments.get("page_id")
    selector = arguments.get("selector")
    
    if not all([page_id, selector]):
        raise Exception("page_id and selector are required")
    
    # Add highlight to element
    response = await send_to_manager("highlight-element", {
        "page_id": page_id,
        "selector": selector,
        "style": """
            outline: 3px solid #FF4444 !important;
            box-shadow: 0 0 10px #FF4444 !important;
            transition: all 0.3s ease-in-out !important;
        """
    })
    
    if "error" in response:
        raise Exception(f"Error highlighting element: {response['error']}")
    
    # Get element dimensions and position
    metrics = response.get("metrics", {})
    
    return create_response(f"""Element highlighted:
- Selector: {selector}
- Position: (x: {metrics.get('x', 'N/A')}, y: {metrics.get('y', 'N/A')})
- Dimensions: {metrics.get('width', 'N/A')}x{metrics.get('height', 'N/A')}px
- Visible: {metrics.get('visible', 'Unknown')}""") 