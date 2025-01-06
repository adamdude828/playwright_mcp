import subprocess
import shutil
import time


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
        'analyze-page', 'close-browser', 'close-tab'
    }
    missing_tools = expected_tools - tools
    assert not missing_tools, f"Missing expected tools: {missing_tools}"


def test_navigate_without_daemon():
    """Test that trying to navigate without starting the daemon fails with appropriate error."""
    # First ensure daemon is stopped
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'stop-daemon'],
        capture_output=True,
        text=True
    )
    # Give it a moment to fully stop
    time.sleep(1)
    
    # Try to navigate without daemon running
    cmd = [
        'mcp-cli', '--server', 'playwright', 'call-tool',
        '--tool', 'navigate',
        '--tool-args', '{"url": "https://example.com"}'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # The error comes back in stdout as part of the tool response
    assert "Browser daemon is not running" in result.stdout, "Response should indicate daemon is not running"


def test_start_daemon():
    """Test that the start-daemon command works successfully."""
    # First ensure daemon is stopped
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'stop-daemon'],
        capture_output=True,
        text=True
    )
    time.sleep(1)
    
    # Start the daemon
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'start-daemon'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Start daemon command should succeed"
    assert "Browser daemon started successfully" in result.stdout, (
        "Response should indicate daemon started successfully"
    )


def test_stop_daemon_when_not_running():
    """Test that stop-daemon succeeds even when daemon isn't running."""
    # First ensure daemon is stopped
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'stop-daemon'],
        capture_output=True,
        text=True
    )
    time.sleep(1)
    
    # Try to stop it again
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'stop-daemon'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Stop daemon command should succeed even when daemon isn't running"
    assert "No running daemon found" in result.stdout, (
        "Response should indicate no daemon was running"
    )


def test_start_navigate_stop_cycle():
    """Test a full cycle of starting daemon, navigating to a page, and stopping."""
    # First ensure daemon is stopped
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'stop-daemon'],
        capture_output=True,
        text=True
    )
    time.sleep(1)
    
    # Start the daemon
    start_result = subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'start-daemon'],
        capture_output=True,
        text=True
    )
    assert start_result.returncode == 0, "Start daemon command should succeed"
    assert "Browser daemon started successfully" in start_result.stdout
    time.sleep(1)  # Give daemon time to fully start
    
    # Navigate to a page
    nav_result = subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'navigate',
         '--tool-args', '{"url": "https://example.com"}'],
        capture_output=True,
        text=True
    )
    assert nav_result.returncode == 0, "Navigation should succeed"
    assert "Navigated successfully" in nav_result.stdout
    
    # Stop the daemon
    stop_result = subprocess.run(
        ['mcp-cli', '--server', 'playwright', 'call-tool', '--tool', 'stop-daemon'],
        capture_output=True,
        text=True
    )
    assert stop_result.returncode == 0, "Stop daemon command should succeed"
    assert "Browser daemon stopped successfully" in stop_result.stdout 