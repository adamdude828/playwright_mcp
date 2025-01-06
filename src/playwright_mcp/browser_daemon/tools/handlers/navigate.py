from ....utils.logging import setup_logging
from ...tools.handlers.utils import send_to_manager

logger = setup_logging("navigate_handler")


async def handle_navigate(arguments: dict) -> list:
    """Handle the navigate command."""
    try:
        await send_to_manager("navigate", arguments)
        return [{"type": "text", "text": "Navigated successfully"}]
    except Exception as e:
        return [{"type": "text", "text": str(e)}] 