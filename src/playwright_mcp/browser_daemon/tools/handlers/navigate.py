"""Handler for navigation requests."""

from .utils import send_to_manager


async def handle_navigate(args: dict, daemon=None) -> dict:
    """Handle navigate request."""
    # Check required arguments
    if "url" not in args:
        return {
            "status": "error",
            "isError": True,
            "error": "Missing required argument: url"
        }

    try:
        result = await send_to_manager("navigate", args)
        
        if "error" in result:
            return {
                "status": "error",
                "isError": True,
                "error": result["error"]
            }
            
        return {
            "session_id": result["session_id"],
            "page_id": result["page_id"],
            "created_session": result.get("created_session", True),
            "created_page": result.get("created_page", True),
            "isError": False
        }
        
    except Exception as e:
        error_msg = str(e)
        return {
            "status": "error",
            "isError": True,
            "error": error_msg
        } 