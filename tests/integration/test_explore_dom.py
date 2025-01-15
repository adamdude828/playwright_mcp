"""Tests for DOM exploration functionality."""
import pytest
from tests.utils.test_client import TestClient


@pytest.fixture
async def client():
    """Create a test client."""
    async with TestClient() as client:
        # Start the daemon first
        await client.call_tool("start-daemon", {})
        yield client


def extract_page_id(response: list) -> str:
    """Extract page ID from navigation response text."""
    data = eval(response[0].text)
    return data["page_id"]


async def test_explore_simple_page(client):
    """Test exploring a simple page with known structure."""
    # First navigate to a simple page
    nav_response = await client.call_tool(
        "navigate",
        {
            "url": "https://example.com",
            "wait_until": "networkidle"
        }
    )
    page_id = extract_page_id(nav_response)
    
    # Then explore its DOM
    explore_response = await client.call_tool(
        "explore-dom",
        {
            "page_id": page_id,
            "selector": "body"  # Start from body
        }
    )
    
    # Verify response format and content
    text = explore_response[0].text
    assert text.startswith("Element: body"), "Response should start with body element"
    assert "div" in text, "Response should contain div elements"
    assert "children)" in text, "Response should indicate child counts" 