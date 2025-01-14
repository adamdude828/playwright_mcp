import subprocess
import shutil
import time
import re
import os
import signal
import pytest
from tests.utils.test_client import TestClient


def clean_output(output: str) -> str:
    """Remove ANSI escape codes and formatting characters from output."""
    # Remove ANSI escape codes
    output = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', output)
    # Remove box drawing characters and extra spaces
    output = re.sub(r'[─│╭╮╰╯]|\s+', ' ', output)
    # Remove extra whitespace
    output = output.strip()
    # Extract just the response part
    if "Tool Response" in output:
        output = output.split("Tool Response")[1].strip()
    return output


def test_mcp_cli_available():
    """Test that mcp-cli is available in the system path."""
    mcp_cli_path = shutil.which('mcp-cli')
    assert mcp_cli_path is not None, "mcp-cli not found in system path"


def test_playwright_tool_available():
    """Test that mcp-cli has access to playwright tools."""
    # Get list of servers
    servers_result = subprocess.run(
        ['mcp-cli', 'list-servers'],
        capture_output=True,
        text=True
    )
    assert servers_result.returncode == 0, "Failed to list MCP servers"
    
    # Parse server list from text output
    output_lines = servers_result.stdout.split('\n')
    servers = []
    for line in output_lines:
        if line.strip().startswith('•'):
            servers.append(line.strip()[2:].strip())
    
    assert len(servers) > 0, "No MCP servers found"
    assert 'playwright' in servers, "Playwright server not found in server list"
    
    # Check playwright server for tools
    tools_result = subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'list-tools'],
        capture_output=True,
        text=True
    )
    
    assert tools_result.returncode == 0, "Failed to list tools for playwright server"
    
    # Parse tools from the box-formatted output
    tools = set()
    lines = tools_result.stdout.split('\n')
    for i, line in enumerate(lines):
        # Each tool name appears on a line by itself after a box border
        if line.strip().startswith('╭') and i + 2 < len(lines):
            # Extract tool name and remove box borders and padding
            tool_name = lines[i + 2].strip()
            if tool_name and not tool_name.startswith('╰'):
                # Remove box borders and padding
                tool_name = tool_name.strip('│').strip()
                tools.add(tool_name)
    
    assert len(tools) > 0, "No tools found in playwright server"
    
    # Verify we have the expected playwright-related tools
    expected_tools = {
        'start-daemon', 'stop-daemon', 'navigate', 'new-tab',
        'analyze-page', 'close-browser', 'close-tab', 'execute-js'
    }
    missing_tools = expected_tools - tools
    assert not missing_tools, f"Missing expected tools: {missing_tools}"


def test_navigate_without_daemon():
    """Test that trying to navigate without starting the daemon fails with appropriate error."""
    # First ensure no daemon is running by checking and killing any existing processes
    result = subprocess.run(
        ["pgrep", "-f", "playwright_mcp.browser_daemon.browser_manager"],
        capture_output=True,
        text=True
    )
    if result.stdout:
        for pid in result.stdout.strip().split('\n'):
            try:
                os.kill(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
    time.sleep(1)  # Wait for processes to terminate

    # Also try to remove the socket file if it exists
    socket_path = os.path.join(os.getenv('TMPDIR', '/tmp'), 'playwright_mcp.sock')
    try:
        os.unlink(socket_path)
    except OSError:
        pass

    # Try to navigate without daemon running
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'navigate',
         '--tool-args', '{"url": "https://example.com"}'],
        capture_output=True,
        text=True
    )

    # The error comes back in stdout as part of the tool response
    assert "Browser daemon is not running" in result.stdout, "Response should indicate daemon is not running"


@pytest.mark.asyncio
async def test_start_daemon():
    """Test that the start-daemon command works successfully."""
    # First ensure daemon is stopped
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', '--tool', 'stop-daemon', 'call-tool'],
        capture_output=True,
        text=True
    )
    time.sleep(1)
    
    # Start the daemon using test client
    async with TestClient() as client:
        result = await client.call_tool("start-daemon", {})
        
        # Check response format follows MCP protocol
        assert "content" in result, "Response should include content field"
        assert "isError" in result, "Response should include isError field"
        assert result["isError"] is False, "Response should indicate success"
        assert "Browser daemon started successfully" in result["content"][0].text, (
            "Response should indicate daemon started successfully"
        )


@pytest.mark.asyncio
async def test_stop_daemon_when_not_running():
    """Test that stop-daemon succeeds even when daemon isn't running."""
    # First ensure no daemon is running by checking and killing any existing processes
    result = subprocess.run(
        ["pgrep", "-f", "playwright_mcp.browser_daemon.browser_manager"],
        capture_output=True,
        text=True
    )
    if result.stdout:
        for pid in result.stdout.strip().split('\n'):
            try:
                os.kill(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
    time.sleep(1)  # Wait for processes to terminate

    # Try to stop daemon when we know none is running
    async with TestClient() as client:
        result = await client.call_tool("stop-daemon", {})
        
        # Check response format follows MCP protocol
        assert "content" in result, "Response should include content field"
        assert "isError" in result, "Response should include isError field"
        assert result["isError"] is False, "Response should indicate success"
        assert "No running daemon found" in result["content"][0].text, (
            "Response should indicate no daemon was running"
        )


@pytest.mark.asyncio
async def test_start_navigate_stop_cycle():
    """Test a full cycle of starting daemon, navigating to a page, and stopping."""
    # First ensure daemon is stopped
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'stop-daemon', '--tool-args', '{}'],
        capture_output=True,
        text=True
    )
    time.sleep(1)
    
    async with TestClient() as client:
        # Start the daemon
        start_result = await client.call_tool("start-daemon", {})
        assert "content" in start_result, "Start response should include content field"
        assert "isError" in start_result, "Start response should include isError field"
        assert start_result["isError"] is False, "Start response should indicate success"
        # Accept either message since both indicate the daemon is running
        assert any(msg in start_result["content"][0].text for msg in [
            "Browser daemon started successfully",
            "Browser daemon is already running"
        ]), "Response should indicate daemon is running"
        
        # Navigate to a page
        nav_result = await client.call_tool(
            "navigate",
            {"url": "https://example.com", "wait_until": "networkidle"}
        )
        
        # Handle both old and new response formats
        if "content" in nav_result:
            # New format
            assert "isError" in nav_result, "Navigation response should include isError field"
            assert nav_result["isError"] is False, "Navigation response should indicate success"
            nav_data = eval(nav_result["content"][0].text)
        else:
            # Old format
            assert "result" in nav_result, "Navigation response should include result field"
            nav_data = eval(nav_result["result"])
        
        # Check navigation data
        assert "session_id" in nav_data, "Response should include session ID"
        assert "page_id" in nav_data, "Response should include page ID"
        assert nav_data["created_session"] is True, "Should indicate new session was created"
        assert nav_data["created_page"] is True, "Should indicate new page was created"
        
        # Stop the daemon
        stop_result = await client.call_tool("stop-daemon", {})
        assert "content" in stop_result, "Stop response should include content field"
        assert "isError" in stop_result, "Stop response should include isError field"
        assert stop_result["isError"] is False, "Stop response should indicate success"
        # Accept either message since both indicate success
        assert any(msg in stop_result["content"][0].text for msg in [
            "Browser daemon stopped successfully",
            "No running daemon found"
        ]), "Response should indicate daemon is not running or was stopped" 