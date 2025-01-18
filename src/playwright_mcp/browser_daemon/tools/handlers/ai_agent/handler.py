"""Handler for AI agent requests."""
from ..utils import send_to_manager
import logging

logger = logging.getLogger(__name__)


async def handle_ai_agent(args: dict, daemon=None) -> dict:
    """Handle AI agent request."""
    logger.info(f"Handling AI agent request with args: {args}")
    
    # Check required arguments
    if "page_id" not in args:
        logger.error("Missing required argument: page_id")
        return {
            "status": "error",
            "isError": True,
            "error": "Missing required argument: page_id"
        }
    if "query" not in args:
        logger.error("Missing required argument: query")
        return {
            "status": "error",
            "isError": True,
            "error": "Missing required argument: query"
        }

    try:
        logger.info("Sending AI agent request to manager")
        result = await send_to_manager("ai-agent", args)
        logger.info(f"Received result from manager: {result}")
        
        if "error" in result:
            logger.error(f"AI agent request failed: {result['error']}")
            return {
                "status": "error",
                "isError": True,
                "error": result["error"]
            }
            
        logger.info(f"AI agent job started successfully with job_id: {result.get('job_id')}")
        return {
            "status": "running",
            "job_id": result["job_id"],
            "message": result["message"],
            "isError": False
        }
        
    except Exception as e:
        logger.error(f"AI agent request failed with exception: {e}", exc_info=True)
        return {
            "status": "error",
            "isError": True,
            "error": f"AI agent request failed: {str(e)}"
        } 