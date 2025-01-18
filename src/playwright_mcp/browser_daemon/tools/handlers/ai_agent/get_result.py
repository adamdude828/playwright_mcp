"""Handler for getting AI agent job results."""
from ..utils import send_to_manager


async def handle_get_ai_result(args: dict, daemon=None) -> dict:
    """Handle get-ai-result request."""
    # Check required arguments
    if "job_id" not in args:
        return {
            "status": "error",
            "isError": True,
            "error": "Missing required argument: job_id"
        }

    try:
        result = await send_to_manager("get-ai-result", args)
        
        if "error" in result:
            return {
                "status": "error",
                "isError": True,
                "error": result["error"]
            }
            
        return {
            "job_id": result["job_id"],
            "status": result["status"],
            "result": result.get("result"),
            "isError": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "isError": True,
            "error": f"Failed to get result: {str(e)}"
        } 