"""Handler for AI agent requests."""
from ..utils import send_to_manager


async def handle_ai_agent(args: dict, daemon=None) -> dict:
    """Handle AI agent request."""
    # Check required arguments
    if "page_id" not in args:
        return {
            "status": "error",
            "isError": True,
            "error": "Missing required argument: page_id"
        }
    if "query" not in args:
        return {
            "status": "error",
            "isError": True,
            "error": "Missing required argument: query"
        }

    try:
        result = await send_to_manager("ai-agent", args)
        
        if "error" in result:
            return {
                "status": "error",
                "isError": True,
                "error": result["error"]
            }
            
        return {
            "status": "running",
            "job_id": result["job_id"],
            "message": result["message"],
            "isError": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "isError": True,
            "error": f"AI agent request failed: {str(e)}"
        } 