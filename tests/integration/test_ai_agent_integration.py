"""Integration test for AIAgentHandler with direct page interaction."""

import pytest
import asyncio
import logging
from playwright.async_api import async_playwright, Page
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


@pytest.fixture
async def browser_setup():
    """Set up browser and page for testing."""
    logger.info("Setting up browser and page")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        logger.info("Browser and page setup complete")
        
        yield page
        
        # Cleanup
        logger.info("Cleaning up browser and page")
        await page.close()
        await browser.close()
        logger.info("Cleanup complete")


@pytest.mark.asyncio
async def test_ai_agent_query_about_example(browser_setup: Page):
    """Test querying the AI agent about example.com content."""
    page = browser_setup
    
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
    query = "What is the main heading on the page?"
    logger.info(f"Sending query to AI agent: {query}")
    result = await handler.handle({
        "command": "ai-agent",
        "page_id": page_id,
        "query": query
    }, daemon)
    
    assert "job_id" in result
    assert "message" in result
    assert result["message"] == "AI agent job started successfully"
    
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
            logger.info(job.result.data)  # Just log the answer text
            logger.info("-" * 40)
            
            assert "Example Domain" in str(job.result)
            break
        elif job and job.status == "error":
            logger.error(f"Job failed with error: {job.error}")
            logger.error(f"Job details: {vars(job)}")
            break
        await asyncio.sleep(1)
        wait_time += 1 


@pytest.mark.asyncio
async def test_ai_agent_find_subscribe_button(browser_setup: Page):
    """Test finding the subscribe button on The Points Guy website."""
    page = browser_setup
    
    # Navigate to The Points Guy website
    await page.goto("https://thepointsguy.com")
    
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
    
    assert "job_id" in result
    assert "message" in result
    assert result["message"] == "AI agent job started successfully"
    
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
            
            # The result should contain information about finding and clicking the subscribe button
            assert "subscribe" in job.result.data.lower()
            break
            
        elif job and job.status == "error":
            pytest.fail(f"Job failed with error: {job.error}")
            
        await asyncio.sleep(1)
        wait_time += 1
        
    if wait_time >= max_wait:
        pytest.fail("Job did not complete within the timeout period") 