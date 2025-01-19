"""Handler for AI agent request."""

import json
from ..utils import send_to_manager, create_response, logger


async def handle_ai_agent(args: dict, daemon=None) -> dict:
    """Handle AI agent request."""
    logger.info(f"Handling AI agent request with args: {args}")
    
    # Check required arguments
    if "page_id" not in args:
        logger.error("Missing required argument: page_id")
        return create_response("Missing required argument: page_id", is_error=True)
        
    if "query" not in args:
        logger.error("Missing required argument: query")
        return create_response("Missing required argument: query", is_error=True)

    try:
        result = await send_to_manager("ai-agent", args)
        if "error" in result:
            return create_response(result["error"], is_error=True)
            
        return create_response(json.dumps({
            "status": "running",
            "job_id": result["job_id"],
            "message": result["message"]
        }))
        
    except Exception as e:
        logger.error(f"AI agent request failed with exception: {e}", exc_info=True)
        return create_response(f"AI agent request failed: {str(e)}", is_error=True) 