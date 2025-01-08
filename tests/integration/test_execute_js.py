"""Integration tests for the execute-js functionality."""
import subprocess
import pytest
import time
import json
import re
import ast


@pytest.fixture(scope="module")
def daemon():
    """Start and stop the browser daemon for tests."""
    # First stop any existing daemon
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', '--tool', 'stop-daemon', 'call-tool'],
        capture_output=True,
        text=True
    )
    time.sleep(1)  # Wait for cleanup
    
    # Start the daemon
    start_result = subprocess.run(
        ['mcp-cli', '--server', 'playwright', '--tool', 'start-daemon', 'call-tool'],
        capture_output=True,
        text=True
    )
    assert start_result.returncode == 0, "Start daemon command should succeed"
    assert "Browser daemon started successfully" in start_result.stdout
    time.sleep(1)  # Give daemon time to fully start
    
    yield
    
    # Cleanup
    subprocess.run(
        ['mcp-cli', '--server', 'playwright', '--tool', 'stop-daemon', 'call-tool'],
        capture_output=True,
        text=True
    )


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


@pytest.fixture
def browser_page(daemon):
    """Create a browser session and page, navigate to a test site, and clean up after."""
    # Navigate to create a session and page
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         'call-tool', '--tool', 'navigate',
         '--tool-args', '{"url": "https://example.com"}'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Navigation should succeed"
    output = clean_output(result.stdout)
    
    # Extract the response text from the list format
    response_text = output.strip("[]")
    
    # First parse the outer response using ast.literal_eval
    try:
        response = ast.literal_eval(response_text)
        # Then parse the inner JSON text
        data = json.loads(response["text"])
    except (ValueError, SyntaxError, json.JSONDecodeError) as e:
        pytest.fail(f"Failed to parse response: {response_text}\nError: {e}")
    
    assert "session_id" in data, "Response should include session ID"
    assert "page_id" in data, "Response should include page ID"
    
    return {"session_id": data["session_id"], "page_id": data["page_id"]}


def test_execute_simple_js(browser_page):
    """Test executing a simple JavaScript expression."""
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         'call-tool', '--tool', 'execute-js',
         '--tool-args', (
             f'{{"session_id": "{browser_page["session_id"]}", '
             f'"page_id": "{browser_page["page_id"]}", '
             f'"script": "document.title"}}'
         )],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "JavaScript execution should succeed"
    output = clean_output(result.stdout)
    assert "Example Domain" in output, "Should return the page title"


def test_execute_complex_js(browser_page):
    """Test executing a more complex JavaScript function that interacts with the DOM."""
    script = """() => {
        const elements = Array.from(document.querySelectorAll('*'));
        return {
            totalElements: elements.length,
            elementTypes: elements.reduce((acc, el) => {
                const tag = el.tagName.toLowerCase();
                acc[tag] = (acc[tag] || 0) + 1;
                return acc;
            }, {})
        };
    }"""
    
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         'call-tool', '--tool', 'execute-js',
         '--tool-args', (
             f'{{"session_id": "{browser_page["session_id"]}", '
             f'"page_id": "{browser_page["page_id"]}", '
             f'"script": {json.dumps(script)}}}'
         )],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "JavaScript execution should succeed"
    output = clean_output(result.stdout)
    
    # Verify we got a structured result with element counts
    assert "totalElements" in output, "Should include total element count"
    assert "elementTypes" in output, "Should include element type breakdown"
    assert "html" in output.lower(), "Should include HTML tag"
    assert "body" in output.lower(), "Should include BODY tag"


def test_execute_js_with_invalid_session(browser_page):
    """Test executing JavaScript with an invalid session ID."""
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         'call-tool', '--tool', 'execute-js',
         '--tool-args', json.dumps({
             "session_id": "invalid_session",
             "page_id": browser_page["page_id"],
             "script": "document.title"
         })],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Command should complete"
    output = clean_output(result.stdout)
    assert "No browser session found" in output, "Should indicate invalid session"


def test_execute_js_with_invalid_page(browser_page):
    """Test executing JavaScript with an invalid page ID."""
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         'call-tool', '--tool', 'execute-js',
         '--tool-args', json.dumps({
             "session_id": browser_page["session_id"],
             "page_id": "invalid_page",
             "script": "document.title"
         })],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Command should complete"
    output = clean_output(result.stdout)
    assert "No page found" in output, "Should indicate invalid page"


def test_execute_invalid_js(browser_page):
    """Test executing invalid JavaScript code."""
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         'call-tool', '--tool', 'execute-js',
         '--tool-args', json.dumps({
             "session_id": browser_page["session_id"],
             "page_id": browser_page["page_id"],
             "script": "this.is.invalid.code"
         })],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Command should complete"
    output = clean_output(result.stdout)
    assert "error" in output.lower(), "Should indicate JavaScript error" 