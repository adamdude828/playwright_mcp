"""Tests for browser manager functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from playwright_mcp.browser_daemon.browser_manager import BrowserManager
from playwright_mcp.browser_daemon.core.session import session_manager


@pytest.fixture
def mock_server():
    """Create a mock server for testing."""
    server = MagicMock()
    server.read_command = AsyncMock()
    server.send_response = AsyncMock()
    server.start = AsyncMock()
    server.cleanup = AsyncMock()
    return server


@pytest.fixture
def browser_manager(mock_server):
    """Create a BrowserManager instance for testing."""
    manager = BrowserManager()
    manager.server = mock_server
    return manager


@pytest.mark.asyncio
async def test_initialization(browser_manager):
    """Test BrowserManager initialization."""
    assert browser_manager.session_manager == session_manager
    assert len(browser_manager.handlers) > 0
    # Check that all handlers have the correct structure
    assert all(
        isinstance(handler_info, dict) and
        "handler" in handler_info and
        "needs_daemon" in handler_info and
        hasattr(handler_info["handler"], "handle")
        for handler_info in browser_manager.handlers.values()
    )


@pytest.mark.asyncio
async def test_handle_connection_valid_command(browser_manager, mock_server):
    """Test handling connection with valid command."""
    mock_server.read_command.return_value = {"command": "navigate", "args": {"url": "test"}}
    
    reader = AsyncMock()
    writer = AsyncMock()
    
    await browser_manager.handle_connection(reader, writer)
    
    mock_server.send_response.assert_called_once()


@pytest.mark.asyncio
async def test_handle_connection_ping(browser_manager, mock_server):
    """Test handling ping command."""
    mock_server.read_command.return_value = {"command": "ping"}
    
    reader = AsyncMock()
    writer = AsyncMock()
    
    await browser_manager.handle_connection(reader, writer)
    
    mock_server.send_response.assert_called_once_with(writer, {"result": "pong"})


@pytest.mark.asyncio
async def test_handle_connection_no_command(browser_manager, mock_server):
    """Test handling connection without command."""
    mock_server.read_command.return_value = {}
    
    reader = AsyncMock()
    writer = AsyncMock()
    
    await browser_manager.handle_connection(reader, writer)
    
    mock_server.send_response.assert_called_once_with(writer, {"error": "No command specified"})


@pytest.mark.asyncio
async def test_handle_connection_unknown_command(browser_manager, mock_server):
    """Test handling unknown command."""
    mock_server.read_command.return_value = {"command": "unknown"}
    
    reader = AsyncMock()
    writer = AsyncMock()
    
    await browser_manager.handle_connection(reader, writer)
    
    mock_server.send_response.assert_called_once_with(writer, {"error": "Unknown command: unknown"})


@pytest.mark.asyncio
async def test_handle_connection_handler_error(browser_manager, mock_server):
    """Test handling connection when handler raises error."""
    mock_server.read_command.return_value = {"command": "navigate"}

    # Create a new mock handler with the error
    error_handler = MagicMock()
    error_handler.handle = AsyncMock(side_effect=Exception("Test error"))
    browser_manager.handlers["navigate"] = {
        "handler": error_handler,
        "needs_daemon": False
    }

    reader = AsyncMock()
    writer = AsyncMock()

    await browser_manager.handle_connection(reader, writer)

    mock_server.send_response.assert_called_once()
    response = mock_server.send_response.call_args[0][1]
    assert "error" in response
    assert "Test error" in response["error"]


@pytest.mark.asyncio
async def test_start(browser_manager):
    """Test starting the browser manager."""
    await browser_manager.start()
    browser_manager.server.start.assert_called_once_with(browser_manager.handle_connection)


@pytest.mark.asyncio
async def test_shutdown(browser_manager):
    """Test shutting down the browser manager."""
    # Mock the session_manager's shutdown method
    browser_manager.session_manager.shutdown = AsyncMock()
    
    await browser_manager.shutdown()
    
    # Verify both shutdown and cleanup were called
    browser_manager.session_manager.shutdown.assert_called_once()
    browser_manager.server.cleanup.assert_called_once() 