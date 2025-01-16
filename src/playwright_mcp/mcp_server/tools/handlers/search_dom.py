from typing import Dict, Any
from playwright_mcp.mcp_server.tools.base import ToolHandler


class SearchDOMHandler(ToolHandler):
    name = "search-dom"
    description = "Search for DOM elements matching specific criteria like text content, tag name, or attributes"

    async def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate the incoming arguments for the search-dom tool."""
        if not isinstance(args, dict):
            return False
        
        # Check required arguments
        if "page_id" not in args or not isinstance(args["page_id"], str):
            return False
            
        # Validate optional arguments if present
        if "text" in args and not isinstance(args["text"], str):
            return False
        if "tag" in args and not isinstance(args["tag"], str):
            return False
        if "class_name" in args and not isinstance(args["class_name"], str):
            return False
        if "id" in args and not isinstance(args["id"], str):
            return False
        if "attribute" in args and not isinstance(args["attribute"], dict):
            return False
            
        return True

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the search-dom tool request."""
        try:
            # Forward request to daemon with same parameter names
            response = await self.send_to_daemon({
                "command": "search-dom",
                "args": args
            })

            # Process daemon response
            if "error" in response:
                return {
                    "status": "error",
                    "error": response["error"]
                }

            return {
                "status": "success",
                "matches": response.get("matches", []),
                "total": response.get("total", 0)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to execute search-dom: {str(e)}"
            } 