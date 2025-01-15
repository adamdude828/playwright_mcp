"""Test client for Model Context Protocol (MCP).

This is a simplified MCP client for testing purposes. Unlike a full MCP client that would:
1. Connect to a server script
2. Get available tools
3. Send queries to Claude
4. Execute tool calls based on Claude's decisions

This test client directly executes tool calls for testing, bypassing the LLM interaction.
It uses the same tool handlers that would be available to a full MCP client.
"""
from playwright_mcp.browser_daemon.tools.handlers import TOOL_HANDLERS
from typing import List
from mcp.types import TextContent


class TestClient:
    """A simplified MCP client for testing.
    
    This client provides direct access to MCP tools without going through an LLM.
    It maintains the same protocol for tool calls but allows tests to directly:
    1. Call specific tools with arguments 
    2. Get tool responses in the same format as a full client
    
    Note: The client does not manage tool lifecycle (e.g. starting/stopping daemons).
    Tests should handle that explicitly for clarity.
    """
    
    async def __aenter__(self):
        """Start the test client."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up the test client."""
        pass
        
    async def call_tool(self, tool_name: str, tool_args: dict) -> List[TextContent]:
        """Execute an MCP tool call directly.
        
        Args:
            tool_name: Name of the MCP tool to call
            tool_args: Arguments to pass to the tool
            
        Returns:
            List[TextContent]: The tool's response as a list of TextContent objects
        """
        handler = TOOL_HANDLERS[tool_name]
        response = await handler(tool_args)
        
        # Ensure response is always a list of TextContent
        if not isinstance(response, list):
            return [TextContent(type="text", text=str(response))]
            
        return response 