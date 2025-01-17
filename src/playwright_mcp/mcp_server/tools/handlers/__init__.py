from .search_dom import SearchDOMHandler
from .search_dom_js import SearchDOMJSHandler

TOOL_HANDLERS = {
    "search-dom": SearchDOMHandler,
    "search-dom-js": SearchDOMJSHandler,
} 