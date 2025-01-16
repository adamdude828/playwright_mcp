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
            description=(
                "Analyze and explore the DOM structure of a webpage by examining the immediate children of a "
                "specified element. For each child element, returns: the HTML tag name (lowercase), element ID, "
                "CSS classes, text content, and number of child elements it contains. Results are formatted in a "
                "tree-like structure for easy visualization. If no selector is provided, defaults to 'body' element."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID to explore"
                    },
                    "selector": {
                        "type": "string",
                        "description": (
                            "CSS selector to target specific element (e.g. '#main', '.content', 'div.header'). "
                            "Defaults to 'body' if not specified."
                        )
                    }
                },
                "required": ["page_id"]
            }
        ),
        Tool(
            name="interact-dom",
            description=(
                "Perform real-time interactions with DOM elements like clicking, typing, hovering, etc. "
                "Supports common user interactions and returns the result of the operation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID where the interaction should occur"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector to target the element to interact with"
                    },
                    "action": {
                        "type": "string",
                        "description": "Type of interaction to perform",
                        "enum": ["click", "type", "hover", "focus", "press", "select"]
                    },
                    "value": {
                        "type": "string",
                        "description": "Value to use for the interaction (e.g. text to type, key to press)"
                    },
                    "options": {
                        "type": "object",
                        "description": (
                            "Additional options for the interaction "
                            "(e.g. click position, delay between keystrokes)"
                        ),
                        "properties": {
                            "delay": {
                                "type": "number",
                                "description": "Delay between keystrokes for typing (milliseconds)"
                            },
                            "position": {
                                "type": "object",
                                "description": "Click position relative to element",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"}
                                }
                            },
                            "button": {
                                "type": "string",
                                "enum": ["left", "right", "middle"],
                                "description": "Mouse button to use for click"
                            },
                            "clickCount": {
                                "type": "number",
                                "description": "Number of times to click"
                            }
                        }
                    }
                },
                "required": ["page_id", "selector", "action"]
            }
        ),
        Tool(
            name="search-dom",
            description=(
                "Search for DOM elements matching specific criteria like text content, "
                "tag name, or attributes. Returns matching elements with their properties "
                "and location in the DOM tree."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID to search in"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text content to search for (case-insensitive)"
                    },
                    "tag": {
                        "type": "string",
                        "description": "HTML tag name to filter by (e.g. 'div', 'a', 'button')"
                    },
                    "class_name": {
                        "type": "string",
                        "description": "CSS class to filter by"
                    },
                    "id": {
                        "type": "string",
                        "description": "Element ID to filter by"
                    },
                    "attribute": {
                        "type": "object",
                        "description": "Custom attribute to filter by",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Attribute name"
                            },
                            "value": {
                                "type": "string",
                                "description": "Attribute value"
                            }
                        },
                        "required": ["name", "value"]
                    }
                },
                "required": ["page_id"]
            }
        ),
        Tool(
            name="screenshot",
            description="Take a screenshot of the current page or a specific element",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID to take screenshot of"
                    },
                    "selector": {
                        "type": "string",
                        "description": "Optional CSS selector to screenshot specific element"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to save screenshot file"
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "Whether to take full page screenshot",
                        "default": False
                    }
                },
                "required": ["page_id", "path"]
            }
        ),
        Tool(
            name="highlight-element",
            description=(
                "Highlight a DOM element by adding a colored outline. Useful for visualizing "
                "element locations during testing and debugging."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID containing the element"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for element to highlight"
                    },
                    "color": {
                        "type": "string",
                        "description": "Color to use for highlight (CSS color value)",
                        "default": "red"
                    },
                    "duration": {
                        "type": "number",
                        "description": "How long to show highlight in milliseconds",
                        "default": 1000
                    }
                },
                "required": ["page_id", "selector"]
            }
        ),
        Tool(
            name="find-similar-selectors",
            description=(
                "Find alternative CSS selectors for a given element that are more robust "
                "against page changes. Returns multiple selector options ranked by reliability."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID containing the element"
                    },
                    "selector": {
                        "type": "string",
                        "description": "Current CSS selector for the element"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of alternative selectors to return",
                        "default": 5
                    }
                },
                "required": ["page_id", "selector"]
            }
        )
    ]
