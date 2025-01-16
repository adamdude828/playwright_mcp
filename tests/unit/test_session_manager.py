"""Unit tests for SessionManager class."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from playwright.async_api import Browser, Page
from playwright_mcp.browser_daemon.core.session import SessionManager, session_manager


@pytest.fixture
def mock_browser():
    """Create a mock browser instance."""
    browser = MagicMock(spec=Browser)
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_page():
    """Create a mock page instance."""
    page = MagicMock(spec=Page)
    page.close = AsyncMock()
    return page


@pytest.fixture
def session_mgr(mock_browser, mock_page):
    """Get a clean session manager instance for each test."""
    mgr = SessionManager()
    mgr.sessions.clear()
    mgr.pages.clear()
    mgr.playwright = None
    mgr._initialized = True
    
    # Setup mock for browser launch
    async def mock_launch(browser_type: str, headless: bool):
        return mock_browser
    
    # Setup mock for page creation
    async def mock_new_page():
        return mock_page
        
    mock_browser.new_page = mock_new_page
    mgr._launch_browser = AsyncMock(side_effect=mock_launch)
    
    return mgr


@pytest.mark.asyncio
async def test_singleton_behavior():
    """Test that SessionManager maintains singleton behavior."""
    mgr1 = SessionManager()
    mgr2 = SessionManager()
    assert mgr1 is mgr2
    assert id(mgr1) == id(mgr2)


@pytest.mark.asyncio
async def test_session_management(session_mgr, mock_browser):
    """Test basic session management operations."""
    # Launch browser
    session_id = await session_mgr.launch_browser(headless=True)
    assert session_id is not None
    assert session_id in session_mgr.sessions
    
    # Get session
    session = session_mgr.get_session(session_id)
    assert session is not None
    assert session is mock_browser
    
    # Close session
    result = await session_mgr.close_browser(session_id)
    assert result is True
    assert session_id not in session_mgr.sessions
    mock_browser.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_page_management(session_mgr, mock_browser, mock_page):
    """Test page creation and management."""
    # Launch browser and create page
    session_id = await session_mgr.launch_browser(headless=True)
    page_id = await session_mgr.new_page(session_id)
    
    assert page_id is not None
    assert page_id in session_mgr.pages
    
    # Get page
    page = session_mgr.get_page(page_id)
    assert page is not None
    assert page is mock_page
    
    # Close page
    result = await session_mgr.close_page(page_id)
    assert result is True
    assert page_id not in session_mgr.pages
    mock_page.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_page_persistence(session_mgr, mock_browser, mock_page):
    """Test that pages persist between operations."""
    # Create session and page
    session_id = await session_mgr.launch_browser(headless=True)
    page_id = await session_mgr.new_page(session_id)
    
    # Verify page exists
    assert page_id in session_mgr.pages
    
    # Get page multiple times
    page1 = session_mgr.get_page(page_id)
    page2 = session_mgr.get_page(page_id)
    
    assert page1 is page2
    assert id(page1) == id(page2)
    assert page1 is mock_page
    
    # Verify page still exists after operations
    assert page_id in session_mgr.pages


@pytest.mark.asyncio
async def test_shared_instance_behavior(mock_browser, mock_page):
    """Test behavior of the shared session_manager instance."""
    # Clear any existing state
    session_manager.sessions.clear()
    session_manager.pages.clear()
    
    # Setup mocks for the shared instance
    async def mock_launch(browser_type: str, headless: bool):
        return mock_browser
    session_manager._launch_browser = AsyncMock(side_effect=mock_launch)
    mock_browser.new_page = AsyncMock(return_value=mock_page)
    
    # Create session and page
    session_id = await session_manager.launch_browser(headless=True)
    page_id = await session_manager.new_page(session_id)
    
    # Get a new instance and verify it sees the same state
    new_manager = SessionManager()
    assert new_manager.get_page(page_id) is mock_page
    assert page_id in new_manager.pages
    assert session_id in new_manager.sessions
    
    # Verify both instances share the same data
    assert new_manager.pages is session_manager.pages
    assert new_manager.sessions is session_manager.sessions 