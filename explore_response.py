"""Script to explore TestClient response format."""
import asyncio
import json
from tests.utils.test_client import TestClient


async def main():
    """Start daemon and navigate to test URL."""
    async with TestClient() as client:
        # Start daemon
        result = await client.call_tool("start-daemon", {})
        print("\nDaemon start result:", result.content[0].text)
        
        # Navigate to test URL
        nav_result = await client.call_tool("navigate", {"url": "about:blank"})
        
        # Get the navigation data directly from the embedded resource
        resource = nav_result.content[0].resource
        data = json.loads(resource.text)
        
        print("\nNavigate response:")
        print("  session_id:", data["session_id"])
        print("  page_id:", data["page_id"])
        print("  created_session:", data["created_session"])
        print("  created_page:", data["created_page"])
        
        # Execute JavaScript
        js_result = await client.call_tool("execute-js", {
            "session_id": data["session_id"],
            "page_id": data["page_id"],
            "script": "() => 42"  # Wrap in arrow function
        })
        print("\nExecute JS response:")
        print("  result:", js_result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main()) 