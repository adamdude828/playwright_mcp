"""Tests for AI agent tools."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import logging
from pydantic_ai import RunContext
from pydantic_ai.usage import Usage
from pydantic_ai.models import infer_model
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.tools import (
    search_dom, interact_dom, explore_dom, create_agent,
    SearchDOMInput, InteractDOMInput, ExploreDOMInput
)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_page():
    """Create a mock page."""
    page = Mock()
    page.query_selector.return_value = Mock()
    page.query_selector_all.return_value = [Mock()]
    page.evaluate.return_value = "test content"
    return page


@pytest.fixture
def mock_daemon(mock_page):
    """Create a mock daemon."""
    daemon = Mock()
    daemon.session_manager.get_page.return_value = mock_page
    return daemon


@pytest.fixture
def mock_context():
    """Create a mock RunContext for testing."""
    return RunContext(
        model=infer_model("anthropic:claude-3-sonnet-20240229"),
        usage=Usage(),
        prompt="test prompt",
        deps="test_page_id"
    )


@pytest.mark.asyncio
async def test_search_dom_by_selector(mock_page, mock_context):
    """Test searching the DOM using a selector."""
    element = Mock()
    element.text_content = AsyncMock(return_value="Test Title")
    element.evaluate = AsyncMock(return_value="h1")
    mock_page.query_selector_all = AsyncMock(return_value=[element])

    with patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.tools.session_manager") as mock_session_manager:
        mock_session_manager.get_page = Mock(return_value=mock_page)
        result = await search_dom(
            ctx=mock_context,
            input=SearchDOMInput(selector="h1")
        )

    assert result is not None
    assert "Test Title" in str(result)
    mock_page.query_selector_all.assert_awaited_once_with("h1")


@pytest.mark.asyncio
async def test_search_dom_by_text(mock_page, mock_context):
    """Test searching the DOM using text content."""
    element = Mock()
    element.text_content = AsyncMock(return_value="Test Title")
    element.evaluate = AsyncMock(return_value="div")
    
    get_by_text = Mock()
    get_by_text.all = AsyncMock(return_value=[element])
    mock_page.get_by_text = Mock(return_value=get_by_text)

    with patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.tools.session_manager") as mock_session_manager:
        mock_session_manager.get_page = Mock(return_value=mock_page)
        result = await search_dom(
            ctx=mock_context,
            input=SearchDOMInput(text="Test")
        )

    assert result is not None
    assert "Test Title" in str(result)
    mock_page.get_by_text.assert_called_once_with("Test")


@pytest.mark.asyncio
async def test_interact_dom_click(mock_page, mock_context):
    """Test clicking an element in the DOM."""
    element = Mock()
    element.click = AsyncMock()
    
    mock_page.query_selector = AsyncMock(return_value=element)

    with patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.tools.session_manager") as mock_session_manager:
        mock_session_manager.get_page = Mock(return_value=mock_page)
        result = await interact_dom(
            ctx=mock_context,
            input=InteractDOMInput(selector="button", action="click")
        )

    assert result is not None
    assert "Successfully performed click" in result
    element.click.assert_awaited_once()
    mock_page.query_selector.assert_awaited_once_with("button")


@pytest.mark.asyncio
async def test_interact_dom_type(mock_page, mock_context):
    """Test typing into an element in the DOM."""
    # Set up mock element
    mock_element = Mock()
    mock_element.type = AsyncMock()
    mock_element.evaluate = AsyncMock(return_value="input")

    # Set up mock page
    mock_page.query_selector = AsyncMock(return_value=mock_element)

    # Mock session manager
    with patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.tools.session_manager") as mock_session_manager:
        mock_session_manager.get_page = Mock(return_value=mock_page)

        # Call the function
        result = await interact_dom(
            ctx=mock_context,
            input=InteractDOMInput(selector="test-selector", action="type", value="test text")
        )

        # Verify the result
        assert result == "Successfully performed type"
        mock_page.query_selector.assert_awaited_with("test-selector")
        mock_element.type.assert_awaited_with("test text")


@pytest.mark.asyncio
async def test_explore_dom(mock_page, mock_context):
    """Test exploring the DOM structure."""
    # Set up mock page
    mock_page.content = AsyncMock(return_value="<html><body><h1>Title</h1><p>Content</p></body></html>")

    # Set up mock body element
    mock_body = Mock()
    mock_body.evaluate = AsyncMock(return_value="body")
    mock_body.text_content = AsyncMock(return_value="")
    mock_body.query_selector_all = AsyncMock(return_value=[])

    # Set up mock page query_selector
    mock_page.query_selector = AsyncMock(return_value=mock_body)

    # Mock session manager
    with patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.tools.session_manager") as mock_session_manager:
        mock_session_manager.get_page = Mock(return_value=mock_page)

        # Call the function
        result = await explore_dom(
            ctx=mock_context,
            input=ExploreDOMInput()
        )

        # Verify the result
        assert result is not None
        assert "<body/>" in result
        mock_page.query_selector.assert_awaited_with("body")
        mock_body.evaluate.assert_awaited_with("el => el.tagName.toLowerCase()")


def test_create_agent():
    """Test creating an AI agent with tools."""
    agent = create_agent("test_page_id")
    # Check that the agent has the expected tools
    assert len(agent._function_tools) == 3
    assert "search_dom" in agent._function_tools
    assert "interact_dom" in agent._function_tools
    assert "explore_dom" in agent._function_tools
    # Check that the tools are callable
    assert callable(agent._function_tools["search_dom"].function)
    assert callable(agent._function_tools["interact_dom"].function)
    assert callable(agent._function_tools["explore_dom"].function) 