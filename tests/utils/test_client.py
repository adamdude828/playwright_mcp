"""Test client for Model Context Protocol (MCP).

This is a simplified MCP client for testing purposes that uses the official MCP Python SDK.
It directly executes tool calls for testing, bypassing the LLM interaction.
"""
import os
import logging
from typing import Any, Dict, List, Optional
from mcp.types import TextContent, EmbeddedResource
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, get_default_environment, StdioServerParameters
from contextlib import AsyncExitStack


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def is_mcp_content(item) -> bool:
    """Check if an item is an MCP content type."""
    return isinstance(item, (TextContent, EmbeddedResource))


class TestClient:
    """A simplified MCP client for testing purposes.
    Bypasses LLM interaction and directly executes tool calls.
    """
    
    def __init__(self, working_dir: Optional[str] = None):
        self.working_dir = working_dir or os.getcwd()
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def __aenter__(self):
        """Initialize client and connect to server."""
        logger.debug("Starting server process...")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "playwright_mcp", "--mode", "server"],
            env=get_default_environment()
        )
        
        # Connect to server using stdio transport
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        read_stream, write_stream = stdio_transport
        
        # Create and initialize client session
        logger.debug("Creating client session...")
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        logger.debug("Initializing client session...")
        await self.session.initialize()
        logger.debug("Client session initialized")
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources."""
        logger.debug("Cleaning up resources...")
        await self.exit_stack.aclose()

    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> List[TextContent | EmbeddedResource]:
        """Call a tool on the server and return the response.
        
        Args:
            tool_name: Name of the tool to call
            tool_args: Arguments to pass to the tool
            
        Returns:
            List of TextContent or EmbeddedResource responses from the tool
        """
        if not self.session:
            raise RuntimeError("Session not initialized - use async with")
            
        logger.debug(f"Calling tool {tool_name} with args {tool_args}")
        # Make the tool call through the session
        result = await self.session.call_tool(tool_name, tool_args)
        logger.debug(f"Raw result: {result}")
        
        return result 