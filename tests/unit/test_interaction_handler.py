import pytest
from unittest.mock import AsyncMock, MagicMock

from playwright_mcp.browser_daemon.handlers.interaction import InteractionHandler
from playwright_mcp.browser_daemon.core.session import SessionManager


@pytest.fixture
def mock_session_manager():
    """Create a mock session manager."""
    manager = MagicMock(spec=SessionManager)
    manager.get_session = MagicMock(return_value=True)
    manager.get_page = MagicMock()
    return manager


@pytest.fixture
def mock_element():
    """Create a mock Playwright element."""
    element = AsyncMock()
    element.click = AsyncMock()
    element.type = AsyncMock()
    element.hover = AsyncMock()
    element.focus = AsyncMock()
    element.press = AsyncMock()
    element.select_option = AsyncMock()
    return element


@pytest.fixture
def mock_page():
    """Create a mock Playwright page."""
    page = AsyncMock()
    page.query_selector = AsyncMock()
    return page


@pytest.fixture
def interaction_handler(mock_session_manager):
    """Create an interaction handler instance."""
    return InteractionHandler(mock_session_manager)


@pytest.mark.asyncio
async def test_handle_unknown_command(interaction_handler):
    """Test handling unknown command."""
    result = await interaction_handler.handle({"command": "unknown"})
    assert "error" in result
    assert "Unknown interaction command" in result["error"]


@pytest.mark.asyncio
async def test_interact_dom_missing_args(interaction_handler):
    """Test interact-dom with missing arguments."""
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "test"  # Missing selector and action
    })
    assert "error" in result
    assert "Missing required arguments" in result["error"]


@pytest.mark.asyncio
async def test_interact_dom_invalid_page(interaction_handler):
    """Test interact-dom with invalid page."""
    interaction_handler.session_manager.get_page.return_value = None
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "invalid",
        "selector": "#test",
        "action": "click"
    })
    assert "error" in result
    assert "No page found" in result["error"]


@pytest.mark.asyncio
async def test_interact_dom_element_not_found(interaction_handler, mock_page):
    """Test interact-dom when element is not found."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = None
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#nonexistent",
        "action": "click"
    })
    
    assert "error" in result
    assert "No element found matching selector" in result["error"]


@pytest.mark.asyncio
async def test_interact_dom_click_success(interaction_handler, mock_page, mock_element):
    """Test successful click interaction."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "click",
        "options": {
            "button": "left",
            "clickCount": 2,
            "position": {"x": 10, "y": 10}
        }
    })
    
    assert "success" in result
    assert result["success"] is True
    mock_element.click.assert_called_once_with(
        button="left",
        click_count=2,
        position={"x": 10, "y": 10}
    )


@pytest.mark.asyncio
async def test_interact_dom_type_success(interaction_handler, mock_page, mock_element):
    """Test successful type interaction."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "type",
        "value": "Hello World",
        "options": {"delay": 100}
    })
    
    assert "success" in result
    assert result["success"] is True
    mock_element.type.assert_called_once_with("Hello World", delay=100)


@pytest.mark.asyncio
async def test_interact_dom_type_missing_value(interaction_handler, mock_page, mock_element):
    """Test type interaction without value."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "type"
    })
    
    assert "error" in result
    assert "Value is required for type action" in result["error"]


@pytest.mark.asyncio
async def test_interact_dom_hover_success(interaction_handler, mock_page, mock_element):
    """Test successful hover interaction."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "hover"
    })
    
    assert "success" in result
    assert result["success"] is True
    mock_element.hover.assert_called_once()


@pytest.mark.asyncio
async def test_interact_dom_focus_success(interaction_handler, mock_page, mock_element):
    """Test successful focus interaction."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "focus"
    })
    
    assert "success" in result
    assert result["success"] is True
    mock_element.focus.assert_called_once()


@pytest.mark.asyncio
async def test_interact_dom_press_success(interaction_handler, mock_page, mock_element):
    """Test successful press interaction."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "press",
        "value": "Enter"
    })
    
    assert "success" in result
    assert result["success"] is True
    mock_element.press.assert_called_once_with("Enter")


@pytest.mark.asyncio
async def test_interact_dom_press_missing_value(interaction_handler, mock_page, mock_element):
    """Test press interaction without value."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "press"
    })
    
    assert "error" in result
    assert "Value (key) is required for press action" in result["error"]


@pytest.mark.asyncio
async def test_interact_dom_select_success(interaction_handler, mock_page, mock_element):
    """Test successful select interaction."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "select",
        "value": "option1"
    })
    
    assert "success" in result
    assert result["success"] is True
    mock_element.select_option.assert_called_once_with("option1")


@pytest.mark.asyncio
async def test_interact_dom_select_missing_value(interaction_handler, mock_page, mock_element):
    """Test select interaction without value."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "select"
    })
    
    assert "error" in result
    assert "Value is required for select action" in result["error"]


@pytest.mark.asyncio
async def test_interact_dom_unknown_action(interaction_handler, mock_page, mock_element):
    """Test interaction with unknown action."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "unknown"
    })
    
    assert "error" in result
    assert "Unknown action" in result["error"]


@pytest.mark.asyncio
async def test_interact_dom_action_fails(interaction_handler, mock_page, mock_element):
    """Test handling of action failure."""
    interaction_handler.session_manager.get_page.return_value = mock_page
    mock_page.query_selector.return_value = mock_element
    mock_element.click.side_effect = Exception("Click failed")
    
    result = await interaction_handler.handle({
        "command": "interact-dom",
        "page_id": "page1",
        "selector": "#test",
        "action": "click"
    })
    
    assert "error" in result
    assert "Click failed" in result["error"] 