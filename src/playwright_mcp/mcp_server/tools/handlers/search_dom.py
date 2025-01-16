from typing import Dict, Any
from playwright_mcp.mcp_server.tools.base import ToolHandler


class SearchDOMHandler(ToolHandler):
    name = "search-dom"
    description = "Search the DOM for elements matching specific criteria including tags, IDs, classes, and attributes"

    async def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate the incoming arguments for the search-dom tool."""
        if not isinstance(args, dict):
            return False
        
        # Check required arguments
        if "query" not in args or not isinstance(args["query"], str):
            return False
        if "page_id" not in args or not isinstance(args["page_id"], str):
            return False
            
        # Validate optional arguments if present
        if "visible_only" in args and not isinstance(args["visible_only"], bool):
            return False
        if "max_results" in args and not isinstance(args["max_results"], int):
            return False
        if "include_html" in args and not isinstance(args["include_html"], bool):
            return False
            
        return True

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the search-dom tool request."""
        try:
            # Extract and process arguments
            query = args["query"]
            page_id = args["page_id"]
            visible_only = args.get("visible_only", True)
            max_results = args.get("max_results", 100)
            include_html = args.get("include_html", False)

            # Forward request to daemon
            response = await self.send_to_daemon({
                "command": "handle-search-dom",
                "args": {
                    "query": query,
                    "page_id": page_id,
                    "visible_only": visible_only,
                    "max_results": max_results,
                    "include_html": include_html
                }
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
                "total_matches": response.get("total_matches", 0)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to execute search-dom: {str(e)}"
            } 