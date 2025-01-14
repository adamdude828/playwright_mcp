from typing import Dict, List
from mcp.types import TextContent
from .utils import create_response, send_to_manager


async def handle_navigate(arguments: Dict) -> List[TextContent]:
    """Handle navigate command by navigating to a URL in a new or existing session."""
    try:
        # Send navigate command to browser manager
        result = await send_to_manager("navigate", arguments)
        
        # Format response with expected field names
        response_data = {
            "session_id": result["session_id"],
            "page_id": result["page_id"],
            "created_session": result["created_session"],
            "created_page": result["created_page"]
        }
        
        return [TextContent(type="text", text=str(response_data))]
        
    except Exception as e:
        return [TextContent(type="text", text=str(e))] 