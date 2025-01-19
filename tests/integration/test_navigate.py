import re
import pytest
import json
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


@pytest.mark.anyio
async def test_navigate_returns_session_and_page_ids():
    """Test that navigate command returns both session and page IDs."""
    client = TestClient()
    await client.__aenter__()
    try:
        # First ensure daemon is started
        await client.call_tool("start-daemon", {})
        
        # Navigate to a page
        result = await client.call_tool(
            "navigate",
            {"url": "https://example.com"}
        )
        
        # Check response format
        assert result.isError is False, "Result should not be an error"
        assert len(result.content) > 0, "Result should not be empty"
        assert result.content[0].type == "resource", "Content should be resource type"
        
        # Parse the response data
        data = json.loads(result.content[0].resource.text)
        
        # Verify response contains session and page IDs
        assert 'session_id' in data, "Response should include session ID"
        assert 'page_id' in data, "Response should include page ID"
        assert 'chromium_' in data['session_id'], "Session ID should be for chromium browser"
    finally:
        # Clean up
        await client.call_tool("stop-daemon", {})
        await client.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_navigate_reuses_session():
    """Test that navigate command reuses an existing session."""
    client = TestClient()
    await client.__aenter__()
    try:
        # Start daemon
        await client.call_tool("start-daemon", {})
        
        # First navigation to get a session ID
        result = await client.call_tool(
            "navigate",
            {"url": "https://example.com"}
        )
        
        # Check response format
        assert result.isError is False, "Result should not be an error"
        assert len(result.content) > 0, "Result should not be empty"
        assert result.content[0].type == "resource", "Content should be resource type"
        
        # Parse the response data
        data = json.loads(result.content[0].resource.text)
        
        # Get session ID from first navigation
        assert 'session_id' in data, "Response should include session ID"
        session_id = data['session_id']
        assert data['created_session'] is True, "First navigation should create new session"
        
        # Second navigation using the same session ID
        result = await client.call_tool(
            "navigate",
            {
                "url": "https://google.com",
                "session_id": session_id
            }
        )
        
        # Check response format
        assert result.isError is False, "Result should not be an error"
        assert len(result.content) > 0, "Result should not be empty"
        assert result.content[0].type == "resource", "Content should be resource type"
        
        # Parse the response data
        data = json.loads(result.content[0].resource.text)
        
        # Verify session was reused
        assert data['session_id'] == session_id, "Should reuse the same session ID"
        assert data['created_session'] is False, "Should not create new session"
        assert data['created_page'] is True, "Should create new page"
    finally:
        # Clean up
        await client.call_tool("stop-daemon", {})
        await client.__aexit__(None, None, None) 