import pytest
import asyncio
from ..utils.test_client import TestClient


@pytest.mark.asyncio
async def test_mcp_server_socket_communication():
    """Test that socket communication is stable with a single MCP server instance."""
    
    async with TestClient() as client:
        # Start daemon
        await client.call_tool("start-daemon", {})
        
        # First navigate to a page
        nav_result = await client.call_tool("navigate", {"url": "https://example.com"})
        assert len(nav_result) == 1
        nav_response = nav_result[0]
        assert "created_session" in nav_response.text
        page_id = "page_4441812160"  # Get this from nav response
        
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
            job_response = agent_result[0]
            job_data = eval(job_response.text)  # Convert string response to dict
            job_id = job_data["job_id"]
            
            result_response = await client.call_tool("get-ai-result", {
                "job_id": job_id
            })
            results.append(result_response)
            
            # Small delay to ensure we can see logs clearly
            await asyncio.sleep(0.1)
            
        # Verify all commands succeeded
        for result in results:
            assert len(result) == 1
            response = result[0]
            assert "isError" not in response.text
            
        # Clean up
        await client.call_tool("stop-daemon", {}) 