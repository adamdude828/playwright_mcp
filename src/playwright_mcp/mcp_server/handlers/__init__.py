"""Tool handlers for MCP server."""
from .start_daemon import handle_start_daemon
from .stop_daemon import handle_stop_daemon
from .navigate import handle_navigate
from .execute_js import handle_execute_js
from .close_tab import handle_close_tab
from .explore_dom import handle_explore_dom
from .interact_dom import handle_interact_dom
from .search_dom import handle_search_dom
from .screenshot import handle_screenshot
from .highlight_element import handle_highlight_element
from .ai_agent import handle_ai_agent
from .ai_agent.get_result import handle_get_ai_result


# Map of tool names to their handlers
HANDLERS = {
    "start-daemon": handle_start_daemon,
    "stop-daemon": handle_stop_daemon,
    "navigate": handle_navigate,
    "execute-js": handle_execute_js,
    "close-tab": handle_close_tab,
    "explore-dom": handle_explore_dom,
    "interact-dom": handle_interact_dom,
    "search-dom": handle_search_dom,
    "screenshot": handle_screenshot,
    "highlight-element": handle_highlight_element,
    "ai-agent": handle_ai_agent,
    "get-ai-result": handle_get_ai_result
}

# Export HANDLERS as TOOL_HANDLERS for backward compatibility
TOOL_HANDLERS = HANDLERS
