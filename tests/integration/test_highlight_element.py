"""Integration tests for the highlight-element functionality."""
import pytest
import os
import json
from tests.utils.test_client import TestClient


@pytest.mark.anyio
async def test_highlight_element_generates_screenshot(tmp_path):
    """Test that highlight-element can generate a screenshot without error."""
    client = TestClient()
    await client.__aenter__()
    try:
        # Start the daemon
        await client.call_tool("start-daemon", {})
        
        # Navigate to create a session and page
        result = await client.call_tool("navigate", {"url": "about:blank"})
        print("\nRaw navigate result:", result.content[0].resource.text)
        
        # Parse the response data
        response_data = json.loads(result.content[0].resource.text)
        browser_page = {
            "session_id": response_data['session_id'],
            "page_id": response_data['page_id']
        }
        
        print("\nBrowser page:", browser_page)
        
        # Create a test element to highlight
        await client.call_tool("execute-js", {
            "session_id": browser_page["session_id"],
            "page_id": browser_page["page_id"],
            "script": """() => {
                const div = document.createElement('div');
                div.id = 'test-element';
                div.textContent = 'Test Element';
                document.body.appendChild(div);
            }"""
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
        
        # Clean up screenshot
        os.unlink(screenshot_path)
        
        # Clean up browser
        await client.call_tool("close-tab", {
            "session_id": browser_page["session_id"],
            "page_id": browser_page["page_id"]
        })
        
        # Stop daemon before client exits
        await client.call_tool("stop-daemon", {})
    finally:
        await client.__aexit__(None, None, None) 