from .utils import send_to_manager, logger, create_resource_response


async def handle_execute_js(arguments: dict) -> list:
    """Handle execute-js tool."""
    logger.debug(f"Handling execute-js request with args: {arguments}")
    
    response = await send_to_manager("execute-js", arguments)
    logger.debug(f"Got response from send_to_manager: {response}")
    
    if "error" in response:
        raise Exception(f"JavaScript execution failed: {response['error']}")

    return create_resource_response({
        "result": str(response.get("result"))
    }, resource_type="js_execution") 