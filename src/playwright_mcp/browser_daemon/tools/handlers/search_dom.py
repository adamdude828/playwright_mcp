from typing import Dict, Any
from .utils import send_to_manager


async def handle_search_dom(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle DOM search requests in the browser context."""
    try:
        # Extract arguments
        page_id = arguments.get("page_id")
        if not page_id:
            return {"error": "No page_id provided"}

        query = arguments.get("query")
        if not query:
            return {"error": "No query provided"}

        visible_only = arguments.get("visible_only", True)
        max_results = arguments.get("max_results", 100)
        include_html = arguments.get("include_html", False)

        # Forward to page manager
        response = await send_to_manager("handle-search-dom", {
            "page_id": page_id,
            "query": query,
            "visible_only": visible_only,
            "max_results": max_results,
            "include_html": include_html
        })

        if "error" in response:
            return {"error": response["error"]}

        return response

    except Exception as e:
        return {"error": f"Failed to search DOM: {str(e)}"} 