import traceback
from .utils import send_to_manager, logger, create_response


async def handle_analyze_page(arguments: dict) -> dict:
    """Handle analyze-page tool."""
    logger.info(f"Handling analyze-page request with args: {arguments}")
    try:
        response = await send_to_manager("analyze-page", arguments)

        if "error" in response:
            logger.error(f"Page analysis failed: {response['error']}")
            return create_response(f"Analysis failed: {response['error']}", is_error=True)

        elements = response["elements"]
        summary = elements["summary"]
        interactive = elements["interactive_elements"]

        # Create a human-readable summary
        message = (
            f"Page Analysis Results:\n"
            f"{summary['total_anchors']} links found\n"
            f"{summary['total_buttons']} buttons found\n"
            f"{summary['total_form_elements']} form elements found\n\n"
            f"Interactive Elements:\n"
        )

        # Add details about each type of interactive element
        for element_type, elements_list in interactive.items():
            message += f"\n{element_type.upper()}:\n"
            for element in elements_list:
                message += f"- {element.get('text', 'No text')} ({element['selector']})\n"

        return create_response(message)
    except Exception as e:
        logger.error(f"Error in handle_analyze_page: {e}")
        logger.error(traceback.format_exc())
        return create_response(f"Analysis error: {e}", is_error=True) 