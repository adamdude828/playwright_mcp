from typing import Dict, Any

from ..core.session import SessionManager
from ..core.logging import setup_logging
from .base import BaseHandler

logger = setup_logging("session_handler")


class SessionHandler(BaseHandler):
    def __init__(self, session_manager: SessionManager):
        super().__init__(session_manager)
        self.required_close_browser_args = ["session_id"]
        self.required_close_tab_args = ["page_id"]

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session-related commands."""
        command = args.get("command")
        
        if command == "close-browser":
            return await self._handle_close_browser(args)
        elif command == "close-tab":
            return await self._handle_close_tab(args)
        else:
            return {"error": f"Unknown session command: {command}"}

    async def _handle_close_browser(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle close-browser command."""
        if not self._validate_required_args(args, self.required_close_browser_args):
            return {"error": "Missing required arguments for closing browser"}

        try:
            session_id = args["session_id"]
            success = await self.session_manager.close_browser(session_id)
            return {"success": success}

        except Exception as e:
            logger.error(f"Browser close failed: {e}")
            return {"error": str(e)}

    async def _handle_close_tab(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle close-tab command."""
        if not self._validate_required_args(args, self.required_close_tab_args):
            return {"error": "Missing required arguments for closing tab"}

        try:
            page_id = args["page_id"]
            success = await self.session_manager.close_page(page_id)
            return {"success": success}

        except Exception as e:
            logger.error(f"Tab close failed: {e}")
            return {"error": str(e)} 