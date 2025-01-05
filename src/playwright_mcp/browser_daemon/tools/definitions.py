from mcp.types import Tool


def get_tool_definitions() -> list[Tool]:
    """Get all tool definitions."""
    return [
        Tool(
            name="launch-browser",
            description="Launch a new browser instance and return a session ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "browser_type": {
                        "type": "string",
                        "description": (
                            "Type of browser to launch (chromium, firefox, or webkit)"
                        ),
                        "enum": ["chromium", "firefox", "webkit"]
                    },
                    "headless": {
                        "type": "boolean",
                        "description": "Whether to run browser in headless mode",
                        "default": True
                    }
                },
                "required": ["browser_type"]
            }
        ),
        Tool(
            name="new-page",
            description="Create a new page in a browser session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID from launch-browser"
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="goto",
            description="Navigate to a URL in a page",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID from new-page"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    }
                },
                "required": ["page_id", "url"]
            }
        ),
        Tool(
            name="close-browser",
            description="Close a browser session and clean up resources",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID to close"
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="close-page",
            description="Close a specific page in a browser session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID containing the page"
                    },
                    "page_id": {
                        "type": "string",
                        "description": "Page ID to close"
                    }
                },
                "required": ["session_id", "page_id"]
            }
        )
    ]
