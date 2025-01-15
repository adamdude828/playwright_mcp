from mcp.types import Tool


def get_tool_definitions() -> list[Tool]:
    """Get all tool definitions."""
    return [
        Tool(
            name="start-daemon",
            description="Start the browser daemon if it's not already running",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="stop-daemon",
            description="Stop the browser daemon if it's running",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="navigate",
            description=(
                "Navigate to a URL, optionally reusing an existing browser session "
                "or page"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    },
                    "session_id": {
                        "type": "string",
                        "description": (
                            "Optional browser session ID to reuse. If not provided, "
                            "a new session will be created."
                        )
                    },
                    "page_id": {
                        "type": "string",
                        "description": (
                            "Optional page ID to reuse. If not provided, "
                            "a new page will be created."
                        )
                    },
                    "browser_type": {
                        "type": "string",
                        "description": "Type of browser to launch if creating new session",
                        "enum": ["chromium", "firefox", "webkit"],
                        "default": "chromium"
                    },
                    "headless": {
                        "type": "boolean",
                        "description": "Whether to run browser in headless mode if creating new session",
                        "default": True
                    },
                    "wait_until": {
                        "type": "string",
                        "description": "When to consider navigation complete",
                        "enum": ["load", "domcontentloaded", "networkidle"]
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="execute-js",
            description=(
                "Execute JavaScript code in the context of a page and return the results. "
                "The code will be executed in the browser and can interact with the DOM."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID where the page is running"
                    },
                    "page_id": {
                        "type": "string",
                        "description": "Page ID where to execute the JavaScript"
                    },
                    "script": {
                        "type": "string",
                        "description": (
                            "JavaScript code to execute. Can be a function or expression. "
                            "If it's a function, it should be self-contained and return a value."
                        )
                    }
                },
                "required": ["session_id", "page_id", "script"]
            }
        ),
        Tool(
            name="new-tab",
            description="Open a new tab in an existing browser session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID to open the tab in"
                    }
                },
                "required": ["session_id"]
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
            name="close-tab",
            description="Close a specific tab in a browser session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID containing the tab"
                    },
                    "page_id": {
                        "type": "string",
                        "description": "Tab ID to close"
                    }
                },
                "required": ["session_id", "page_id"]
            }
        ),
        Tool(
            name="explore-dom",
            description="Explore immediate children of a DOM element",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID to explore"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector to filter elements"
                    }
                },
                "required": ["page_id"]
            }
        )
    ]
