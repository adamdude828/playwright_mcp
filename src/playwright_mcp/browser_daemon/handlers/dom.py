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
        self.required_search_dom_args = ["page_id"]

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
        # Validate page_id (only required parameter)
        page_id = args.get("page_id")
        if not page_id:
            return {"error": "Missing required arguments for DOM search"}

        page = self.session_manager.get_page(page_id)
        if not page:
            return {"error": f"No page found with ID: {page_id}"}

        try:
            # Get page content and parse with BeautifulSoup using lxml parser
            content = await page.content()
            logger.debug(f"Got page content of length: {len(content)}")
            logger.debug(f"Page content preview: {content[:500]}")
            
            try:
                soup = BeautifulSoup(content, 'lxml')
                logger.debug("Successfully parsed with lxml parser")
                logger.debug(f"Found tags: {[tag.name for tag in soup.find_all()][:10]}")
            except Exception as parse_error:
                logger.error(f"Failed to parse with lxml: {parse_error}")
                try:
                    # Fallback to html.parser with explicit encoding
                    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
                    logger.debug("Successfully parsed with html.parser")
                except Exception as html_parse_error:
                    logger.error(f"Failed to parse with html.parser: {html_parse_error}")
                    return {"error": f"Failed to parse HTML content: {html_parse_error}"}

            matches = []
            # Get search criteria
            search_text = args.get("search_text", "").lower()
            search_tag = args.get("search_tag", "").lower()
            search_class = args.get("search_class", "").lower()
            search_id = args.get("search_id", "").lower()
            search_attribute = args.get("search_attribute", {})

            logger.debug(
                f"Searching with criteria - text: {search_text}, tag: {search_tag}, "
                f"class: {search_class}, id: {search_id}, attribute: {search_attribute}"
            )

            try:
                # Helper function to get element path
                def get_element_path(element):
                    try:
                        path = []
                        current = element
                        while current and current.name:
                            siblings = []
                            if current.parent:
                                siblings = [s for s in current.parent.children if s.name == current.name]
                            position = siblings.index(current) + 1 if siblings else 1
                            path.append(f"{current.name}[{position}]")
                            current = current.parent
                        path.reverse()
                        return '/[document][0]/' + '/'.join(path)
                    except Exception as path_error:
                        logger.error(f"Error getting element path: {path_error}")
                        return "unknown_path"

                # If only searching by tag, use direct find_all
                if search_tag and not any([search_text, search_class, search_id, search_attribute]):
                    logger.debug(f"Performing tag-only search for: {search_tag}")
                    elements = soup.find_all(search_tag)
                    logger.debug(f"Found {len(elements)} elements with tag {search_tag}")
                    for element in elements:
                        match_info = {
                            "type": "tag",
                            "tag": element.name,
                            "path": get_element_path(element),
                            "text": element.get_text(strip=True),
                            "attributes": element.attrs
                        }
                        matches.append(match_info)
                    logger.debug(f"Processed {len(matches)} tag matches")
                    return {
                        "matches": matches,
                        "total": len(matches)
                    }

                # Search for elements matching any of the criteria
                for element in soup.find_all():
                    try:
                        logger.debug(f"Found element: {element.name}")
                        
                        # Skip if tag doesn't match when search_tag is specified
                        if search_tag and element.name.lower() != search_tag:
                            continue

                        # Base match info
                        match_info = {
                            "type": None,
                            "tag": element.name,
                            "path": get_element_path(element),
                            "attributes": element.attrs
                        }

                        # If we have a tag match, add it first
                        if search_tag and element.name.lower() == search_tag:
                            tag_match = match_info.copy()
                            tag_match.update({
                                "type": "tag",
                                "text": element.get_text(strip=True)
                            })
                            matches.append(tag_match)

                        # Check ID
                        if search_text and element.get('id', ''):
                            element_id = element.get('id', '').lower()
                            if search_text in element_id:
                                match_info.update({
                                    "type": "id",
                                    "id": element.get('id'),
                                    "text": element.get_text(strip=True)
                                })
                                matches.append(match_info.copy())

                        # Check classes
                        if search_text and element.get('class'):
                            element_classes = element.get('class', [])
                            if any(search_text in c.lower() for c in element_classes):
                                match_info.update({
                                    "type": "class",
                                    "classes": element_classes,
                                    "text": element.get_text(strip=True)
                                })
                                matches.append(match_info.copy())

                        # Check other attributes
                        if search_text:
                            logger.debug(f"Checking attributes for element {element.name}")
                            for attr, value in element.attrs.items():
                                if attr not in ['id', 'class']:
                                    attr_value = str(value).lower()
                                    if search_text in attr or search_text in attr_value:
                                        logger.debug(f"Found attribute match: {attr}={value}")
                                        match_info.update({
                                            "type": "attribute",
                                            "attribute": attr,
                                            "value": value,
                                            "text": element.get_text(strip=True)
                                        })
                                        matches.append(match_info.copy())

                        # Check text content
                        if search_text:
                            element_text = element.get_text(strip=True).lower()
                            if search_text in element_text:
                                match_info.update({
                                    "type": "text",
                                    "text": element_text
                                })
                                matches.append(match_info.copy())

                    except Exception as element_error:
                        logger.error(f"Error processing element: {element_error}")
                        continue

                logger.debug(f"Found {len(matches)} matches")
                return {
                    "matches": matches,
                    "total": len(matches)
                }

            except Exception as search_error:
                logger.error(f"Error during DOM search: {search_error}")
                return {"error": f"Error during DOM search: {search_error}"}

        except Exception as e:
            logger.error(f"Error in _handle_search_dom: {e}")
            return {"error": str(e)} 