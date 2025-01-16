import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
from mcp.types import Tool, TextContent
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions
from playwright_mcp.mcp_server.server import (
    handle_list_tools, handle_call_tool, is_mcp_content,
    TOOLS, start_server, server
)


@pytest.fixture
def mock_tool_definitions():
    """Mock tool definitions."""
    return [
        Tool(
            name="test-tool",
            description="Test tool",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@pytest.fixture
def mock_tool_handlers():
    """Mock tool handlers."""
    async def mock_handler(args):
        return "Success"
    return {"test-tool": mock_handler}


@pytest.fixture
def mock_stdio_server():
    """Mock stdio server context manager."""
    async def mock_server(*args, **kwargs):
        read_stream = AsyncMock()
        write_stream = AsyncMock()
        return read_stream, write_stream
    
    ctx_manager = MagicMock()
    ctx_manager.__aenter__ = mock_server
    ctx_manager.__aexit__ = AsyncMock()
    return ctx_manager


@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test listing available tools."""
    with patch("playwright_mcp.mcp_server.server.get_tool_definitions", return_value=TOOLS):
        tools = await handle_list_tools()
        assert len(tools) > 0
        assert all(isinstance(tool, Tool) for tool in tools)
        assert "start-daemon" in [tool.name for tool in tools]


@pytest.mark.asyncio
async def test_handle_call_tool_success():
    """Test successful tool execution."""
    mock_result = "Test success"
    mock_handler = AsyncMock(return_value=mock_result)
    
    with patch("playwright_mcp.mcp_server.server.TOOL_HANDLERS", {"test-tool": mock_handler}):
        result = await handle_call_tool("test-tool", {})
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == mock_result


@pytest.mark.asyncio
async def test_handle_call_tool_unknown():
    """Test handling unknown tool."""
    result = await handle_call_tool("unknown-tool", {})
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert "Unknown tool" in result[0].text


@pytest.mark.asyncio
async def test_handle_call_tool_error():
    """Test handling tool execution error."""
    mock_handler = AsyncMock(side_effect=Exception("Test error"))
    
    with patch("playwright_mcp.mcp_server.server.TOOL_HANDLERS", {"test-tool": mock_handler}):
        result = await handle_call_tool("test-tool", {})
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Test error" in result[0].text


def test_is_mcp_content():
    """Test MCP content type checking."""
    text_content = TextContent(type="text", text="test")
    assert is_mcp_content(text_content)
    assert not is_mcp_content("plain string")
    assert not is_mcp_content({"type": "text", "text": "test"})


@pytest.mark.asyncio
async def test_server_initialization(mock_stdio_server):
    """Test successful server initialization."""
    with patch("playwright_mcp.mcp_server.server.stdio_server", return_value=mock_stdio_server):
        with patch.object(server, "run") as mock_run:
            await start_server()
            
            # Verify server.run was called with correct initialization options
            mock_run.assert_called_once()
            init_options = mock_run.call_args[0][2]
            assert isinstance(init_options, InitializationOptions)
            assert init_options.server_name == "playwright"
            assert init_options.server_version == "0.1.0"


@pytest.mark.asyncio
async def test_server_shutdown_graceful(mock_stdio_server):
    """Test graceful server shutdown on CancelledError."""
    with patch("playwright_mcp.mcp_server.server.stdio_server", return_value=mock_stdio_server):
        with patch.object(server, "run", side_effect=asyncio.CancelledError):
            await start_server()
            # If we get here without exception, the shutdown was handled gracefully


@pytest.mark.asyncio
async def test_server_error_handling(mock_stdio_server):
    """Test server error handling."""
    test_error = Exception("Test server error")
    
    with patch("playwright_mcp.mcp_server.server.stdio_server") as mock_stdio:
        mock_stdio.side_effect = test_error
        with pytest.raises(Exception) as exc_info:
            await start_server()
        assert str(exc_info.value) == str(test_error)


@pytest.mark.asyncio
async def test_server_capabilities():
    """Test server capabilities configuration."""
    capabilities = server.get_capabilities(
        notification_options=NotificationOptions(),
        experimental_capabilities={}
    )
    
    # Verify basic capability structure
    assert hasattr(capabilities, "tools")
    assert hasattr(capabilities, "experimental")
    assert capabilities.experimental == {} 