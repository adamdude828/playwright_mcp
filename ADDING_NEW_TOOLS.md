# Adding New Tools to Playwright MCP

This guide explains how to add new tools to the Playwright MCP system. The system uses a layered architecture with MCP Server and Browser Daemon components.

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  MCP Server │ ──▶ │ Tool Handler │ ──▶ │   Browser   │
│   (Front)   │     │   (Middle)   │     │   Daemon    │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 1. Tool Registration

Tools must be registered in two places:

### 1.1 Tool Definition

Add your tool definition in `src/playwright_mcp/browser_daemon/tools/definitions.py`:

```python
def get_tool_definitions() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="your-tool-name",
            description="Description of what your tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Description of parameter"
                    }
                },
                "required": ["param1"]
            }
        )
    ]
```

### 1.2 Tool Handler Registration

Create a new handler in `src/playwright_mcp/browser_daemon/tools/handlers/your_tool.py`:

```python
from mcp.types import TextContent
import traceback
from .utils import logger

async def handle_your_tool(arguments: dict) -> list:
    """Handle your-tool tool."""
    logger.info(f"Handling your-tool request with args: {arguments}")
    try:
        # Implement your tool logic here
        result = "Your result"
        
        return [
            TextContent(
                type="text",
                text=str(result)
            )
        ]
    except Exception as e:
        logger.error(f"Error in handle_your_tool: {e}")
        logger.error(traceback.format_exc())
        return [
            TextContent(
                type="text",
                text=str(e)
            )
        ]
```

Register your handler in `src/playwright_mcp/browser_daemon/tools/handlers/__init__.py`:

```python
from .your_tool import handle_your_tool

TOOL_HANDLERS = {
    # ... existing handlers ...
    "your-tool-name": handle_your_tool
}
```

### 1.3 Handler Structure Best Practices

1. **Function Signature**:
   ```python
   from typing import Dict
   from .utils import logger, create_response

   async def handle_your_tool(arguments: Dict) -> dict:
       """Handle your-tool command by doing X."""
   ```

2. **Standard Imports**:
   - Import `Dict` from typing for type hints
   - Import `logger` and `create_response` from `.utils`

3. **Response Formatting**:
   Always use the `create_response` utility for consistent response formatting:
   ```python
   # Success response
   result = "Operation completed"
   return create_response(result)

   # Error response
   error_msg = "Something went wrong"
   return create_response(error_msg, is_error=True)

   # Dictionary response (automatically JSON formatted)
   data = {"key": "value", "numbers": [1, 2, 3]}
   return create_response(data)
   ```

4. **Error Handling**:
   ```python
   try:
       # Your tool logic here
       result = await perform_operation()
       return create_response(result)
   except Exception as e:
       logger.error(f"Error in handle_your_tool: {e}")
       return create_response(str(e), is_error=True)
   ```

5. **Input Validation**:
   ```python
   # Required parameters
   if "required_param" not in arguments:
       return create_response("required_param is required", is_error=True)
   
   # Optional parameters with defaults
   optional_param = arguments.get("optional_param", default_value)
   ```

## 2. How list-tools Works

The `