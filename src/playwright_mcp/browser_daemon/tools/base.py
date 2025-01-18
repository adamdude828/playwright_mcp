from typing import Any, Dict, Type
from pydantic import BaseModel
from functools import wraps
from mcp.types import Tool, TextContent


class ToolHandler:
    """Base class for tool handlers using Pydantic models."""
    name: str = ""
    description: str = ""
    input_model: Type[BaseModel] = None
    
    @classmethod
    def register(cls, name: str, description: str):
        """Decorator to register a tool handler with Pydantic validation."""
        def decorator(func):
            @wraps(func)
            async def wrapper(arguments: Dict[str, Any], daemon=None) -> Dict[str, Any]:
                # Validate input using Pydantic
                try:
                    validated_args = cls.input_model(**arguments)
                    result = await func(validated_args, daemon=daemon)
                    return {
                        "content": [
                            TextContent(
                                type="text",
                                text=str(result)
                            )
                        ]
                    }
                except Exception as e:
                    return {
                        "isError": True,
                        "content": [
                            TextContent(
                                type="text",
                                text=str(e)
                            )
                        ]
                    }
            
            # Store metadata on wrapper
            wrapper.tool_name = name
            wrapper.description = description
            wrapper.input_model = cls.input_model
            return wrapper
        return decorator

    @classmethod
    def to_tool_definition(cls) -> Tool:
        """Convert handler to MCP Tool definition."""
        if not cls.input_model:
            raise ValueError(f"Tool handler {cls.__name__} has no input_model defined")
        schema = cls.input_model.schema()
        return Tool(
            name=cls.name,
            description=cls.description,
            inputSchema=schema
        ) 