import os
from typing import Dict, Any

from ..core.session import SessionManager
from ..core.logging import setup_logging
from .base import BaseHandler

logger = setup_logging("screenshot_handler")


class ScreenshotHandler(BaseHandler):
    def __init__(self, session_manager: SessionManager):
        super().__init__(session_manager)
        self.required_screenshot_args = ["page_id", "save_path"]
        self.required_highlight_args = ["page_id", "selector"]

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle screenshot-related commands."""
        command = args.get("command")
        
        if command == "screenshot":
            return await self._handle_screenshot(args)
        elif command == "highlight-element":
            return await self._handle_highlight_element(args)
        else:
            return {"error": f"Unknown screenshot command: {command}"}

    async def _handle_screenshot(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle screenshot command."""
        if not self._validate_required_args(args, self.required_screenshot_args):
            return {"error": "Missing required arguments for screenshot"}

        try:
            page_result = await self._get_page(args["page_id"])
            if "error" in page_result:
                return page_result

            page = page_result["page"]
            save_path = args["save_path"]

            # Validate absolute path
            if not os.path.isabs(save_path):
                return {"error": "save_path must be an absolute path"}

            # Ensure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Take the screenshot
            await page.screenshot(path=save_path)
            return {"success": True, "path": save_path}

        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {"error": str(e)}

    async def _handle_highlight_element(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle element highlighting command."""
        if not self._validate_required_args(args, self.required_highlight_args):
            return {"error": "Missing required arguments for highlighting"}

        try:
            page_result = await self._get_page(args["page_id"])
            if "error" in page_result:
                return page_result

            page = page_result["page"]
            selector = args["selector"]
            style = args.get("style", "")

            # Get element metrics
            metrics = await page.evaluate("""(params) => {
                const element = document.querySelector(params.selector);
                if (!element) return null;
                const rect = element.getBoundingClientRect();
                return {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    visible: window.getComputedStyle(element).display !== 'none'
                };
            }""", {"selector": selector})

            if not metrics:
                return {"error": "Element not found"}

            # Apply highlight style
            await page.evaluate("""(params) => {
                const element = document.querySelector(params.selector);
                if (element) {
                    element.style.cssText += params.style;
                }
            }""", {"selector": selector, "style": style})

            return {"metrics": metrics}

        except Exception as e:
            logger.error(f"Element highlighting failed: {e}")
            return {"error": str(e)} 