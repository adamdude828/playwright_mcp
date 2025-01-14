"""Unit tests for SessionManager class."""
import pytest
from unittest.mock import Mock, AsyncMock
from playwright_mcp.browser_daemon.session import SessionManager


@pytest.fixture
def session_manager():
    """Create a fresh SessionManager instance for each test."""
    return SessionManager()


@pytest.fixture
def mock_playwright():
    """Create a mock Playwright instance."""
    mock = AsyncMock()
    mock.stop = AsyncMock()
    return mock


@pytest.fixture
def mock_browser_context():
    """Create a mock BrowserContext instance."""
    mock = AsyncMock()
    mock.close = AsyncMock()
    return mock


@pytest.fixture
def mock_page():
    """Create a mock Page instance."""
    mock = AsyncMock()
    mock.close = AsyncMock()
    mock.context = None  # Will be set in tests that need it
    return mock


def test_add_session(session_manager, mock_playwright, mock_browser_context):
    """Test adding a new browser session."""
    session_id = "test_session"
    session_manager.add_session(session_id, mock_playwright, mock_browser_context)
    
    assert session_manager.active_playwright[session_id] == mock_playwright
    assert session_manager.active_contexts[session_id] == mock_browser_context


def test_add_page(session_manager, mock_page):
    """Test adding a new page."""
    page_id = "test_page"
    session_manager.add_page(page_id, mock_page)
    
    assert session_manager.active_pages[page_id] == mock_page


def test_get_context_invalid_session(session_manager):
    """Test getting context with invalid session ID raises ValueError."""
    with pytest.raises(ValueError, match="No browser session found for ID: invalid_session"):
        session_manager.get_context("invalid_session")


def test_get_page_invalid_page(session_manager):
    """Test getting page with invalid page ID raises ValueError."""
    with pytest.raises(ValueError, match="No page found for ID: invalid_page"):
        session_manager.get_page("invalid_page")


def test_get_playwright_invalid_session(session_manager):
    """Test getting playwright with invalid session ID raises ValueError."""
    with pytest.raises(ValueError, match="No playwright instance found for ID: invalid_session"):
        session_manager.get_playwright("invalid_session")


def test_successful_get_context(session_manager, mock_playwright, mock_browser_context):
    """Test successful retrieval of browser context."""
    session_id = "test_session"
    session_manager.add_session(session_id, mock_playwright, mock_browser_context)
    
    retrieved_context = session_manager.get_context(session_id)
    assert retrieved_context == mock_browser_context


def test_successful_get_page(session_manager, mock_page):
    """Test successful retrieval of page."""
    page_id = "test_page"
    session_manager.add_page(page_id, mock_page)
    
    retrieved_page = session_manager.get_page(page_id)
    assert retrieved_page == mock_page


def test_successful_get_playwright(session_manager, mock_playwright, mock_browser_context):
    """Test successful retrieval of playwright instance."""
    session_id = "test_session"
    session_manager.add_session(session_id, mock_playwright, mock_browser_context)
    
    retrieved_playwright = session_manager.get_playwright(session_id)
    assert retrieved_playwright == mock_playwright


def test_multiple_sessions(session_manager, mock_playwright, mock_browser_context):
    """Test managing multiple sessions."""
    # Create multiple mock instances
    mock_playwright2 = Mock()
    mock_context2 = Mock()
    
    # Add multiple sessions
    session_manager.add_session("session1", mock_playwright, mock_browser_context)
    session_manager.add_session("session2", mock_playwright2, mock_context2)
    
    # Verify both sessions are stored correctly
    assert session_manager.get_context("session1") == mock_browser_context
    assert session_manager.get_context("session2") == mock_context2
    assert session_manager.get_playwright("session1") == mock_playwright
    assert session_manager.get_playwright("session2") == mock_playwright2


def test_multiple_pages(session_manager, mock_page):
    """Test managing multiple pages."""
    # Create multiple mock pages
    mock_page2 = Mock()
    
    # Add multiple pages
    session_manager.add_page("page1", mock_page)
    session_manager.add_page("page2", mock_page2)
    
    # Verify both pages are stored correctly
    assert session_manager.get_page("page1") == mock_page
    assert session_manager.get_page("page2") == mock_page2


def test_empty_session_id(session_manager, mock_playwright, mock_browser_context):
    """Test handling empty session ID."""
    session_id = ""
    session_manager.add_session(session_id, mock_playwright, mock_browser_context)
    
    # Should still work with empty string as key
    assert session_manager.get_context(session_id) == mock_browser_context
    assert session_manager.get_playwright(session_id) == mock_playwright


def test_special_chars_session_id(session_manager, mock_playwright, mock_browser_context):
    """Test handling session ID with special characters."""
    session_id = "test@#$%^&*()_+"
    session_manager.add_session(session_id, mock_playwright, mock_browser_context)
    
    # Should work with special characters
    assert session_manager.get_context(session_id) == mock_browser_context
    assert session_manager.get_playwright(session_id) == mock_playwright


@pytest.mark.asyncio
async def test_close_session_invalid_id(session_manager):
    """Test closing non-existent session raises ValueError."""
    with pytest.raises(ValueError, match="No browser session found for ID: invalid_session"):
        await session_manager.close_session("invalid_session")


@pytest.mark.asyncio
async def test_close_session_with_pages(session_manager, mock_playwright, mock_browser_context, mock_page):
    """Test closing a session with associated pages."""
    session_id = "test_session"
    page_id = "test_page"
    
    # Set up the session with a page
    mock_page.context = mock_browser_context
    session_manager.add_session(session_id, mock_playwright, mock_browser_context)
    session_manager.add_page(page_id, mock_page)
    
    # Close the session
    await session_manager.close_session(session_id)
    
    # Verify cleanup
    mock_page.close.assert_awaited_once()
    mock_browser_context.close.assert_awaited_once()
    mock_playwright.stop.assert_awaited_once()
    
    # Verify session and page are removed
    assert session_id not in session_manager.active_contexts
    assert session_id not in session_manager.active_playwright
    assert page_id not in session_manager.active_pages


@pytest.mark.asyncio
async def test_cleanup_multiple_sessions(session_manager, mock_playwright, mock_browser_context, mock_page):
    """Test cleanup of multiple sessions."""
    # Create multiple sessions and pages
    mock_playwright2 = AsyncMock()
    mock_context2 = AsyncMock()
    mock_page2 = AsyncMock()
    
    mock_playwright2.stop = AsyncMock()
    mock_context2.close = AsyncMock()
    mock_page2.close = AsyncMock()
    
    # Set up contexts for pages
    mock_page.context = mock_browser_context
    mock_page2.context = mock_context2
    
    # Add sessions and pages
    session_manager.add_session("session1", mock_playwright, mock_browser_context)
    session_manager.add_session("session2", mock_playwright2, mock_context2)
    session_manager.add_page("page1", mock_page)
    session_manager.add_page("page2", mock_page2)
    
    # Run cleanup
    await session_manager.cleanup()
    
    # Verify all resources were cleaned up
    mock_page.close.assert_awaited_once()
    mock_page2.close.assert_awaited_once()
    mock_browser_context.close.assert_awaited_once()
    mock_context2.close.assert_awaited_once()
    mock_playwright.stop.assert_awaited_once()
    mock_playwright2.stop.assert_awaited_once()
    
    # Verify all sessions and pages are removed
    assert not session_manager.active_contexts
    assert not session_manager.active_playwright
    assert not session_manager.active_pages


@pytest.mark.asyncio
async def test_cleanup_with_error(session_manager, mock_playwright, mock_browser_context, capsys):
    """Test cleanup handling when an error occurs during session cleanup."""
    session_id = "test_session"
    session_manager.add_session(session_id, mock_playwright, mock_browser_context)
    
    # Make the context.close() method raise an exception
    mock_browser_context.close.side_effect = Exception("Test error")
    
    # Run cleanup
    await session_manager.cleanup()
    
    # Verify error was printed
    captured = capsys.readouterr()
    assert f"Error cleaning up session {session_id}: Test error" in captured.out
    
    # Verify the cleanup attempted to close the context
    mock_browser_context.close.assert_awaited_once()
    
    # The session should still be active since cleanup failed
    assert session_id in session_manager.active_contexts
    assert session_id in session_manager.active_playwright 