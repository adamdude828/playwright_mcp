"""Tests for navigation and page analysis functionality."""
import pytest
from tests.utils.test_client import TestClient


@pytest.fixture(scope="function")
async def client():
    """Create and clean up test client."""
    async with TestClient() as client:
        # Start the daemon
        await client.call_tool("start-daemon", {})
        yield client
        # Stop the daemon
        await client.call_tool("stop-daemon", {})


@pytest.mark.asyncio
async def test_navigate_to_invalid_url(client):
    """Test that navigation to an invalid URL fails appropriately."""
    invalid_url = "https://thisisnotarealwebsite.com.fake.invalid"
    
    # Try to navigate to invalid URL
    result = await client.call_tool("navigate", {"url": invalid_url})
    
    # For navigation errors, check both isError and error message
    assert result.isError, "Response should indicate an error"
    assert "net::" in result.content[0].text, "Response should include network error"