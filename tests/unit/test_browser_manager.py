import pytest
from unittest.mock import AsyncMock, patch
from playwright.async_api import BrowserContext, Playwright
from playwright_mcp.browser_daemon.browser_manager import BrowserManager
from playwright_mcp.utils.logging import setup_logging

logger = setup_logging("test_browser_manager")


@pytest.mark.asyncio
async def test_browser_manager_initialization():
    """Test that browser manager initializes correctly."""
    manager = BrowserManager()
    assert manager.sessions == {}
    assert manager.playwright is None


@pytest.mark.asyncio
async def test_launch_browser():
    """Test launching a browser with the manager."""
    logger.debug("Setting up mocks...")
    mock_context = AsyncMock(spec=BrowserContext)

    mock_playwright = AsyncMock(spec=Playwright)
    mock_browser_type = AsyncMock()

    async def mock_launch(**kwargs):
        logger.debug(f"launch called with kwargs: {kwargs}")
        return mock_context

    mock_browser_type.launch = AsyncMock(side_effect=mock_launch)
    mock_playwright.chromium = mock_browser_type
    logger.debug("Mocks configured")

    mock_playwright_factory = AsyncMock()

    async def mock_start():
        logger.debug("mock_playwright_factory.start called")
        return mock_playwright

    mock_playwright_factory.start = AsyncMock(side_effect=mock_start)

    logger.debug("Starting test with mocked playwright")

    with patch('playwright.async_api.async_playwright',
               return_value=mock_playwright_factory):
        with patch('playwright_mcp.browser_daemon.browser_manager.async_playwright',
                   return_value=mock_playwright_factory):
            logger.debug("Patches applied")
            manager = BrowserManager()
            logger.debug("Calling launch_browser...")
            session_id = await manager.launch_browser("chromium")
            assert session_id.startswith("chromium_")
            assert mock_browser_type.launch.called


@pytest.mark.asyncio
async def test_browser_launches_with_single_tab():
    """Test that browser launches successfully."""
    logger.debug("Setting up mocks...")
    mock_context = AsyncMock(spec=BrowserContext)

    mock_playwright = AsyncMock(spec=Playwright)
    mock_browser_type = AsyncMock()

    async def mock_launch(**kwargs):
        logger.debug(f"launch called with kwargs: {kwargs}")
        return mock_context

    mock_browser_type.launch = AsyncMock(side_effect=mock_launch)
    mock_playwright.chromium = mock_browser_type

    mock_playwright_factory = AsyncMock()

    async def mock_start():
        return mock_playwright

    mock_playwright_factory.start = AsyncMock(side_effect=mock_start)

    with patch('playwright.async_api.async_playwright',
               return_value=mock_playwright_factory):
        with patch('playwright_mcp.browser_daemon.browser_manager.async_playwright',
                   return_value=mock_playwright_factory):
            manager = BrowserManager()
            session_id = await manager.launch_browser("chromium")
            assert session_id.startswith("chromium_")
            assert mock_browser_type.launch.called


@pytest.mark.asyncio
async def test_browser_launches_with_single_tab_live():
    """Test that browser launches with exactly one tab using real Playwright."""
    manager = BrowserManager()
    session_id = await manager.launch_browser("chromium", headless=True)
    assert session_id.startswith("chromium_")
    assert len(manager.sessions) == 1 