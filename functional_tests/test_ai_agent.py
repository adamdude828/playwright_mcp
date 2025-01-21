"""Test the AI agent functionality."""
import asyncio
import json
from tests.utils.test_client import TestClient


async def main():
    """Test AI agent functionality."""
    async with TestClient() as client:
        # Start daemon
        result = await client.call_tool("start-daemon", {})
        print("\nDaemon start result:", result.content[0].text)
        
        # Navigate to test URL
        nav_result = await client.call_tool("navigate", {"url": "https://example.com"})
        resource = nav_result.content[0].resource
        data = json.loads(resource.text)
        session_id = data["session_id"]
        page_id = data["page_id"]
        print("\nNavigate response:")
        print("  session_id:", session_id)
        print("  page_id:", page_id)
        
        # Run AI agent query
        agent_result = await client.call_tool("ai-agent", {
            "page_id": page_id,
            "query": "What is the text of the main heading (h1) on this page?",
            "max_actions": 2  # Limit actions for test
        })
        resource = agent_result.content[0].resource
        data = json.loads(resource.text)
        job_id = data["job_id"]
        print("\nAI Agent response:", agent_result)
        print("  job_id:", job_id)
        
        # Wait 30 seconds before checking result
        print("\nWaiting 30 seconds for AI agent to complete...")
        await asyncio.sleep(30)
        
        # Get the result
        result = await client.call_tool("get-ai-result", {"job_id": job_id})
        print("\nGet AI result response:", result)
        
        # Handle both TextContent and EmbeddedResource responses
        content = result.content[0]
        if hasattr(content, 'resource'):
            data = json.loads(content.resource.text)
            status = data.get("status")
            print("\nJob status:", status)
            if status == "completed":
                print("Final result:", data.get("result", "No result"))
            elif status == "error":
                print("Error:", data.get("error", "Unknown error"))
        else:
            print("\nError:", content.text)
                
        # Stop daemon
        stop_result = await client.call_tool("stop-daemon", {})
        print("\nDaemon stop result:", stop_result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main()) 