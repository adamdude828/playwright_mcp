from ....utils.logging import setup_logging
from ...tools.handlers.utils import send_to_manager
from mcp.types import TextContent
import json

logger = setup_logging("navigate_handler")


async def handle_navigate(arguments: dict) -> list[TextContent]:
    """Handle the navigate command."""
    try:
        response = await send_to_manager("navigate", arguments)
        
        # Check if analysis was requested and is present in response
        if arguments.get("analyze_after_navigation") and "analysis" in response:
            elements_map = response["analysis"]
            summary = elements_map["summary"]
            interactive = elements_map["interactive_elements"]
            
            # Create a human-readable summary
            text = (
                f"Navigated successfully and analyzed page:\n"
                f"Found {summary['total_anchors']} links, "
                f"{summary['total_buttons']} buttons, and "
                f"{summary['total_form_elements']} form elements.\n\n"
                f"Full element details:\n"
                f"{json.dumps(interactive, indent=2)}"
            )
        else:
            text = "Navigated successfully"

        # Add screenshot info if available
        if "screenshot_path" in response:
            text = f"{text}\nScreenshot saved to: {response['screenshot_path']}"

        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=str(e))] 