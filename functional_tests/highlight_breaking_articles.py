"""Script to test highlighting breaking articles on thepointsguy.com."""
import asyncio
import json
import os
from datetime import datetime
from tests.utils.test_client import TestClient


async def main():
    """Start daemon and test highlighting breaking articles."""
    async with TestClient() as client:
        # Start daemon
        result = await client.call_tool("start-daemon", {})
        print("\nDaemon start result:", result.content[0].text)
        
        # Navigate to The Points Guy
        nav_result = await client.call_tool("navigate", {
            "url": "https://thepointsguy.com",
            "wait_until": "networkidle"  # Wait for network to be idle
        })
        data = json.loads(nav_result.content[0].resource.text)
        session_id = data["session_id"]
        page_id = data["page_id"]
        
        print("\nNavigated to thepointsguy.com")
        print("Session ID:", session_id)
        print("Page ID:", page_id)
        
        # Create timestamp for unique screenshot name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "screen_shots",
            f"breaking_articles_{timestamp}.png"
        ))
        
        # Highlight breaking articles
        highlight_result = await client.call_tool("highlight-element", {
            "page_id": page_id,
            "selector": ".breakingArticles",
            "color": "#FF0000",  # Red highlight
            "duration": 2000  # 2 seconds
        })
        
        print("\nHighlight Result:")
        if highlight_result.isError:
            print("Error:", highlight_result.content[0].text)
        else:
            print(highlight_result.content[0].text)
            
            # Take a screenshot while the highlight is visible
            await client.call_tool("screenshot", {
                "page_id": page_id,
                "path": screenshot_path,
                "full_page": False
            })
            print(f"\nScreenshot saved to: {screenshot_path}")
        
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