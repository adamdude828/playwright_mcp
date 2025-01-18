from typing import Dict, Any, Optional

from ..core.session import SessionManager
from ..core.logging import setup_logging
from .base import BaseHandler
from ..daemon import BrowserDaemon

logger = setup_logging("navigation_handler")


class NavigationHandler(BaseHandler):
    def __init__(self, session_manager: SessionManager):
        super().__init__(session_manager)
        self.required_navigate_args = ["url"]
        self.required_new_tab_args = ["session_id"]

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle navigation commands."""
        command = args.get("command")
        
        if command == "navigate":
            return await self._handle_navigate(args)
        elif command == "new-tab":
            return await self._handle_new_tab(args)
        else:
            return {"error": f"Unknown navigation command: {command}"}

    async def _handle_navigate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle navigate command."""
        if not self._validate_required_args(args, self.required_navigate_args):
            return {"error": "Missing required arguments for navigation"}

        # Get or create session/page if needed
        session_id = args.get("session_id")
        page_id = args.get("page_id")
        created_session = False
        created_page = False

        try:
            # Create new session if needed
            if not session_id or not self.session_manager.get_session(session_id):
                browser_type = args.get("browser_type", "chromium")
                headless = args.get("headless", True)
                session_id = await self.session_manager.launch_browser(browser_type, headless)
                created_session = True

            # Create new page if needed
            if not page_id or not self.session_manager.get_page(page_id):
                page_id = await self.session_manager.new_page(session_id)
                if not page_id:
                    return {"error": "Failed to create new page"}
                created_page = True

            # Get the page and navigate
            page = self.session_manager.get_page(page_id)
            if not page:
                return {"error": f"No page found with ID: {page_id}"}

            await page.goto(args["url"], wait_until=args.get("wait_until", "networkidle"))

            return {
                "session_id": session_id,
                "page_id": page_id,
                "created_session": created_session,
                "created_page": created_page
            }

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"error": str(e)}

    async def _handle_new_tab(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new-tab command."""
        if not self._validate_required_args(args, self.required_new_tab_args):
            return {"error": "Missing required arguments for new tab"}

        try:
            session_id = args["session_id"]
            page_id = await self.session_manager.new_page(session_id)
            
            if not page_id:
                return {"error": "Failed to create new page"}

            # Navigate to URL if provided
            if "url" in args:
                page = self.session_manager.get_page(page_id)
                if not page:
                    return {"error": f"No page found with ID: {page_id}"}

                await page.goto(args["url"], wait_until=args.get("wait_until", "networkidle"))

            return {"page_id": page_id}

        except Exception as e:
            logger.error(f"New tab creation failed: {e}")
            return {"error": str(e)}

    async def handle_navigate(self, args: dict, daemon: Optional[BrowserDaemon] = None) -> dict:
        """Handle navigation command."""
        if not daemon:
            return {
                "error": "Browser daemon is not running. Please call the 'start-daemon' tool first.",
                "isError": True
            }

        # Validate required arguments
        if "url" not in args:
            return {
                "error": "Missing required argument: url",
                "isError": True
            }

        url = args["url"]
        wait_until = args.get("wait_until", "load")

        try:
            # Create new session and page if needed
            session = await daemon.session_manager.create_session()
            page = await session.create_page()

            # Navigate to URL
            await page.goto(url, wait_until=wait_until)

            return {
                "session_id": session.id,
                "page_id": page.id,
                "created_session": True,
                "created_page": True,
                "isError": False
            }

        except Exception as e:
            return {
                "error": f"Failed to navigate: {str(e)}",
                "isError": True
            } 