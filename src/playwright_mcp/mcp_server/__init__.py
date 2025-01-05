"""MCP server package."""
from .core import main
from .server import server, handle_list_tools, handle_call_tool

__all__ = ['main', 'server', 'handle_list_tools', 'handle_call_tool'] 