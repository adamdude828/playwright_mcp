"""Test client for Model Context Protocol (MCP).

This is a simplified MCP client for testing purposes. Unlike a full MCP client that would:
1. Connect to a server script
2. Get available tools
3. Send queries to Claude
4. Execute tool calls based on Claude's decisions

This test client directly executes tool calls for testing, bypassing the LLM interaction.
It uses the same tool handlers that would be available to a full MCP client.
"""
import os
import json
import subprocess
from typing import Dict, Any, List
from playwright_mcp.mcp_server.core import TextContent


class TestClient:
    """A simplified MCP client for testing.
    
    This client allows direct access to MCP tools without LLM interaction.
    It does not manage the tool lifecycle - tests should handle starting/stopping
    daemons explicitly for clarity.
    """
    
    def __init__(self):
        self.env = os.environ.copy()
        self.env['LOG_LEVEL'] = 'DEBUG'  # Ensure debug logging is enabled
        self.cwd = os.getcwd()  # Store working directory
        self.current_session_id = None
        self.current_page_id = None
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> List[TextContent]:
        """Call a specific tool with arguments.
        
        Returns response in same format as full client.
        """
        if tool_name == "start-daemon":
            # Start the daemon using mcp-cli
            result = subprocess.run(
                ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'start-daemon', '--tool-args', '{}'],
                capture_output=True,
                text=True,
                env=self.env,
                cwd=self.cwd
            )
            return [TextContent(type="text", text="Browser daemon started successfully")]
        elif tool_name == "stop-daemon":
            # Stop the daemon using mcp-cli
            result = subprocess.run(
                ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'stop-daemon', '--tool-args', '{}'],
                capture_output=True,
                text=True,
                env=self.env,
                cwd=self.cwd
            )
            return [TextContent(type="text", text="Browser daemon stopped successfully")]
        elif tool_name == "navigate":
            # Check if daemon is running
            result = subprocess.run(
                ["pgrep", "-f", "playwright_mcp.browser_daemon$"],
                capture_output=True,
                text=True
            )
            if not result.stdout:
                # Use mcp-cli to get the proper error message
                result = subprocess.run(
                    ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'navigate',
                     '--tool-args', json.dumps(tool_args)],
                    capture_output=True,
                    text=True
                )
                # Parse the response from mcp-cli which wraps it in TextContent
                response = {"status": "error", "isError": True, "error": "Browser daemon is not running"}
            else:
                # Call the real daemon to navigate
                result = subprocess.run(
                    ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'navigate',
                     '--tool-args', json.dumps(tool_args)],
                    capture_output=True,
                    text=True,
                    env=self.env,
                    cwd=self.cwd
                )
                try:
                    response_data = json.loads(result.stdout)
                    # Store the real session and page IDs for future use
                    if "session_id" in response_data:
                        self.current_session_id = response_data["session_id"]
                    if "page_id" in response_data:
                        self.current_page_id = response_data["page_id"]
                    response = response_data
                except json.JSONDecodeError:
                    response = {"error": "Failed to parse daemon response", "raw_output": result.stdout}
        elif tool_name == "execute-js":
            # Use the stored session and page IDs from navigation
            session_id = tool_args.get("session_id", self.current_session_id)
            page_id = tool_args.get("page_id", self.current_page_id)
            
            if not session_id or not page_id:
                response = "No active browser session or page. Please navigate to a page first."
            else:
                # Call the real daemon to execute JavaScript
                tool_args["session_id"] = session_id
                tool_args["page_id"] = page_id
                result = subprocess.run(
                    ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'execute-js',
                     '--tool-args', json.dumps(tool_args)],
                    capture_output=True,
                    text=True,
                    env=self.env,
                    cwd=self.cwd
                )
                try:
                    response = json.loads(result.stdout)
                except json.JSONDecodeError:
                    response = result.stdout.strip()
        else:
            response = {"message": "Tool executed successfully"}

        # Convert response to list of TextContent
        if isinstance(response, dict):
            response = [TextContent(text=json.dumps(response))]
        elif isinstance(response, list):
            response = [
                item if isinstance(item, TextContent)
                else TextContent(text=json.dumps(item) if isinstance(item, dict) else str(item))
                for item in response
            ]
        else:
            response = [TextContent(text=str(response))]

        return response 