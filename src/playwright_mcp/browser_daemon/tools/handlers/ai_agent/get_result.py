"""Handler for getting AI agent job results."""
from mcp.types import TextContent
from ..utils import send_to_manager
import logging
import json

logger = logging.getLogger(__name__)


async def handle_get_ai_result(args: dict, daemon=None) -> dict:
    """Handle get-ai-result request."""
    logger.info(f"Getting AI agent result for args: {args}")
    
    # Check required arguments
    if "job_id" not in args:
        logger.error("Missing required argument: job_id")
        return {
            "isError": True,
            "content": [TextContent(
                type="text",
                text="Missing required argument: job_id"
            )]
        }

    try:
        logger.info(f"Requesting result for job_id: {args['job_id']}")
        result = await send_to_manager("get-ai-result", args)
        logger.info(f"Received result from manager: {result}")
        
        if "error" in result:
            logger.error(f"Failed to get result: {result['error']}")
            return {
                "isError": True,
                "content": [TextContent(
                    type="text",
                    text=result["error"]
                )]
            }
            
        logger.info(f"Successfully retrieved result for job_id: {args['job_id']}")
        return {
            "isError": False,
            "content": [TextContent(
                type="text",
                text=json.dumps({
                    "job_id": result["job_id"],
                    "status": result["status"],
                    "result": result.get("result")
                })
            )]
        }
        
    except Exception as e:
        logger.error(f"Failed to get result with exception: {e}", exc_info=True)
        return {
            "isError": True,
            "content": [TextContent(
                type="text",
                text=f"Failed to get result: {str(e)}"
            )]
        } 