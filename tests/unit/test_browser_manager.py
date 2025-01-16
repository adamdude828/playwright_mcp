import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from playwright_mcp.browser_daemon.browser_manager import BrowserManager
from playwright_mcp.browser_daemon.core.session import session_manager


@pytest.fixture
def mock_server():
    """Mock UnixSocketServer."""
    server = MagicMock()
    server.start = AsyncMock()
    server.read_command = AsyncMock()
    server.send_response = AsyncMock()
    server.cleanup = MagicMock()
    return server


@pytest.fixture
def mock_handlers():
    """Mock command handlers."""
    handler = MagicMock()
    handler.handle = AsyncMock(return_value={"result": "success"})
    return {
        "navigate": handler,
        "execute-js": handler,
        "screenshot": handler,
        "close-browser": handler
    }


@pytest.fixture
def browser_manager(mock_server):
    """Create BrowserManager with mocked server."""
    with patch("playwright_mcp.browser_daemon.browser_manager.UnixSocketServer", return_value=mock_server):
        manager = BrowserManager()
        return manager


@pytest.mark.asyncio
async def test_initialization(browser_manager):
    """Test BrowserManager initialization."""
    assert browser_manager.session_manager == session_manager
    assert len(browser_manager.handlers) > 0
    assert all(hasattr(handler, "handle") for handler in browser_manager.handlers.values())


@pytest.mark.asyncio
async def test_handle_connection_valid_command(browser_manager, mock_server):
    """Test handling connection with valid command."""
    mock_server.read_command.return_value = {
        "command": "navigate",
        "args": {"url": "https://example.com"}
    }
    
    reader = AsyncMock()
    writer = AsyncMock()
    
    await browser_manager.handle_connection(reader, writer)
    
    mock_server.read_command.assert_called_once_with(reader)
    mock_server.send_response.assert_called_once()
    response = mock_server.send_response.call_args[0][1]
    assert "error" not in response


@pytest.mark.asyncio
async def test_handle_connection_ping(browser_manager, mock_server):
    """Test handling ping command."""
    mock_server.read_command.return_value = {"command": "ping"}
    
    reader = AsyncMock()
    writer = AsyncMock()
    
    await browser_manager.handle_connection(reader, writer)
    
    mock_server.send_response.assert_called_once()
    response = mock_server.send_response.call_args[0][1]
    assert response == {"result": "pong"}


@pytest.mark.asyncio
async def test_handle_connection_no_command(browser_manager, mock_server):
    """Test handling connection with no command."""
    mock_server.read_command.return_value = {"args": {}}
    
    reader = AsyncMock()
    writer = AsyncMock()
    
    await browser_manager.handle_connection(reader, writer)
    
    mock_server.send_response.assert_called_once()
    response = mock_server.send_response.call_args[0][1]
    assert "error" in response
    assert "No command specified" in response["error"]


@pytest.mark.asyncio
async def test_handle_connection_unknown_command(browser_manager, mock_server):
    """Test handling connection with unknown command."""
    mock_server.read_command.return_value = {"command": "unknown"}
    
    reader = AsyncMock()
    writer = AsyncMock()
    
    await browser_manager.handle_connection(reader, writer)
    
    mock_server.send_response.assert_called_once()
    response = mock_server.send_response.call_args[0][1]
    assert "error" in response
    assert "Unknown command" in response["error"]


@pytest.mark.asyncio
async def test_handle_connection_handler_error(browser_manager, mock_server):
    """Test handling connection when handler raises error."""
    mock_server.read_command.return_value = {"command": "navigate"}
    
    # Create a new mock handler with the error
    error_handler = MagicMock()
    error_handler.handle = AsyncMock(side_effect=Exception("Test error"))
    browser_manager.handlers["navigate"] = error_handler
    
    reader = AsyncMock()
    writer = AsyncMock()
    
    await browser_manager.handle_connection(reader, writer)
    
    mock_server.send_response.assert_called_once()
    response = mock_server.send_response.call_args[0][1]
    assert "error" in response
    assert "Test error" in response["error"]


@pytest.mark.asyncio
async def test_start(browser_manager, mock_server):
    """Test starting browser manager service."""
    await browser_manager.start()
    mock_server.start.assert_called_once_with(browser_manager.handle_connection)


@pytest.mark.asyncio
async def test_shutdown(browser_manager, mock_server):
    """Test shutting down browser manager service."""
    with patch.object(session_manager, "shutdown", new_callable=AsyncMock) as mock_shutdown:
        await browser_manager.shutdown()
        mock_shutdown.assert_called_once()
        mock_server.cleanup.assert_called_once() 