"""Handler for navigation requests."""

from mcp.types import TextContent, EmbeddedResource, TextResourceContents
from .utils import logger, send_to_manager
import json


async def handle_navigate(arguments: dict) -> list[TextContent | EmbeddedResource]:
    """Handle navigation requests."""
    logger.debug(f"Handling navigation request with arguments: {arguments}")
    
    if "url" not in arguments:
        logger.error("Missing required 'url' argument")
        return [EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri="mcp://navigation",
                text='{"error": "Missing required \'url\' argument"}'
            )
        )]
        
    try:
        response = await send_to_manager("navigate", arguments)
        
        # Return the navigation data as an embedded resource
        return [EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri="mcp://navigation",
                text=json.dumps({
                    "session_id": response["session_id"],
                    "page_id": response["page_id"],
                    "created_session": response["created_session"],
                    "created_page": response["created_page"]
                })
            )
        )]
    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        return [EmbeddedResource(
            type="resource",
            resource=TextResourceContents(
                uri="mcp://navigation",
                text=json.dumps({"error": str(e)})
            )
        )] 