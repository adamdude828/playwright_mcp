from mcp.types import TextContent
import traceback
from .utils import send_to_manager, logger
import json


async def handle_analyze_page(arguments: dict) -> list[TextContent]:
    """Handle analyze-page tool."""
    logger.info(f"Handling analyze-page request with args: {arguments}")
    try:
        response = await send_to_manager("analyze_page", arguments)

        if "error" in response:
            logger.error(f"Page analysis failed: {response['error']}")
            raise ValueError(response["error"])

        elements_map = response["elements"]
        summary = elements_map["summary"]
        interactive = elements_map["interactive_elements"]
        
        # Create a human-readable summary
        text = (
            f"Page Analysis Results:\n"
            f"Found {summary['total_anchors']} links, "
            f"{summary['total_buttons']} buttons, and "
            f"{summary['total_form_elements']} form elements.\n\n"
            f"Full element details:\n"
            f"{json.dumps(interactive, indent=2)}"
        )

        logger.info("Page analysis successful")
        return [
            TextContent(
                type="text",
                text=text
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_analyze_page: {e}")
        logger.error(traceback.format_exc())
        raise 