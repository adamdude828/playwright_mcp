"""Handler for AI agent request."""

from ..utils import send_to_manager, create_response, create_resource_response
from playwright_mcp.utils.logging import setup_logging


logger = setup_logging("ai_agent", "ai_agent.log")


async def handle_ai_agent(args: dict, daemon=None) -> dict:
    """Handle AI agent request."""
    logger.info(f"Handling AI agent request with args: {args}")
    
    # Check required arguments
    if "page_id" not in args:
        logger.error("Missing required argument: page_id")
        return create_response("Missing required argument: page_id")
        
    if "query" not in args:
        logger.error("Missing required argument: query")
        return create_response("Missing required argument: query")

    result = await send_to_manager("ai-agent", args)
    if "error" in result:
        return create_response(result["error"])
        
    # Return job ID and status as a resource
    return create_resource_response({
        "status": result.get("status", "running"),
        "job_id": result["job_id"],
        "message": result.get("message", "Job started")
    }, "ai_agent") 