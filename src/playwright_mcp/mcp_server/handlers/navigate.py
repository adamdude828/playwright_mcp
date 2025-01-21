"""Handler for navigation requests."""

from .utils import logger, send_to_manager, create_resource_response


async def handle_navigate(arguments: dict) -> list:
    """Handle navigation requests."""
    logger.debug(f"Handling navigation request with arguments: {arguments}")
    
    if "url" not in arguments:
        raise Exception("Missing required 'url' argument")
        
    response = await send_to_manager("navigate", arguments)
    logger.debug(f"Got response from send_to_manager: {response}")
    
    if "error" in response:
        logger.error(f"Navigation failed: {response['error']}")
        raise Exception(f"Navigation failed: {response['error']}")

    return create_resource_response({
        "session_id": response["session_id"],
        "page_id": response["page_id"],
        "created_session": response["created_session"],
        "created_page": response["created_page"]
    }, resource_type="navigation") 