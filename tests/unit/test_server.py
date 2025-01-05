import pytest
from playwright_mcp.mcp_server.server import server, handle_list_tools, handle_call_tool
from playwright_mcp.browser_daemon.tools.definitions import get_tool_definitions


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
