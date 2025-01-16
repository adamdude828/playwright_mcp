"""MCP server tools package."""
from .handlers.search_dom import SearchDOMHandler

# Register tool handlers
HANDLERS = [
    SearchDOMHandler(),
] 