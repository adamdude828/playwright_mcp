"""Test client for Model Context Protocol (MCP).

This is a simplified MCP client for testing purposes that uses the official MCP Python SDK.
It directly executes tool calls for testing, bypassing the LLM interaction.
"""
import os
import logging
import json
from typing import Any, Dict, List, Optional
from mcp.types import TextContent, EmbeddedResource
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, get_default_environment, StdioServerParameters
from contextlib import AsyncExitStack


# Set up logging with file handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Add file handler
fh = logging.FileHandler('logs/test_client.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Add console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


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
        self.read_stream, self.write_stream = stdio_transport
        
        # Create and initialize client session
        logger.debug("Creating client session...")
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.read_stream, self.write_stream)
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
        
        try:
            # Make the tool call through the session
            result = await self.session.call_tool(tool_name, tool_args)
            logger.debug(f"Raw result type: {type(result)}")
            logger.debug(f"Raw result content: {result}")
            
            # Log detailed content of each response item
            for item in result:
                if isinstance(item, TextContent):
                    logger.debug(f"Text content: {item.text}")
                elif isinstance(item, EmbeddedResource):
                    logger.debug(f"Resource URI: {item.resource.uri}")
                    logger.debug(f"Resource text: {item.resource.text}")
                    try:
                        parsed = json.loads(item.resource.text)
                        logger.debug(f"Parsed JSON: {json.dumps(parsed, indent=2)}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON: {e}")
                        logger.debug(f"Raw text causing error: {item.resource.text!r}")
            
            return result
        except Exception as e:
            logger.exception(f"Error in call_tool: {e}")
            raise 