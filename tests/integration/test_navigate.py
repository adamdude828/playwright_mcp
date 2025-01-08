import subprocess
import time
import re
import json


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


def test_navigate_returns_session_and_page_ids():
    """Test that navigate command returns both session and page IDs."""
    # First ensure daemon is started
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', '--tool', 'start-daemon', 'call-tool'],
        capture_output=True,
        text=True
    )
    time.sleep(1)
    
    # Navigate to a page
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         '--tool', 'navigate',
         '--tool-args', '{"url": "https://example.com"}',
         'call-tool'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Navigation should succeed"
    
    # Clean and parse the output
    output = clean_output(result.stdout)
    response = eval(output.strip('[]'))
    data = json.loads(response['text'])
    
    # Verify response contains session and page IDs
    assert 'session_id' in data, "Response should include session ID"
    assert 'page_id' in data, "Response should include page ID"
    assert 'chromium_' in data['session_id'], "Session ID should be for chromium browser"
    
    # Clean up
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', '--tool', 'stop-daemon', 'call-tool'],
        capture_output=True,
        text=True
    )


def test_navigate_reuses_session():
    """Test that navigate command reuses an existing session."""
    # Start daemon
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', '--tool', 'start-daemon', 'call-tool'],
        capture_output=True,
        text=True
    )
    time.sleep(1)
    
    # First navigation to get a session ID
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         '--tool', 'navigate',
         '--tool-args', '{"url": "https://example.com"}',
         'call-tool'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "First navigation should succeed"
    
    # Clean and parse the output
    output = clean_output(result.stdout)
    response = eval(output.strip('[]'))
    data = json.loads(response['text'])
    
    # Get session ID from first navigation
    assert 'session_id' in data, "Response should include session ID"
    session_id = data['session_id']
    assert data['created_session'] is True, "First navigation should create new session"
    
    # Second navigation using the same session ID
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         '--tool', 'navigate',
         '--tool-args', f'{{"url": "https://google.com", "session_id": "{session_id}"}}',
         'call-tool'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Second navigation should succeed"
    
    # Clean and parse the output
    output = clean_output(result.stdout)
    response = eval(output.strip('[]'))
    data = json.loads(response['text'])
    
    # Verify session was reused
    assert data['session_id'] == session_id, "Should reuse the same session ID"
    assert data['created_session'] is False, "Should not create new session"
    assert data['created_page'] is True, "Should create new page"
    
    # Clean up
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', '--tool', 'stop-daemon', 'call-tool'],
        capture_output=True,
        text=True
    ) 