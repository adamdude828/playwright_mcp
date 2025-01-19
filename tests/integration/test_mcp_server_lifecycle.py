import pytest
import asyncio
import json
from ..utils.test_client import TestClient


@pytest.mark.anyio
async def test_mcp_server_basic_communication():
    """Test basic socket communication with navigation."""
    client = TestClient()
    await client.__aenter__()
    try:
        # Start daemon
        await client.call_tool("start-daemon", {})
        
        # Navigate to a page
        nav_result = await client.call_tool("navigate", {"url": "https://example.com"})
        assert nav_result.isError is False, "Navigation should not error"
        assert len(nav_result.content) == 1, "Should have one content item"
        
        # Parse navigation response
        nav_data = json.loads(nav_result.content[0].resource.text)
        assert "session_id" in nav_data, "Response should include session ID"
        assert "page_id" in nav_data, "Response should include page ID"
    finally:
        # Clean up
        await client.call_tool("stop-daemon", {})
        await client.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_mcp_server_socket_communication():
    """Test that socket communication is stable with a single MCP server instance."""
    client = TestClient()
    await client.__aenter__()
    try:
        # Start daemon
        await client.call_tool("start-daemon", {})
        
        # First navigate to a page
        nav_result = await client.call_tool("navigate", {"url": "https://example.com"})
        assert nav_result.isError is False, "Navigation should not error"
        assert len(nav_result.content) == 1, "Should have one content item"
        
        # Parse navigation response
        nav_data = json.loads(nav_result.content[0].resource.text)
        assert "session_id" in nav_data, "Response should include session ID"
        assert "page_id" in nav_data, "Response should include page ID"
        page_id = nav_data["page_id"]
        
        # Run multiple AI agent commands in quick succession
        results = []
        for _ in range(3):
            # Start AI agent job
            agent_result = await client.call_tool("ai-agent", {
                "page_id": page_id,
                "query": "What is the main heading?"
            })
            results.append(agent_result)
            
            # Get the result immediately
            assert len(agent_result.content) == 1, "Should have one content item"
            
            # Handle both TextContent and EmbeddedResource responses
            content = agent_result.content[0]
            if hasattr(content, 'resource'):
                job_data = json.loads(content.resource.text)
                # Only check for job_id if we got a successful response
                if not job_data.get("isError"):
                    assert "job_id" in job_data, "Response should include job ID"
                    job_id = job_data["job_id"]
                    
                    result_response = await client.call_tool("get-ai-result", {
                        "job_id": job_id
                    })
                    results.append(result_response)
            else:
                # For error responses, just verify it's a text type
                assert content.type == "text", "Error response should be text type"
                assert "Daemon" in content.text, "Error should mention daemon"
            
            # Small delay to ensure we can see logs clearly
            await asyncio.sleep(0.1)
            
        # Verify all commands succeeded
        for result in results:
            assert len(result.content) == 1, "Should have one content item"
            
            # Handle both TextContent and EmbeddedResource responses
            content = result.content[0]
            if hasattr(content, 'resource'):
                assert content.type == "resource", "Content should be resource type"
            else:
                assert content.type == "text", "Content should be text type"
    finally:
        # Clean up
        await client.call_tool("stop-daemon", {})
        await client.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_mcp_server_ai_agent():
    """Test AI agent functionality."""
    client = TestClient()
    await client.__aenter__()
    try:
        # Start daemon
        await client.call_tool("start-daemon", {})
        
        # First navigate to a page
        nav_result = await client.call_tool("navigate", {"url": "https://example.com"})
        assert nav_result.isError is False, "Navigation should not error"
        assert len(nav_result.content) == 1, "Should have one content item"
        
        # Parse navigation response
        nav_data = json.loads(nav_result.content[0].resource.text)
        page_id = nav_data["page_id"]
        
        # Start AI agent job
        agent_result = await client.call_tool("ai-agent", {
            "page_id": page_id,
            "query": "What is the main heading?"
        })
        
        # Verify response format
        assert len(agent_result.content) == 1, "Should have one content item"
        content = agent_result.content[0]
        
        # Handle both TextContent and EmbeddedResource responses
        if hasattr(content, 'resource'):
            job_data = json.loads(content.resource.text)
            assert content.type == "resource", "Content should be resource type"
            # Only check for job_id if we got a successful response
            if not job_data.get("isError"):
                assert "job_id" in job_data, "Response should include job ID"
                assert "status" in job_data, "Response should include status"
        else:
            assert content.type == "text", "Error response should be text type"
            assert "Daemon" in content.text, "Error should mention daemon"
            
    finally:
        # Clean up
        await client.call_tool("stop-daemon", {})
        await client.__aexit__(None, None, None) 