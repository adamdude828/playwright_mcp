"""Tests for page analysis functionality."""
import pytest
from tests.utils.test_client import TestClient
import re


@pytest.fixture
async def client():
    """Create a test client."""
    async with TestClient() as client:
        yield client


def extract_page_id(response: dict) -> str:
    """Extract page ID from navigation response text."""
    text = response["content"][0].text
    match = re.search(r"Page ID: (page_\d+)", text)
    if not match:
        raise ValueError("Could not find page ID in response")
    return match.group(1)


@pytest.mark.skip(reason="Skipping until response format is updated")
async def test_analyze_simple_page(client):
    """Test analyzing a simple page with known elements."""
    # First navigate to a simple page
    nav_response = await client.call_tool(
        "navigate",
        {
            "url": "https://example.com",
            "wait_until": "networkidle"
        }
    )
    page_id = extract_page_id(nav_response)
    
    # Then analyze it
    analyze_response = await client.call_tool(
        "analyze-page",
        {"page_id": page_id}
    )
    assert not analyze_response.get("isError"), f"Analysis failed: {analyze_response}"
    
    # Verify response contains expected information
    text = analyze_response["content"][0].text
    assert "links found" in text.lower(), "Response should mention links"
    assert "buttons found" in text.lower(), "Response should mention buttons"
    assert "form elements found" in text.lower(), "Response should mention form elements"


@pytest.mark.skip(reason="Skipping until response format is updated")
async def test_analyze_nonexistent_page(client):
    """Test analyzing a page that hasn't been navigated to."""
    response = await client.call_tool(
        "analyze-page",
        {"page_id": "nonexistent_page_id"}
    )
    assert response.get("isError"), "Expected error response for nonexistent page"
    assert "no page found" in response["content"][0].text.lower(), "Error should mention page not found"


@pytest.mark.skip(reason="Skipping until response format is updated")
async def test_analyze_complex_page(client):
    """Test analyzing a page with various interactive elements."""
    # Navigate to a page with forms and buttons
    nav_response = await client.call_tool(
        "navigate",
        {
            "url": "https://www.thepointsguy.com",
            "wait_until": "networkidle"
        }
    )
    page_id = extract_page_id(nav_response)
    
    # Analyze the page
    analyze_response = await client.call_tool(
        "analyze-page",
        {"page_id": page_id}
    )
    assert not analyze_response.get("isError"), f"Analysis failed: {analyze_response}"
    
    # Verify response contains expected information
    text = analyze_response["content"][0].text
    assert "links found" in text.lower(), "Response should mention links"
    assert "buttons found" in text.lower(), "Response should mention buttons" 