"""Tests for browser manager functionality."""

import pytest
from playwright_mcp.browser_daemon.browser_manager import BrowserManager
from playwright_mcp.browser_daemon.core.session import session_manager
from playwright_mcp.browser_daemon.core.server import UnixSocketServer
from playwright_mcp.browser_daemon.tools.base import ToolHandler
from unittest.mock import patch, Mock, AsyncMock


@pytest.mark.asyncio
async def test_initialization():
    """Test initialization of BrowserManager."""
    browser_manager = BrowserManager()
    assert browser_manager.session_manager == session_manager


@pytest.mark.asyncio
@patch("playwright_mcp.browser_daemon.browser_manager.UnixSocketServer")
async def test_shutdown(mock_server_class):
    """Test shutdown of BrowserManager."""
    # Set up mocks
    mock_server = Mock()
    mock_server.cleanup = AsyncMock()
    mock_server_class.return_value = mock_server

    mock_session_manager = Mock()
    mock_session_manager.shutdown = AsyncMock()

    # Create browser manager with mocked dependencies
    browser_manager = BrowserManager()
    browser_manager.server = mock_server
    browser_manager.session_manager = mock_session_manager

    # Call shutdown
    await browser_manager.shutdown()

    # Verify mocks were called
    mock_session_manager.shutdown.assert_awaited_once()
    mock_server.cleanup.assert_awaited_once()


class TestInput:
    """Test input model."""
    def __init__(self, value: str):
        self.value = value


@pytest.mark.asyncio
async def test_daemon_parameter_handling():
    """Test that daemon parameter is not passed twice to handlers."""
    manager = BrowserManager()
    
    # Create a handler that will fail if daemon is passed twice
    class TestHandler(ToolHandler):
        name = "test-handler"
        description = "Test handler"
        input_model = TestInput
        
        @classmethod
        @ToolHandler.register(name, description)
        async def handle(cls, args: TestInput, daemon=None):
            # This will raise TypeError if daemon is passed both through args and kwargs
            return {"result": "success"}
    
    # Set up the handler in manager
    manager.handlers = {
        "test-handler": {"handler": TestHandler, "needs_daemon": True}
    }
    
    # Mock the server's read_command method
    class MockReader:
        async def read(self):
            # This is what's happening in the real code - daemon is being passed in args
            return b'{"command": "test-handler", "args": {"value": "test", "daemon": "first_daemon"}}'
        
        async def readline(self):
            return await self.read()
    
    class MockWriter:
        write = AsyncMock()
        drain = AsyncMock()
        wait_closed = AsyncMock()
        
        def close(self):
            pass
    
    # This should raise TypeError due to daemon being passed twice
    await manager.handle_connection(MockReader(), MockWriter()) 