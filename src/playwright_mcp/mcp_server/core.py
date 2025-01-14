"""Core MCP server functionality."""
from typing import Dict, Any
from .server import TOOLS


def get_tool_definitions() -> Dict[str, Any]:
    """Get tool definitions."""
    return {
        tool.name: {
            "description": tool.description,
            "parameters": tool.inputSchema
        }
        for tool in TOOLS
    } 