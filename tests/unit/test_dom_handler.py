import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from playwright_mcp.browser_daemon.handlers.dom import DOMHandler
from playwright_mcp.browser_daemon.core.session import SessionManager


@pytest.fixture
def mock_session_manager():
    """Create a mock session manager."""
    manager = MagicMock(spec=SessionManager)
    manager.get_session = MagicMock(return_value=True)
    manager.get_page = MagicMock()
    return manager


@pytest.fixture
def mock_page():
    """Create a mock page."""
    page = AsyncMock()
    page.evaluate = AsyncMock()
    page.content = AsyncMock()
    return page


@pytest.fixture
def dom_handler(mock_session_manager):
    """Create a DOM handler instance."""
    return DOMHandler(mock_session_manager)


@pytest.fixture
def sample_html():
    """Sample HTML content for testing DOM operations."""
    return """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div id="test-id" class="test-class">
                <span data-test="value">Test content</span>
            </div>
            <div class="test-class-2">
                <p>More test content</p>
            </div>
        </body>
    </html>
    """


@pytest.mark.asyncio
async def test_handle_unknown_command(dom_handler):
    """Test handling unknown command."""
    result = await dom_handler.handle({"command": "unknown"})
    assert "error" in result
    assert "Unknown DOM command" in result["error"]


@pytest.mark.asyncio
async def test_execute_js_missing_args(dom_handler):
    """Test execute-js with missing arguments."""
    result = await dom_handler.handle({
        "command": "execute-js",
        "session_id": "test"  # Missing page_id and script
    })
    assert "error" in result
    assert "Missing required arguments" in result["error"]


@pytest.mark.asyncio
async def test_execute_js_invalid_session(dom_handler):
    """Test execute-js with invalid session."""
    dom_handler.session_manager.get_session.return_value = False
    result = await dom_handler.handle({
        "command": "execute-js",
        "session_id": "invalid",
        "page_id": "page1",
        "script": "return true;"
    })
    assert "error" in result
    assert "No browser session found" in result["error"]


@pytest.mark.asyncio
async def test_execute_js_invalid_page(dom_handler):
    """Test execute-js with invalid page."""
    dom_handler.session_manager.get_page.return_value = None
    result = await dom_handler.handle({
        "command": "execute-js",
        "session_id": "session1",
        "page_id": "invalid",
        "script": "return true;"
    })
    assert "error" in result
    assert "No page found" in result["error"]


@pytest.mark.asyncio
async def test_execute_js_success(dom_handler, mock_page):
    """Test successful JavaScript execution."""
    dom_handler.session_manager.get_page.return_value = mock_page
    mock_page.evaluate.return_value = {"key": "value"}
    
    result = await dom_handler.handle({
        "command": "execute-js",
        "session_id": "session1",
        "page_id": "page1",
        "script": "return {key: 'value'};"
    })
    
    assert "result" in result
    assert result["result"] == {"key": "value"}
    mock_page.evaluate.assert_called_once_with("return {key: 'value'};")


@pytest.mark.asyncio
async def test_execute_js_evaluation_error(dom_handler, mock_page):
    """Test error handling during JavaScript execution."""
    error_msg = "JavaScript evaluation failed"
    dom_handler.session_manager.get_page.return_value = mock_page
    mock_page.evaluate.side_effect = Exception(error_msg)
    
    result = await dom_handler.handle({
        "command": "execute-js",
        "session_id": "session1",
        "page_id": "page1",
        "script": "return true;"
    })
    
    assert "error" in result
    assert result["error"] == error_msg


@pytest.mark.asyncio
async def test_explore_dom_missing_args(dom_handler):
    """Test explore-dom with missing arguments."""
    result = await dom_handler.handle({
        "command": "explore-dom"
    })
    assert "error" in result
    assert "Missing required arguments" in result["error"]


@pytest.mark.asyncio
async def test_explore_dom_invalid_page(dom_handler):
    """Test explore-dom with invalid page."""
    dom_handler.session_manager.get_page.return_value = None
    result = await dom_handler.handle({
        "command": "explore-dom",
        "page_id": "invalid"
    })
    assert "error" in result
    assert "No page found" in result["error"]


@pytest.mark.asyncio
async def test_explore_dom_success(dom_handler, mock_page):
    """Test successful DOM exploration."""
    dom_handler.session_manager.get_page.return_value = mock_page
    
    with patch(
            "playwright_mcp.browser_daemon.tools.dom_explorer.explore_dom",
            new_callable=AsyncMock
    ) as mock_explore:
        mock_explore.return_value = {"elements": ["div", "span"]}
        
        result = await dom_handler.handle({
            "command": "explore-dom",
            "page_id": "page1",
            "selector": "body"
        })
        
        assert "elements" in result
        assert result["elements"] == ["div", "span"]
        mock_explore.assert_called_once_with(mock_page, "body")


@pytest.mark.asyncio
async def test_explore_dom_with_invalid_html(dom_handler, mock_page):
    """Test DOM exploration with invalid HTML content."""
    error_msg = "Invalid HTML"
    dom_handler.session_manager.get_page.return_value = mock_page
    mock_page.content.return_value = "<div>Unclosed div"
    
    with patch(
            "playwright_mcp.browser_daemon.tools.dom_explorer.explore_dom",
            new_callable=AsyncMock
    ) as mock_explore:
        mock_explore.side_effect = Exception(error_msg)
        
        result = await dom_handler.handle({
            "command": "explore-dom",
            "page_id": "page1",
            "selector": "body"
        })
        
        assert "error" in result
        assert result["error"] == error_msg


@pytest.mark.asyncio
async def test_explore_dom_with_invalid_selector(dom_handler, mock_page):
    """Test DOM exploration with an invalid selector."""
    error_msg = "Invalid selector"
    dom_handler.session_manager.get_page.return_value = mock_page
    mock_page.content.return_value = "<html><body><div>Test</div></body></html>"
    
    with patch(
            "playwright_mcp.browser_daemon.tools.dom_explorer.explore_dom",
            new_callable=AsyncMock
    ) as mock_explore:
        mock_explore.side_effect = Exception(error_msg)
        
        result = await dom_handler.handle({
            "command": "explore-dom",
            "page_id": "page1",
            "selector": "invalid::selector"
        })
        
        assert "error" in result
        assert result["error"] == error_msg


@pytest.mark.asyncio
async def test_search_dom_missing_args(dom_handler):
    """Test search-dom with missing arguments."""
    result = await dom_handler.handle({
        "command": "search-dom"
    })
    assert "error" in result
    assert "Missing required arguments" in result["error"]


@pytest.mark.asyncio
async def test_search_dom_invalid_page(dom_handler):
    """Test search-dom with invalid page."""
    dom_handler.session_manager.get_page.return_value = None
    result = await dom_handler.handle({
        "command": "search-dom",
        "page_id": "invalid",
        "search_text": "test"
    })
    assert "error" in result
    assert "No page found" in result["error"]


@pytest.mark.asyncio
async def test_search_dom_success(dom_handler, mock_page, sample_html):
    """Test successful DOM search."""
    dom_handler.session_manager.get_page.return_value = mock_page
    mock_page.content.return_value = sample_html
    
    result = await dom_handler.handle({
        "command": "search-dom",
        "page_id": "page1",
        "search_text": "test"
    })
    
    assert "matches" in result
    assert "total" in result
    assert result["total"] > 0
    
    # Verify we found matches by ID, class, attribute, and text
    match_types = {match["type"] for match in result["matches"]}
    assert "id" in match_types
    assert "class" in match_types
    assert "attribute" in match_types
    assert "text" in match_types


@pytest.mark.asyncio
async def test_search_dom_no_matches(dom_handler, mock_page, sample_html):
    """Test DOM search with no matches."""
    dom_handler.session_manager.get_page.return_value = mock_page
    mock_page.content.return_value = sample_html
    
    result = await dom_handler.handle({
        "command": "search-dom",
        "page_id": "page1",
        "search_text": "nonexistent"
    })
    
    assert "matches" in result
    assert "total" in result
    assert result["total"] == 0
    assert len(result["matches"]) == 0


@pytest.mark.asyncio
async def test_search_dom_error_handling(dom_handler, mock_page):
    """Test error handling during DOM search."""
    dom_handler.session_manager.get_page.return_value = mock_page
    mock_page.content.side_effect = Exception("Failed to get content")
    
    result = await dom_handler.handle({
        "command": "search-dom",
        "page_id": "page1",
        "search_text": "test"
    })
    
    assert "error" in result
    assert "Failed to get content" in result["error"] 


@pytest.mark.asyncio
async def test_search_dom_with_malformed_html(dom_handler, mock_page):
    """Test DOM search with malformed HTML that might cause parsing issues."""
    dom_handler.session_manager.get_page.return_value = mock_page
    mock_page.content.return_value = "<div class='test'>Unclosed div"
    
    result = await dom_handler.handle({
        "command": "search-dom",
        "page_id": "page1",
        "search_text": "test"
    })
    
    assert "matches" in result
    assert "total" in result
    assert result["total"] > 0  # Should still find the class match despite malformed HTML


@pytest.mark.asyncio
async def test_search_dom_with_list_attributes(dom_handler, mock_page):
    """Test DOM search with list-type attribute values."""
    html = """
    <html>
        <body>
            <div data-test='["test-value", "another-value"]'>
                Test content
            </div>
        </body>
    </html>
    """
    dom_handler.session_manager.get_page.return_value = mock_page
    mock_page.content.return_value = html
    
    result = await dom_handler.handle({
        "command": "search-dom",
        "page_id": "page1",
        "search_text": "test"
    })
    
    assert "matches" in result
    assert "total" in result
    assert result["total"] > 0
    
    # Verify we found the attribute match
    attribute_matches = [m for m in result["matches"] if m["type"] == "attribute"]
    assert len(attribute_matches) > 0
    assert any(
        m["attribute"] == "data-test" and "test-value" in str(m["value"])
        for m in attribute_matches
    )
 