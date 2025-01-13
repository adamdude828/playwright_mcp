from ....utils.logging import setup_logging
from ...tools.handlers.utils import send_to_manager
from mcp.types import TextContent
import json

logger = setup_logging("navigate_handler")


async def handle_navigate(arguments: dict) -> list[TextContent]:
    """Handle the navigate command."""
    try:
        response = await send_to_manager("navigate", arguments)
        
        # Build response data with all fields from the manager's response
        response_data = {
            "session_id": response["session_id"],
            "page_id": response["page_id"],
            "created_session": response["created_session"],
            "created_page": response["created_page"]
        }
        
        # Include analysis results if present
        if "analysis" in response:
            response_data["analysis"] = response["analysis"]
        
        # Include screenshot path if present
        if "screenshot_path" in response:
            response_data["screenshot_path"] = response["screenshot_path"]
        
        return [TextContent(type="text", text=json.dumps(response_data))]
    except Exception as e:
        # Return error message directly without JSON wrapping
        return [TextContent(type="text", text=str(e))] 