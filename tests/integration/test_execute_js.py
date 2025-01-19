"""Integration tests for the execute-js functionality."""
import pytest
from tests.utils.test_client import TestClient
import json


@pytest.fixture
async def client():
    """Create a test client."""
    async with TestClient() as client:
        # Start the daemon
        await client.call_tool("start-daemon", {})
        try:
            yield client
        finally:
            # Stop the daemon before the context manager exits
            await client.call_tool("stop-daemon", {})


@pytest.fixture
async def browser_page(client):
    """Create a browser and page for testing."""
    # Navigate to create a session and page
    result = await client.call_tool("navigate", {"url": "about:blank"})
    print("\nRaw navigate result:", result.content[0].resource.text)
    
    # Parse the response data
    response_data = json.loads(result.content[0].resource.text)
    
    yield {
        "session_id": response_data['session_id'],
        "page_id": response_data['page_id']
    }
    
    # Cleanup
    await client.call_tool("close-browser", {"session_id": response_data['session_id']})


@pytest.mark.anyio
async def test_execute_simple_js():
    """Test executing simple JavaScript code."""
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
        result = await client.call_tool("execute-js", {
            "session_id": browser_page["session_id"],
            "page_id": browser_page["page_id"],
            "script": "() => 42"  # Wrap in arrow function
        })

        # Validate the response
        assert len(result.content) == 1, "Expected single TextContent result"
        content = result.content[0].text
        assert content == "42", "Expected result to be 42"
        
        # Clean up browser
        await client.call_tool("close-browser", {"session_id": browser_page["session_id"]})
        
        # Stop daemon before client exits
        await client.call_tool("stop-daemon", {})
    finally:
        await client.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_execute_complex_js():
    """Test executing more complex JavaScript code."""
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
        
        script = """() => {
            const obj = {
                name: 'test',
                value: 42,
                nested: {
                    array: [1, 2, 3]
                }
            };
            return obj.nested.array[1];
        }"""
        
        result = await client.call_tool("execute-js", {
            "session_id": browser_page["session_id"],
            "page_id": browser_page["page_id"],
            "script": script
        })
        
        # Validate the response
        assert len(result.content) == 1, "Expected single TextContent result"
        content = result.content[0].text
        assert content == "2", "Expected result to be 2"
        
        # Clean up browser
        await client.call_tool("close-browser", {"session_id": browser_page["session_id"]})
        
        # Stop daemon before client exits
        await client.call_tool("stop-daemon", {})
    finally:
        await client.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_execute_js_with_invalid_session():
    """Test executing JavaScript with an invalid session ID."""
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
        
        # Test with invalid session
        result = await client.call_tool("execute-js", {
            "session_id": "invalid-session",
            "page_id": browser_page["page_id"],
            "script": "() => 2 + 2"
        })
        
        # Validate error message
        assert len(result.content) == 1, "Expected single TextContent result"
        content = result.content[0].text
        assert "No browser session found" in content, \
            f"Expected 'No browser session found' in response, got: {content}"
        
        # Clean up browser
        await client.call_tool("close-browser", {"session_id": browser_page["session_id"]})
        
        # Stop daemon before client exits
        await client.call_tool("stop-daemon", {})
    finally:
        await client.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_execute_js_with_invalid_page():
    """Test executing JavaScript with an invalid page ID."""
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
        
        # Test with invalid page
        result = await client.call_tool("execute-js", {
            "session_id": browser_page["session_id"],
            "page_id": "invalid-page",
            "script": "() => 2 + 2"
        })
        
        # Validate error message
        assert len(result.content) == 1, "Expected single TextContent result"
        content = result.content[0].text
        assert "No page found" in content, \
            f"Expected 'No page found' in response, got: {content}"
        
        # Clean up browser
        await client.call_tool("close-browser", {"session_id": browser_page["session_id"]})
        
        # Stop daemon before client exits
        await client.call_tool("stop-daemon", {})
    finally:
        await client.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_execute_invalid_js():
    """Test executing invalid JavaScript code."""
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
        
        # Test with invalid JavaScript
        result = await client.call_tool("execute-js", {
            "session_id": browser_page["session_id"],
            "page_id": browser_page["page_id"],
            "script": "invalid javascript"
        })
        
        # Validate error message
        assert len(result.content) == 1, "Expected single TextContent result"
        content = result.content[0].text
        assert "SyntaxError" in content, \
            f"Expected SyntaxError in response, got: {content}"
        
        # Clean up browser
        await client.call_tool("close-browser", {"session_id": browser_page["session_id"]})
        
        # Stop daemon before client exits
        await client.call_tool("stop-daemon", {})
    finally:
        await client.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_start_daemon_raw_result():
    """Test starting the daemon and validate the response format."""
    async with TestClient() as client:
        result = await client.call_tool("start-daemon", {})
        print("\nRaw daemon start result:", result)
        
        # Validate result structure
        assert len(result.content) == 1, "Expected single TextContent result"
        response = result.content[0]
        assert response.type == "text", "Expected text type response"
        
        # The content should indicate either success or already running
        content = response.text
        assert "Browser daemon is already running" in content or "Browser daemon started" in content, \
            f"Unexpected response content: {content}" 