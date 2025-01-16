from typing import Dict, Any

from ..core.session import SessionManager
from ..core.logging import setup_logging
from .base import BaseHandler
from bs4 import BeautifulSoup

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
        """Handle search-dom command."""
        # Validate required arguments
        if not args or "search_text" not in args:
            return {"error": "Missing required arguments: search_text"}

        page_id = args.get("page_id")
        if not page_id:
            return {"error": "Missing required arguments: page_id"}

        page = self.session_manager.get_page(page_id)
        if not page:
            return {"error": f"No page found with ID: {page_id}"}

        try:
            # Get page content and parse with BeautifulSoup
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            matches = []
            search_text = args["search_text"].lower()

            # Helper function to get element path
            def get_element_path(element):
                path = []
                current = element
                while current and current.name:
                    siblings = [s for s in current.parent.children if s.name == current.name] if current.parent else []
                    position = siblings.index(current) + 1 if siblings else 1
                    path.append(f"{current.name}[{position}]")
                    current = current.parent
                path.reverse()
                return '/[document][0]/' + '/'.join(path)

            # Helper function to check if element has matching text
            def has_matching_text(element):
                return bool(element.string and search_text in element.string.lower())

            # Search for elements with matching ID
            for element in soup.find_all():
                if element.get('id') and search_text in element.get('id').lower():
                    matches.append({
                        "type": "id",
                        "tag": element.name,
                        "id": element.get("id"),
                        "path": get_element_path(element)
                    })

            # Search for elements with matching class
            for element in soup.find_all(class_=True):
                if any(search_text in c.lower() for c in element.get('class', [])):
                    matches.append({
                        "type": "class",
                        "tag": element.name,
                        "classes": element.get("class"),
                        "path": get_element_path(element)
                    })

            # Search for elements with matching attributes
            for element in soup.find_all():
                for attr, value in element.attrs.items():
                    if attr not in ["id", "class"]:  # Skip id and class as they're handled separately
                        # Handle both string values and lists of strings
                        if isinstance(value, str):
                            # Check both attribute name and value
                            if search_text in attr.lower() or search_text in value.lower():
                                matches.append({
                                    "type": "attribute",
                                    "tag": element.name,
                                    "attribute": attr,
                                    "value": value,
                                    "path": get_element_path(element)
                                })
                        elif isinstance(value, list):
                            # Handle list of values (like multiple data attributes)
                            for v in value:
                                if isinstance(v, str) and (search_text in attr.lower() or search_text in v.lower()):
                                    matches.append({
                                        "type": "attribute",
                                        "tag": element.name,
                                        "attribute": attr,
                                        "value": v,
                                        "path": get_element_path(element)
                                    })

            # Search for elements with matching text content
            for element in soup.find_all(string=True):
                if element.strip() and search_text in element.lower():
                    matches.append({
                        "type": "text",
                        "tag": element.parent.name,
                        "text": str(element).strip(),
                        "path": get_element_path(element.parent)
                    })

            return {
                "matches": matches,
                "total": len(matches)
            }

        except Exception as e:
            return {"error": str(e)} 