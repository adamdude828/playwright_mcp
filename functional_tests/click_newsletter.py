"""Script to test clicking newsletter subscribe trigger on thepointsguy.com."""
import asyncio
import json
from tests.utils.test_client import TestClient


async def main():
    """Start daemon and test clicking newsletter subscribe trigger."""
    async with TestClient() as client:
        # Start daemon
        result = await client.call_tool("start-daemon", {})
        print("\nDaemon start result:", result.content[0].text)
        
        # Navigate to The Points Guy with non-headless browser
        nav_result = await client.call_tool("navigate", {
            "url": "https://thepointsguy.com",
            "wait_until": "networkidle",  # Wait for network to be idle
            "headless": False  # Run in non-headless mode
        })
        data = json.loads(nav_result.content[0].resource.text)
        session_id = data["session_id"]
        page_id = data["page_id"]
        
        print("\nNavigated to thepointsguy.com")
        print("Session ID:", session_id)
        print("Page ID:", page_id)
        
        # Add delay to ensure page is fully loaded
        print("\nWaiting for page to settle...")
        await asyncio.sleep(5)
        
        # Click the newsletter subscribe trigger
        click_result = await client.call_tool("interact-dom", {
            "page_id": page_id,
            "selector": '[data-testid="newsletterSubscribeTrigger"]',
            "action": "click"
        })
        
        print("\nClick Result:")
        if click_result.isError:
            print("Error:", click_result.content[0].text)
        else:
            print(click_result.content[0].text)
            
        # Add delay after click to see the result
        print("\nWaiting to see the click result...")
        await asyncio.sleep(5)
        
        # Clean up by closing the tab
        await client.call_tool("close-tab", {
            "session_id": session_id,
            "page_id": page_id
        })
        
        # Stop daemon
        stop_result = await client.call_tool("stop-daemon", {})
        print("\nDaemon stop result:", stop_result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main()) 