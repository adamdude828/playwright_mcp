"""Integration tests for the AI agent functionality."""
import pytest
import asyncio
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
    result = await client.call_tool("navigate", {
        "url": "https://example.com",
        "headless": False
    })
    
    # Parse the nested response data
    response_data = json.loads(result[0].text)
    
    yield {
        "session_id": response_data["session_id"],
        "page_id": response_data["page_id"]
    }
    
    # Cleanup
    await client.call_tool("close-browser", {"session_id": response_data["session_id"]})


@pytest.mark.asyncio
async def test_ai_agent_analyze_page(client, browser_page):
    """Test AI agent analyzing a page's content."""
    # Start an AI agent job
    result = await client.call_tool("ai-agent", {
        "page_id": browser_page["page_id"],
        "query": "What is the main heading on this page?"
    })
    
    # Parse the response to get job ID
    response_data = json.loads(result[0].text)
    assert "job_id" in response_data, "Response should contain a job ID"
    assert "error" not in response_data, f"Should not get error starting job: {response_data.get('error')}"
    job_id = response_data["job_id"]
    
    # Get the result (may need to retry a few times)
    max_retries = 5
    for _ in range(max_retries):
        result = await client.call_tool("get-ai-result", {
            "job_id": job_id
        })
        response_data = json.loads(result[0].text)
        
        if response_data["status"] == "completed":
            break
            
        if response_data["status"] == "error":
            assert False, f"Job failed with error: {response_data.get('error')}"
            
        await asyncio.sleep(1)
    
    # Verify the result
    assert response_data["status"] == "completed", f"Job did not complete successfully: {response_data}"
    assert response_data["result"] is not None, "Result should not be None when completed"
    assert isinstance(response_data["result"], str), "Result should be a string"
    assert len(response_data["result"]) > 0, "Result should not be empty"


@pytest.mark.asyncio
async def test_ai_agent_invalid_page(client):
    """Test AI agent with invalid page ID."""
    result = await client.call_tool("ai-agent", {
        "page_id": "invalid_page_id",
        "query": "What is on this page?"
    })
    
    # Parse the response
    response_data = json.loads(result[0].text)
    assert "job_id" in response_data, "Response should contain a job ID"
    job_id = response_data["job_id"]
    
    # Get the result
    result = await client.call_tool("get-ai-result", {
        "job_id": job_id
    })
    response_data = json.loads(result[0].text)
    
    # Should fail with an error about invalid page
    assert response_data["status"] == "error", "Should fail with invalid page"
    assert response_data["result"] is None, "Result should be None on error"


@pytest.mark.asyncio
async def test_ai_agent_missing_query(client, browser_page):
    """Test AI agent with missing query."""
    result = await client.call_tool("ai-agent", {
        "page_id": browser_page["page_id"]
    })
    
    # Should fail with missing query error
    response_data = json.loads(result[0].text)
    assert "error" in response_data, "Should fail with missing query error"


@pytest.mark.asyncio
async def test_get_result_invalid_job(client):
    """Test getting result for invalid job ID."""
    result = await client.call_tool("get-ai-result", {
        "job_id": "invalid_job_id"
    })
    
    # Should fail with job not found error
    response_data = json.loads(result[0].text)
    assert response_data["status"] == "error", "Should fail with job not found"
    assert response_data["result"] is None, "Result should be None for invalid job" 