from typing import Dict, Any

from ..core.session import SessionManager
from ..core.logging import setup_logging
from .base import BaseHandler

logger = setup_logging("interaction_handler")


class InteractionHandler(BaseHandler):
    def __init__(self, session_manager: SessionManager):
        super().__init__(session_manager)
        self.required_interact_args = ["page_id", "selector", "action"]

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DOM interaction commands."""
        command = args.get("command")
        
        if command == "interact-dom":
            return await self._handle_interact_dom(args)
        else:
            return {"error": f"Unknown interaction command: {command}"}

    async def _handle_interact_dom(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DOM interaction command."""
        if not self._validate_required_args(args, self.required_interact_args):
            return {"error": "Missing required arguments for DOM interaction"}

        try:
            # Get the page
            page_result = await self._get_page(args["page_id"])
            if "error" in page_result:
                return page_result

            page = page_result["page"]
            selector = args["selector"]
            action = args["action"]
            value = args.get("value", "")
            options = args.get("options", {})

            # First, ensure the element exists and is visible
            element = await page.query_selector(selector)
            if not element:
                return {"error": f"No element found matching selector: {selector}"}

            # Perform the requested action
            if action == "click":
                click_options = {
                    "button": options.get("button", "left"),
                    "click_count": options.get("clickCount", 1),
                }
                if "position" in options:
                    click_options["position"] = options["position"]
                await element.click(**click_options)

            elif action == "type":
                if not value:
                    return {"error": "Value is required for type action"}
                await element.type(value, delay=options.get("delay", 0))

            elif action == "hover":
                await element.hover()

            elif action == "focus":
                await element.focus()

            elif action == "press":
                if not value:
                    return {"error": "Value (key) is required for press action"}
                await element.press(value)

            elif action == "select":
                if not value:
                    return {"error": "Value is required for select action"}
                await element.select_option(value)

            else:
                return {"error": f"Unknown action: {action}"}

            return {"success": True}

        except Exception as e:
            logger.error(f"DOM interaction failed: {e}")
            return {"error": str(e)} 