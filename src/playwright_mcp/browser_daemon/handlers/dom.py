from typing import Dict, Any

from ..core.session import SessionManager
from ..core.logging import setup_logging
from .base import BaseHandler

logger = setup_logging("dom_handler")


class DOMHandler(BaseHandler):
    def __init__(self, session_manager: SessionManager):
        super().__init__(session_manager)
        self.required_execute_js_args = ["session_id", "page_id", "script"]
        self.required_explore_dom_args = ["page_id"]

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DOM-related commands."""
        command = args.get("command")
        
        if command == "execute-js":
            return await self._handle_execute_js(args)
        elif command == "explore-dom":
            return await self._handle_explore_dom(args)
        else:
            return {"error": f"Unknown DOM command: {command}"}

    async def _handle_execute_js(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JavaScript execution command."""
        if not self._validate_required_args(args, self.required_execute_js_args):
            return {"error": "Missing required arguments for JavaScript execution"}

        try:
            # Validate session first
            session_id = args["session_id"]
            if session_id not in self.session_manager.sessions:
                return {"error": f"No browser session found for ID: {session_id}"}

            # Then get the page
            page_result = await self._get_page(args["page_id"])
            if "error" in page_result:
                return page_result

            page = page_result["page"]
            result = await page.evaluate(args["script"])
            return {"result": result}

        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            return {"error": str(e)}

    async def _handle_explore_dom(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DOM exploration command."""
        if not self._validate_required_args(args, self.required_explore_dom_args):
            return {"error": "Missing required arguments for DOM exploration"}

        try:
            page_result = await self._get_page(args["page_id"])
            if "error" in page_result:
                return page_result

            page = page_result["page"]
            selector = args.get("selector", "body")

            # Import here to avoid circular imports
            from ..tools.dom_explorer import explore_dom
            return await explore_dom(page, selector)

        except Exception as e:
            logger.error(f"DOM exploration failed: {e}")
            return {"error": str(e)} 