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
            "isError": True,
            "status": "error",
            "error": "Missing required argument: page_id"
        }
    if "query" not in args:
        logger.error("Missing required argument: query")
        return {
            "isError": True,
            "status": "error",
            "error": "Missing required argument: query"
        }

    try:
        result = await send_to_manager("ai-agent", args)
        if "error" in result:
            return {
                "isError": True,
                "status": "error",
                "error": result["error"]
            }
        return {
            "isError": False,
            "status": "running",
            **result
        }
    except Exception as e:
        logger.error(f"AI agent request failed with exception: {e}", exc_info=True)
        return {
            "isError": True,
            "status": "error",
            "error": f"AI agent request failed: {str(e)}"
        } 