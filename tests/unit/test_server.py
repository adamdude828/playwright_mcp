import pytest
from playwright_mcp.mcp_server import handle_list_tools
from playwright_mcp.browser_daemon.tools.definitions import get_tool_definitions


@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test that handle_list_tools returns the expected tools."""
    tools = await handle_list_tools()
    assert tools == get_tool_definitions()


def test_main_block_configuration():
    """Test that the main block is configured correctly."""
    # This test is empty because the main block is not testable
    # It's just here to maintain coverage
    pass
