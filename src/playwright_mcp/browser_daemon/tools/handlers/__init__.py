from .launch_browser import handle_launch_browser
from .new_page import handle_new_page
from .goto import handle_goto
from .close_browser import handle_close_browser
from .close_page import handle_close_page
from .analyze_page import handle_analyze_page


# Map of tool names to their handlers
TOOL_HANDLERS = {
    "launch-browser": handle_launch_browser,
    "new-page": handle_new_page,
    "goto": handle_goto,
    "close-browser": handle_close_browser,
    "close-page": handle_close_page,
    "analyze-page": handle_analyze_page
}
