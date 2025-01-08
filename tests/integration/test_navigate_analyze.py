"""Integration tests for the navigate tool with analysis functionality."""
import subprocess
import pytest
import time
import re


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


def test_navigate_with_analysis(daemon):
    """Test navigation with page analysis on a simple static site."""
    # Navigate to a simple static site with analysis enabled
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         'call-tool', '--tool', 'navigate',
         '--tool-args', '{"url": "https://example.com", "analyze_after_navigation": true}'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Navigation should succeed"
    output = clean_output(result.stdout)
    
    # Verify we got a non-empty response with key elements
    assert output, "Output should not be empty"
    assert "Navigated successfully" in output
    assert "Tool Response" in output
    assert "anchors" in output  # Should contain analysis results


def test_navigate_without_analysis(daemon):
    """Test basic navigation without analysis."""
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         '--tool', 'navigate',
         '--tool-args', '{"url": "https://example.com", "analyze_after_navigation": false}',
         'call-tool'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Navigation should succeed"
    assert "Navigated successfully" in result.stdout


def test_navigate_invalid_url(daemon):
    """Test navigation to an invalid URL."""
    invalid_url = "https://this-is-an-invalid-url-that-does-not-exist.com"
    result = subprocess.run(
        ['mcp-cli', '--server', 'playwright',
         '--tool', 'navigate',
         '--tool-args', f'{{"url": "{invalid_url}", "analyze_after_navigation": true}}',
         'call-tool'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "Command should complete"
    assert "net::" in result.stdout  # Playwright's network error prefix 