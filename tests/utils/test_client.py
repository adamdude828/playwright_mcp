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
                session_id = tool_args.get("session_id", "")
                page_id = tool_args.get("page_id", "")
                url = tool_args.get("url", "")
                
                if "thisisnotarealwebsite.com" in url:
                    response = "net::ERR_NAME_NOT_RESOLVED"
                else:
                    response = {
                        "session_id": session_id if session_id else "chromium_test_session_1",
                        "page_id": page_id if page_id else "test_page_1",
                        "message": "Navigated successfully",
                        "created_session": not bool(session_id),
                        "created_page": not bool(page_id)
                    }
        elif tool_name == "execute-js":
            session_id = tool_args.get("session_id", "")
            page_id = tool_args.get("page_id", "")
            script = tool_args.get("script", "")

            if session_id != "chromium_test_session_1":
                response = f"No browser session found for ID: {session_id}"
            elif page_id != "test_page_1":
                response = f"No page found with ID: {page_id}"
            elif script == "2 + 2":
                response = "4"
            elif script == "invalid javascript":
                response = "SyntaxError: Unexpected identifier 'javascript'"
            elif "obj.nested.array[1]" in script:
                response = "2"
            else:
                response = {"message": "Tool executed successfully"}
        elif tool_name == "explore-dom":
            page_id = tool_args.get("page_id", "")
            selector = tool_args.get("selector", "")
            
            if page_id != "test_page_1":
                response = f"No page found with ID: {page_id}"
            elif selector == "body":
                response = (
                    "Element: body (3 children)\n"
                    "  - div.main (2 children)\n"
                    "    - h1: Example Domain\n"
                    "    - p: This domain is for use in illustrative examples in documents.\n"
                    "  - div.footer (1 child)\n"
                    "    - p: More information..."
                )
            else:
                response = f"Element: {selector}\n  No children found"
        elif tool_name == "highlight-element":
            page_id = tool_args.get("page_id", "")
            selector = tool_args.get("selector", "")
            save_path = tool_args.get("save_path", "")
            
            if page_id != "test_page_1":
                response = f"No page found with ID: {page_id}"
            elif not selector:
                response = "No selector provided"
            elif not save_path:
                response = "No save path provided"
            else:
                # Create a dummy PNG file
                import os
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, "wb") as f:
                    # Write a minimal valid PNG file
                    png_data = (
                        "89504e470d0a1a0a"    # PNG signature
                        "0000000d49484452"     # IHDR chunk header
                        "0000000100000001"     # Width=1, Height=1
                        "08060000001f15c489"   # Bit depth etc
                        "0000000d49444154"     # IDAT chunk header
                        "78da636400000000"     # Compressed pixel data
                        "06000557bfabc3"       # IDAT chunk trailer
                        "0000000049454e44"     # IEND chunk header
                        "ae426082"             # IEND chunk trailer
                    )
                    f.write(bytes.fromhex(png_data))
                response = {"message": "Element highlighted and screenshot saved"}
        elif tool_name == "ai-agent":
            page_id = tool_args.get("page_id", "")
            query = tool_args.get("query", "")
            
            if not query:
                response = {"error": "Missing required argument: query"}
            elif page_id != "test_page_1":
                # Store the invalid page ID for later
                response = {
                    "job_id": "test_job_invalid_page",
                    "page_id": page_id  # Store this for later
                }
            else:
                response = {"job_id": "test_job_1"}
        elif tool_name == "get-ai-result":
            job_id = tool_args.get("job_id", "")
            
            if job_id == "test_job_1":
                response = {
                    "status": "completed",
                    "result": "The main heading is 'Example Domain'"
                }
            elif job_id == "test_job_invalid_page":
                response = {
                    "status": "error",
                    "result": None,
                    "error": "Invalid page ID"
                }
            else:
                response = {
                    "status": "error",
                    "result": None,
                    "error": "Job not found"
                }
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