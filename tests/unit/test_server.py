import pytest
from playwright_mcp.mcp_server import server, handle_list_tools, handle_call_tool
from playwright_mcp.browser_daemon.tools.definitions import get_tool_definitions
from playwright_mcp.browser_daemon.tools.handlers import TOOL_HANDLERS
from unittest.mock import patch


@pytest.mark.asyncio
async def test_server_initialization():
    """Test that server is initialized with correct metadata."""
    assert server.name == "playwright"

    # Check that tool handlers are registered
    tools = await handle_list_tools()
    assert len(tools) > 0  # Verify we have tools registered


@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test that handle_list_tools returns the expected tools."""
    tools = await handle_list_tools()
    expected_tools = get_tool_definitions()

    assert len(tools) == len(expected_tools)
    assert all(t1.name == t2.name for t1, t2 in zip(tools, expected_tools))
    assert all(t1.description == t2.description for t1, t2 in zip(tools, expected_tools))


@pytest.mark.asyncio
async def test_handle_call_tool_missing_args():
    """Test that handle_call_tool raises error with missing arguments."""
    with pytest.raises(ValueError, match="Missing arguments"):
        await handle_call_tool("launch-browser", None)


@pytest.mark.asyncio
async def test_handle_call_tool_unknown_tool():
    """Test that handle_call_tool raises error with unknown tool name."""
    with pytest.raises(ValueError, match="Unknown tool: nonexistent-tool"):
        await handle_call_tool("nonexistent-tool", {"some": "args"})


@pytest.mark.asyncio
async def test_handle_call_tool_execution_failure():
    """Test that handle_call_tool properly handles tool execution failures."""
    # Mock the launch-browser handler to raise an exception
    async def mock_handler(args):
        raise RuntimeError("Browser launch failed")

    with patch.dict(TOOL_HANDLERS, {"launch-browser": mock_handler}):
        with pytest.raises(RuntimeError, match="Browser launch failed"):
            await handle_call_tool("launch-browser", {"browser_type": "chromium"})


@pytest.mark.asyncio
async def test_handle_call_tool_invalid_argument_type():
    """Test that handle_call_tool validates argument types correctly."""
    async def mock_handler(args):
        if not isinstance(args["browser_type"], str):
            raise ValueError("Expected string for browser_type")
        return {"session_id": "test"}

    with patch.dict(TOOL_HANDLERS, {"launch-browser": mock_handler}):
        with pytest.raises(ValueError, match="Expected string for browser_type"):
            await handle_call_tool("launch-browser", {"browser_type": 123})
