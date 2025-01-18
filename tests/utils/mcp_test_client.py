"""MCP test client that connects directly to the server.

This client implements the MCP protocol to connect directly to the server,
rather than mocking responses or using mcp-cli. It provides a stable
connection for testing server behavior.
"""
from typing import Dict, Any, List, Optional
from mcp.types import TextContent, JSONRPCMessage
from mcp.client.session import ClientSession
from mcp.client.stdio import get_default_environment
from contextlib import AsyncExitStack
import os
import signal
import json
import logging
import anyio
import sys
from anyio.streams.text import TextReceiveStream

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MCPTestClient:
    """MCP test client that maintains a single server connection."""
    
    # Class variable to track server process
    _server_process = None
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
    
    @classmethod
    def _kill_existing_server(cls):
        """Kill any existing server process."""
        if cls._server_process:
            try:
                logger.debug(f"Killing existing server process {cls._server_process}")
                os.kill(cls._server_process, signal.SIGTERM)
                cls._server_process = None
            except ProcessLookupError:
                # Process already gone
                logger.debug("Process already gone")
                cls._server_process = None
    
    async def __aenter__(self):
        """Initialize client and connect to server."""
        # Kill any existing server
        self._kill_existing_server()
        
        logger.debug("Starting server process...")
        # Start the server process
        process = await anyio.open_process(
            ["python", "-m", "playwright_mcp", "--mode", "server"],
            env=get_default_environment(),
            stderr=sys.stderr,
        )
        
        # Store the process ID
        self.__class__._server_process = process.pid
        logger.debug(f"Server process started with PID {process.pid}")
        
        # Create memory streams for message passing
        logger.debug("Creating memory streams...")
        read_stream_writer, read_stream = anyio.create_memory_object_stream[JSONRPCMessage | Exception](0)
        write_stream, write_stream_reader = anyio.create_memory_object_stream[JSONRPCMessage](0)
        
        # Start background tasks for I/O
        async def stdout_reader():
            assert process.stdout, "Opened process is missing stdout"
            try:
                async with read_stream_writer:
                    buffer = ""
                    logger.debug("Starting stdout reader loop...")
                    async for chunk in TextReceiveStream(process.stdout, encoding="utf-8"):
                        logger.debug(f"Received chunk: {chunk}")
                        lines = (buffer + chunk).split("\n")
                        buffer = lines.pop()
                        
                        for line in lines:
                            try:
                                logger.debug(f"Parsing line: {line}")
                                message = JSONRPCMessage.model_validate_json(line)
                                logger.debug(f"Parsed message: {message}")
                            except Exception as exc:
                                logger.error(f"Error parsing message: {exc}")
                                await read_stream_writer.send(exc)
                                continue
                            
                            await read_stream_writer.send(message)
            except anyio.ClosedResourceError:
                logger.debug("stdout reader closed")
                await anyio.lowlevel.checkpoint()
        
        async def stdin_writer():
            assert process.stdin, "Opened process is missing stdin"
            try:
                async with write_stream_reader:
                    logger.debug("Starting stdin writer loop...")
                    async for message in write_stream_reader:
                        json_str = message.model_dump_json(by_alias=True, exclude_none=True)
                        logger.debug(f"Writing message: {json_str}")
                        await process.stdin.send((json_str + "\n").encode("utf-8"))
            except anyio.ClosedResourceError:
                logger.debug("stdin writer closed")
                await anyio.lowlevel.checkpoint()
        
        # Start I/O tasks
        logger.debug("Starting I/O tasks...")
        task_group = await self.exit_stack.enter_async_context(anyio.create_task_group())
        task_group.start_soon(stdout_reader)
        task_group.start_soon(stdin_writer)
        
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
        """Clean up server resources."""
        logger.debug("Cleaning up resources...")
        await self.exit_stack.aclose()
        self._kill_existing_server()
    
    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> List[TextContent]:
        """Call a tool on the server and return the response.
        
        Args:
            tool_name: Name of the tool to call
            tool_args: Arguments to pass to the tool
            
        Returns:
            List of TextContent responses from the tool
        """
        if not self.session:
            raise RuntimeError("Session not initialized - use async with")
            
        logger.debug(f"Calling tool {tool_name} with args {tool_args}")
        # Make the tool call through the session
        result = await self.session.call_tool(tool_name, tool_args)
        
        # Debug log the result
        logger.debug(f"Raw result: {result}")
        if isinstance(result, list):
            logger.debug(f"Result items: {[type(item) for item in result]}")
            logger.debug(f"Result texts: {[item.text for item in result]}")
        
        # Convert result to list of TextContent if needed
        if isinstance(result, list):
            return [
                TextContent(text=json.loads(item.text) if isinstance(item.text, str) else item.text)
                for item in result
            ]
        return [TextContent(text=json.loads(str(result)) if isinstance(result, str) else result)] 