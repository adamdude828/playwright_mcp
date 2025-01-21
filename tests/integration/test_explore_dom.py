"""Tests for DOM exploration functionality."""
import pytest
from tests.utils.test_client import TestClient
import json


@pytest.fixture
async def client():
    """Create a test client."""
    async with TestClient() as client:
        # Start the daemon first
        await client.call_tool("start-daemon", {})
        yield client


def extract_page_id(response):
    """Extract page_id from a response."""
    data = json.loads(response[0].text)
    return data["page_id"]


@pytest.mark.anyio
async def test_explore_simple_page():
    """Test exploring a simple page with known structure."""
    client = TestClient()
    await client.__aenter__()
    try:
        # Start the daemon
        await client.call_tool("start-daemon", {})
        
        # Navigate to create a session and page
        result = await client.call_tool("navigate", {"url": "https://example.com"})
        print("\nRaw navigate result:", result.content[0].resource.text)
        
        # Parse the response data
        response_data = json.loads(result.content[0].resource.text)
        browser_page = {
            "session_id": response_data['session_id'],
            "page_id": response_data['page_id']
        }
        
        print("\nBrowser page:", browser_page)
        
        # Then explore its DOM
        explore_response = await client.call_tool(
            "explore-dom",
            {
                "page_id": browser_page["page_id"],
                "selector": "body"  # Start from body
            }
        )
        
        # Verify response format and content
        assert not explore_response.isError, "Expected successful response"
        assert len(explore_response.content) == 1, "Expected single TextContent result"
        text = explore_response.content[0].text
        print("\nExplore DOM response:", text)
        assert "Element: body" in text, "Response should contain body element"
        assert "div" in text, "Response should contain div elements"
        assert "children)" in text, "Response should indicate child counts"
        
        # Clean up browser
        await client.call_tool("close-tab", {
            "session_id": browser_page["session_id"],
            "page_id": browser_page["page_id"]
        })
        
        # Stop daemon before client exits
        await client.call_tool("stop-daemon", {})
    finally:
        await client.__aexit__(None, None, None) 