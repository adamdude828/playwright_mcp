import pytest
from unittest.mock import Mock, AsyncMock, patch
from playwright_mcp.browser_daemon.handlers.ai_agent import AIAgentHandler
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.tools import create_agent


# Configure pytest-asyncio to use function scope for event loops
pytestmark = pytest.mark.asyncio


@pytest.fixture
def session_manager():
    return Mock()


@pytest.fixture
def daemon():
    daemon = Mock()
    daemon.job_store = Mock()
    daemon.job_store.create_job = AsyncMock(return_value="test_job_id")
    daemon.job_store.set_task = Mock()
    daemon.job_store.set_running = Mock()
    daemon.job_store.complete_job = Mock()
    daemon.job_store.fail_job = Mock()
    return daemon


@pytest.fixture
def handler(session_manager):
    return AIAgentHandler(session_manager)


@pytest.mark.asyncio
async def test_handle_missing_command(handler, daemon):
    """Test handling when command is missing."""
    args = {"page_id": "test_page", "query": "test query"}
    result = await handler.handle(args, daemon)
    assert "error" in result
    assert "Unknown AI agent command" in result["error"]


@pytest.mark.asyncio
async def test_handle_missing_required_args(handler, daemon):
    """Test handling when required arguments are missing."""
    args = {"command": "ai-agent"}
    result = await handler.handle(args, daemon)
    assert "error" in result
    assert "Missing required arguments" in result["error"]


@pytest.mark.asyncio
async def test_handle_successful_job_creation(handler, daemon):
    """Test successful job creation and background task start."""
    args = {
        "command": "ai-agent",
        "page_id": "test_page",
        "query": "test query",
        "max_actions": 3
    }
    
    result = await handler.handle(args, daemon)
    
    assert result["job_id"] == "test_job_id"
    assert result["status"] == "running"
    assert "AI agent job started successfully" in result["message"]
    
    daemon.job_store.create_job.assert_called_once_with(
        page_id="test_page",
        query="test query",
        max_actions=3
    )
    assert daemon.job_store.set_running.called
    assert daemon.job_store.set_task.called


@pytest.mark.asyncio
async def test_handle_without_daemon(handler):
    """Test handling when daemon is not provided."""
    args = {
        "command": "ai-agent",
        "page_id": "test_page",
        "query": "test query"
    }
    result = await handler.handle(args)
    assert "error" in result
    assert "Daemon instance required" in result["error"]


@pytest.mark.asyncio
async def test_agent_creation():
    """Test agent creation with valid page_id."""
    page_id = "test_page"
    
    # Mock the Agent class to capture the tools passed to it
    with patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.tools.Agent") as mock_agent:
        create_agent(page_id)
        
        # Get the tools passed to the Agent constructor
        _, kwargs = mock_agent.call_args
        tools = kwargs.get("tools", [])
        
        assert len(tools) == 3  # search_dom, interact_dom, explore_dom
        tool_names = {t.name for t in tools}
        assert tool_names == {"search_dom", "interact_dom", "explore_dom"} 