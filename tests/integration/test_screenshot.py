"""Integration tests for the screenshot functionality."""
import subprocess
import pytest
import time
import os
import re
import json


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
    # Remove box drawing characters
    output = re.sub(r'[─│╭╮╰╯]', '', output)
    # Remove extra whitespace
    output = re.sub(r'\s+', ' ', output)
    return output.strip()


def test_navigate_with_screenshot(daemon):
    """Test navigation with screenshot capture."""
    # Create a temporary file path for the screenshot
    screenshot_path = "test_screenshot.png"
    
    try:
        result = subprocess.run(
            ['mcp-cli', '--server', 'playwright',
             '--tool', 'navigate',
             '--tool-args', f'{{"url": "https://example.com", "screenshot_path": "{screenshot_path}"}}',
             'call-tool'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Navigation should succeed"
        output = result.stdout
        
        # Extract the JSON response
        response_start = output.find('{"session_id"')
        response_end = output.find('}', response_start) + 1
        response_json = output[response_start:response_end]
        
        # Clean up the response by removing special characters
        response_json = re.sub(r'[^\x20-\x7E]', '', response_json)
        
        # Parse the response
        data = json.loads(response_json)
        
        # Verify we got a non-empty response with key elements
        assert data, "Response data should not be empty"
        assert 'session_id' in data, "Response should include session ID"
        assert 'page_id' in data, "Response should include page ID"
        assert 'screenshot_path' in data, "Response should include screenshot path"
        assert data['screenshot_path'] == screenshot_path, "Screenshot path should match"
        
        # Verify the screenshot file exists and has content
        assert os.path.exists(screenshot_path), "Screenshot file should exist"
        assert os.path.getsize(screenshot_path) > 0, "Screenshot should not be empty"
        
    finally:
        # Cleanup: Remove the screenshot file
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)


def test_navigate_with_invalid_screenshot_path(daemon):
    """Test navigation with an invalid screenshot path."""
    # Try to save to a non-existent directory
    invalid_path = "/nonexistent/directory/screenshot.png"
    
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         'call-tool', '--tool', 'navigate',
         '--tool-args', f'{{"url": "https://example.com", "screenshot_path": "{invalid_path}"}}'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Command should complete"
    output = clean_output(result.stdout)
    # The error message contains the OS-level error about read-only or non-existent directory
    assert "Errno" in output, "Should indicate file system error"


def test_navigate_screenshot_with_analysis(daemon):
    """Test that screenshot and analysis can be used together."""
    screenshot_path = "test_integration_screenshot_with_analysis.png"
    
    try:
        result = subprocess.run(
            ['mcp-cli', '--server', 'playwright',
             '--tool', 'navigate',
             '--tool-args',
             f'{{"url": "https://example.com", '
             f'"screenshot_path": "{screenshot_path}", '
             f'"analyze_after_navigation": true}}',
             'call-tool'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Navigation should succeed"
        output = result.stdout
        
        # Extract the JSON response
        response_start = output.find('{"session_id"')
        response_end = output.find('"}\'') + 2  # Find the end of the JSON string
        response_json = output[response_start:response_end]
        
        # Clean up the response by removing special characters
        response_json = re.sub(r'[^\x20-\x7E]', '', response_json)
        
        # Parse the response
        data = json.loads(response_json)
        
        # Verify we got a non-empty response with key elements
        assert data, "Response data should not be empty"
        assert 'session_id' in data, "Response should include session ID"
        assert 'page_id' in data, "Response should include page ID"
        assert 'screenshot_path' in data, "Response should include screenshot path"
        assert data['screenshot_path'] == screenshot_path, "Screenshot path should match"
        assert 'analysis' in data, "Response should include analysis results"
        assert 'interactive_elements' in data['analysis'], "Analysis should include interactive elements"
        
        # Verify the screenshot file exists and has content
        assert os.path.exists(screenshot_path), "Screenshot file should exist"
        assert os.path.getsize(screenshot_path) > 0, "Screenshot should not be empty"
        
    finally:
        # Cleanup: Remove the screenshot file
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path) 