import pytest
import asyncio
from mcp.client.session import Session
from mcp.shared.session import create_stdio_transport
from playwright_mcp.server import main as server_main


@pytest.fixture
async def server_client():
    """Fixture that starts the server and provides a client session."""
    # Start server in background task
    server_task = asyncio.create_task(server_main())
    
    # Create client session
    transport = await create_stdio_transport()
    session = Session(transport)
    await session.initialize()
    
    yield session
    
    # Cleanup
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass
    await session.close()


@pytest.mark.asyncio
async def test_list_tools(server_client):
    """Test that we can list tools through the client."""
    tools = await server_client.list_tools()
    assert len(tools) > 0
    
    # Verify we have the expected tools
    tool_names = {tool.name for tool in tools}
    expected_tools = {
        "launch-browser",
        "new-page",
        "goto",
        "close-browser",
        "close-page"
    }
    assert tool_names == expected_tools 