from .start_daemon import handle_start_daemon
from .stop_daemon import handle_stop_daemon
from .navigate import handle_navigate
from .close_browser import handle_close_browser
from .new_tab import handle_new_tab
from .close_tab import handle_close_tab


# Map of tool names to their handlers
TOOL_HANDLERS = {
    "start-daemon": handle_start_daemon,
    "stop-daemon": handle_stop_daemon,
    "navigate": handle_navigate,
    "close-browser": handle_close_browser,
    "new-tab": handle_new_tab,
    "close-tab": handle_close_tab,
}
