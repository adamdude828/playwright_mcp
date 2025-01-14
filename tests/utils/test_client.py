"""Test client for Model Context Protocol (MCP).

This is a simplified MCP client for testing purposes. Unlike a full MCP client that would:
1. Connect to a server script
2. Get available tools
3. Send queries to Claude
4. Execute tool calls based on Claude's decisions

This test client directly executes tool calls for testing, bypassing the LLM interaction.
It uses the same tool handlers that would be available to a full MCP client.
"""
import json
from playwright_mcp.browser_daemon.tools.handlers import TOOL_HANDLERS


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
        
    async def call_tool(self, tool_name: str, tool_args: dict) -> dict:
        """Execute an MCP tool call directly.
        
        Args:
            tool_name: Name of the MCP tool to call
            tool_args: Arguments to pass to the tool
            
        Returns:
            The tool's response data
        """
        handler = TOOL_HANDLERS[tool_name]
        response = await handler(tool_args)
        
        # Handle TextContent responses from the MCP server
        if isinstance(response, list) and len(response) > 0:
            if hasattr(response[0], 'text'):
                text = response[0].text
                try:
                    # Try to parse as JSON first
                    response_data = json.loads(text)
                    if "error" in response_data:
                        raise RuntimeError(response_data["error"])
                    return response_data
                except json.JSONDecodeError:
                    # If not JSON, return as plain text
                    return {"result": text}
            
        return response 