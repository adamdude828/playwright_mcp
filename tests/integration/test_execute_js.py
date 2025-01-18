"""Integration tests for the execute-js functionality."""
import pytest
import json
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
    response_data = json.loads(result[0].text)
    
    yield {
        "session_id": response_data["session_id"],
        "page_id": response_data["page_id"]
    }
    
    # Cleanup
    await client.call_tool("close-browser", {"session_id": response_data["session_id"]})


@pytest.mark.asyncio
async def test_execute_simple_js(client, browser_page):
    """Test executing simple JavaScript code."""
    result = await client.call_tool("execute-js", {
        "session_id": browser_page["session_id"],
        "page_id": browser_page["page_id"],
        "script": "2 + 2"
    })
    
    # Get the text content from the response
    assert result[0].text == "4"


@pytest.mark.asyncio
async def test_execute_complex_js(client, browser_page):
    """Test executing more complex JavaScript code."""
    script = """
    const obj = {
        name: 'test',
        value: 42,
        nested: {
            array: [1, 2, 3]
        }
    };
    obj.nested.array[1]
    """
    
    result = await client.call_tool("execute-js", {
        "session_id": browser_page["session_id"],
        "page_id": browser_page["page_id"],
        "script": script
    })
    
    # Get the text content from the response
    assert result[0].text == "2"


@pytest.mark.asyncio
async def test_execute_js_with_invalid_session(client, browser_page):
    """Test executing JavaScript with an invalid session ID."""
    result = await client.call_tool("execute-js", {
        "session_id": "invalid-session",
        "page_id": browser_page["page_id"],
        "script": "2 + 2"
    })
    
    # Check for error in the response
    assert "No browser session found for ID: invalid-session" in result[0].text


@pytest.mark.asyncio
async def test_execute_js_with_invalid_page(client, browser_page):
    """Test executing JavaScript with an invalid page ID."""
    result = await client.call_tool("execute-js", {
        "session_id": browser_page["session_id"],
        "page_id": "invalid-page",
        "script": "2 + 2"
    })
    
    # Check for error in the response
    assert "No page found with ID: invalid-page" in result[0].text


@pytest.mark.asyncio
async def test_execute_invalid_js(client, browser_page):
    """Test executing invalid JavaScript code."""
    result = await client.call_tool("execute-js", {
        "session_id": browser_page["session_id"],
        "page_id": browser_page["page_id"],
        "script": "invalid javascript"
    })
    
    # Check for error in the response
    assert "SyntaxError: Unexpected identifier 'javascript'" in result[0].text 