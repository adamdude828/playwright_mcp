"""Script to test finding the subscribe button on The Points Guy website."""

import asyncio
import logging
from playwright.async_api import async_playwright
from playwright_mcp.browser_daemon.handlers.ai_agent import AIAgentHandler
from playwright_mcp.browser_daemon.core.session import SessionManager
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.job_store import JobStore
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.tools import create_agent

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MockDaemon:
    """Mock daemon class for testing."""
    def __init__(self):
        self.job_store = JobStore()


async def main():
    """Main function to run the test."""
    logger.info("Starting browser setup")
    async with async_playwright() as playwright:
        # Launch browser and navigate to page
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://thepointsguy.com")
        logger.info("Successfully navigated to The Points Guy")
        
        try:
            # Set up session manager and store page
            session_manager = SessionManager()
            page_id = "test_page_1"
            session_manager.add_page(page_id, page)
            
            # Create handler and daemon
            handler = AIAgentHandler(session_manager)
            daemon = MockDaemon()
            
            # Create agent
            agent = create_agent(page_id)
            daemon.agent = agent
            
            # Send query to handler
            query = "Find the selector for the subscribe button in the menu. Once found, click it."
            logger.info(f"Sending query to AI agent: {query}")
            result = await handler.handle({
                "command": "ai-agent",
                "page_id": page_id,
                "query": query
            }, daemon)
            
            logger.info(f"Initial result: {result}")
            assert "job_id" in result
            
            # Wait for job to complete
            job_id = result["job_id"]
            max_wait = 30  # Maximum seconds to wait
            wait_time = 0
            
            while wait_time < max_wait:
                job = daemon.job_store.get_job(job_id)
                if job and job.status == "completed":
                    logger.info("Job completed successfully")
                    logger.info("AI Agent's Answer:")
                    logger.info("-" * 40)
                    logger.info(job.result.data)
                    logger.info("-" * 40)
                    break
                elif job and job.status == "error":
                    logger.error(f"Job failed with error: {job.error}")
                    break
                await asyncio.sleep(1)
                wait_time += 1
                
            if wait_time >= max_wait:
                logger.error("Job did not complete within the timeout period")
            
            # Keep the browser open for a moment to see the result
            await asyncio.sleep(5)
            
        finally:
            # Cleanup
            logger.info("Cleaning up")
            await page.close()
            await browser.close()
            logger.info("Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main()) 