from .start_daemon import handle_start_daemon
from .stop_daemon import handle_stop_daemon
from .navigate import handle_navigate
from .close_browser import handle_close_browser
from .new_tab import handle_new_tab
from .close_tab import handle_close_tab
from .execute_js import handle_execute_js
from .explore_dom import handle_explore_dom
from .screenshot import handle_screenshot
from .highlight_element import handle_highlight_element


# Map of tool names to their handlers
TOOL_HANDLERS = {
    "start-daemon": handle_start_daemon,
    "stop-daemon": handle_stop_daemon,
    "navigate": handle_navigate,
    "close-browser": handle_close_browser,
    "new-tab": handle_new_tab,
    "close-tab": handle_close_tab,
    "execute-js": handle_execute_js,
    "explore-dom": handle_explore_dom,
    "screenshot": handle_screenshot,
    "highlight-element": handle_highlight_element,
}
