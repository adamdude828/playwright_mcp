from typing import Dict, Any

from ..core.session import SessionManager
from ..core.logging import setup_logging
from .base import BaseHandler
from bs4 import BeautifulSoup
import re

logger = setup_logging("dom_handler")


class DOMHandler(BaseHandler):
    def __init__(self, session_manager: SessionManager):
        super().__init__(session_manager)
        self.required_execute_js_args = ["session_id", "page_id", "script"]
        self.required_explore_dom_args = ["page_id"]
        self.required_search_dom_args = ["page_id", "search_text"]

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DOM-related commands."""
        command = args.get("command")
        
        if command == "execute-js":
            return await self._handle_execute_js(args)
        elif command == "explore-dom":
            return await self._handle_explore_dom(args)
        elif command == "search-dom":
            return await self._handle_search_dom(args)
        else:
            return {"error": f"Unknown DOM command: {command}"}

    async def _handle_execute_js(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JavaScript execution command."""
        if not self._validate_required_args(args, self.required_execute_js_args):
            return {"error": "Missing required arguments for JavaScript execution"}

        try:
            # Validate session first
            session_id = args["session_id"]
            if not self.session_manager.get_session(session_id):
                return {"error": f"No browser session found for ID: {session_id}"}

            # Then get the page
            page = self.session_manager.get_page(args["page_id"])
            if not page:
                return {"error": f"No page found with ID: {args['page_id']}"}

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
            page = self.session_manager.get_page(args["page_id"])
            if not page:
                return {"error": f"No page found with ID: {args['page_id']}"}

            selector = args.get("selector", "body")

            # Import here to avoid circular imports
            from ..tools.dom_explorer import explore_dom
            return await explore_dom(page, selector)

        except Exception as e:
            logger.error(f"DOM exploration failed: {e}")
            return {"error": str(e)}

    async def _handle_search_dom(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DOM search command."""
        if not self._validate_required_args(args, self.required_search_dom_args):
            return {"error": "Missing required arguments for DOM search"}

        try:
            page = self.session_manager.get_page(args["page_id"])
            if not page:
                return {"error": f"No page found with ID: {args['page_id']}"}

            # Get full page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            search_text = args["search_text"]
            
            matches = []
            
            # Search by ID
            for elem in soup.find_all(id=re.compile(search_text, re.IGNORECASE)):
                matches.append({
                    "type": "id",
                    "tag": elem.name,
                    "id": elem.get('id'),
                    "classes": elem.get('class', []),
                    "text": elem.text[:100] if elem.text else "",
                    "html": str(elem)[:200]
                })
                
            # Search by class
            for elem in soup.find_all(class_=re.compile(search_text, re.IGNORECASE)):
                matches.append({
                    "type": "class",
                    "tag": elem.name,
                    "id": elem.get('id'),
                    "classes": elem.get('class', []),
                    "text": elem.text[:100] if elem.text else "",
                    "html": str(elem)[:200]
                })
                
            # Search other attributes
            for elem in soup.find_all():
                for attr, value in elem.attrs.items():
                    if attr not in ['id', 'class']:
                        if isinstance(value, str) and re.search(search_text, value, re.IGNORECASE):
                            matches.append({
                                "type": "attribute",
                                "attribute": attr,
                                "tag": elem.name,
                                "id": elem.get('id'),
                                "classes": elem.get('class', []),
                                "text": elem.text[:100] if elem.text else "",
                                "html": str(elem)[:200]
                            })
            
            return {
                "matches": matches,
                "total": len(matches)
            }

        except Exception as e:
            logger.error(f"DOM search failed: {e}")
            return {"error": str(e)} 