import pytest
from playwright_mcp.server import handle_list_tools
from playwright_mcp.tools.definitions import get_tool_definitions


@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test that handle_list_tools returns the correct list of tools."""
    # Get tools directly from definitions
    expected_tools = get_tool_definitions()
    
    # Get tools through the handler
    actual_tools = await handle_list_tools()
    
    # Compare tool lists
    assert len(actual_tools) == len(expected_tools)
    for actual, expected in zip(actual_tools, expected_tools):
        assert actual.name == expected.name
        assert actual.description == expected.description
        assert actual.inputSchema == expected.inputSchema


def test_main_block_configuration():
    """Test that __main__ block is configured correctly."""
    with open("src/playwright_mcp/server.py", "r") as f:
        content = f.read()

    # Check for main block with asyncio.run
    assert 'if __name__ == "__main__":' in content
    assert "asyncio.run(main())" in content
    
    # Verify they appear in the correct order
    main_block_pos = content.find('if __name__ == "__main__":')
    run_pos = content.find("asyncio.run(main())")
    assert main_block_pos < run_pos, "asyncio.run should appear after __main__ check"
    
    # Verify there's a newline at the end of the file
    assert content.endswith("\n"), "File should end with a newline" 