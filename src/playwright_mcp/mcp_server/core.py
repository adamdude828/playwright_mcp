"""Core MCP server functionality."""
from typing import Dict, Any
from .server import TOOLS


class TextContent:
    """Class representing text content in MCP responses."""
    def __init__(self, text: str, type: str = "text"):
        self.text = text
        self.type = type

    def __str__(self):
        """String representation should be just the text content."""
        return self.text
        
    def __repr__(self):
        """Representation for debugging."""
        return f"TextContent(type='{self.type}', text='{self.text}')"
        
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "text": self.text
        }
        
    def __json__(self):
        """Make the class JSON serializable."""
        return self.to_dict()


def get_tool_definitions() -> Dict[str, Any]:
    """Get tool definitions."""
    return {
        tool.name: {
            "description": tool.description,
            "parameters": tool.inputSchema
        }
        for tool in TOOLS
    } 