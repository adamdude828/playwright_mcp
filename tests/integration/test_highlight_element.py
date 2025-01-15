"""Integration tests for the highlight-element functionality."""
import pytest
import os
from tests.utils.test_client import TestClient


@pytest.fixture(scope="module")
async def client():
    """Create and yield a test client."""
    async with TestClient() as client:
        # Start the daemon
        await client.call_tool("start-daemon", {})
        yield client
        # Stop the daemon
        await client.call_tool("stop-daemon", {})


@pytest.fixture
async def browser_page(client):
    """Create a browser and page for testing."""
    # Navigate to create a session and page
    result = await client.call_tool("navigate", {"url": "about:blank"})
    
    # Parse the nested response data
    response_data = eval(result[0].text)
    
    yield {
        "session_id": response_data["session_id"],
        "page_id": response_data["page_id"]
    }
    
    # Cleanup
    await client.call_tool("close-browser", {"session_id": response_data["session_id"]})


@pytest.mark.asyncio
async def test_highlight_element_generates_screenshot(client, browser_page, tmp_path):
    """Test that highlight-element can generate a screenshot without error."""
    # Create a test element to highlight
    await client.call_tool("execute-js", {
        "session_id": browser_page["session_id"],
        "page_id": browser_page["page_id"],
        "script": """
            const div = document.createElement('div');
            div.id = 'test-element';
            div.textContent = 'Test Element';
            document.body.appendChild(div);
        """
    })
    
    # Set up screenshot path
    screenshot_path = tmp_path / "test_highlight.png"
    
    # Highlight the element and take screenshot
    await client.call_tool("highlight-element", {
        "page_id": browser_page["page_id"],
        "selector": "#test-element",
        "save_path": str(screenshot_path)
    })
    
    # Verify the screenshot was created
    assert os.path.exists(screenshot_path), "Screenshot file was not created"
    assert os.path.getsize(screenshot_path) > 0, "Screenshot file is empty"
    
    # Clean up
    os.unlink(screenshot_path) 