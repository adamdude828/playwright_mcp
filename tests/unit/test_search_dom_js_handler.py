import pytest
from unittest.mock import patch
from playwright_mcp.browser_daemon.tools.handlers.search_dom_js import handle_search_dom_js


@pytest.fixture
def mock_send_to_manager():
    with patch("playwright_mcp.browser_daemon.tools.handlers.search_dom_js.send_to_manager") as mock:
        yield mock


@pytest.mark.asyncio
async def test_missing_page_id():
    """Test that handler requires page_id."""
    result = await handle_search_dom_js({})
    assert result["isError"] is True
    assert "page_id is required" in result["content"][0].text


@pytest.mark.asyncio
async def test_injection_failure(mock_send_to_manager):
    """Test handling of JS injection failure."""
    mock_send_to_manager.return_value = {"error": "Failed to inject"}
    
    result = await handle_search_dom_js({"page_id": "test-page"})
    
    assert result["isError"] is True
    assert "Failed to inject search functions" in result["content"][0].text


@pytest.mark.asyncio
async def test_text_search_success(mock_send_to_manager):
    """Test successful text search."""
    mock_send_to_manager.side_effect = [
        {},  # Successful injection
        {
            "success": True,
            "matches": [{
                "type": "text",
                "tag": "div",
                "path": "body > div:nth-child(1)",
                "text": "Hello World",
                "attributes": {"class": "greeting"}
            }]
        }
    ]
    
    result = await handle_search_dom_js({
        "page_id": "test-page",
        "text": "Hello"
    })
    
    assert not result.get("isError")
    assert "Found 1 matches" in result["content"][0].text
    assert "Type: text" in result["content"][0].text
    assert "Tag: div" in result["content"][0].text


@pytest.mark.asyncio
async def test_tag_search_success(mock_send_to_manager):
    """Test successful tag search."""
    mock_send_to_manager.side_effect = [
        {},  # Successful injection
        {
            "success": True,
            "matches": [{
                "type": "tag",
                "tag": "button",
                "path": "body > button:nth-child(1)",
                "text": "Click me",
                "attributes": {"type": "submit"}
            }]
        }
    ]
    
    result = await handle_search_dom_js({
        "page_id": "test-page",
        "tag": "button"
    })
    
    assert not result.get("isError")
    assert "Found 1 matches" in result["content"][0].text
    assert "Type: tag" in result["content"][0].text
    assert "Tag: button" in result["content"][0].text


@pytest.mark.asyncio
async def test_class_search_success(mock_send_to_manager):
    """Test successful class search."""
    mock_send_to_manager.side_effect = [
        {},  # Successful injection
        {
            "success": True,
            "matches": [{
                "type": "class",
                "tag": "div",
                "path": "body > div:nth-child(1)",
                "text": "Content",
                "attributes": {"class": "container"}
            }]
        }
    ]
    
    result = await handle_search_dom_js({
        "page_id": "test-page",
        "class_name": "container"
    })
    
    assert not result.get("isError")
    assert "Found 1 matches" in result["content"][0].text
    assert "Type: class" in result["content"][0].text
    assert "class: container" in result["content"][0].text.lower()


@pytest.mark.asyncio
async def test_id_search_success(mock_send_to_manager):
    """Test successful ID search."""
    mock_send_to_manager.side_effect = [
        {},  # Successful injection
        {
            "success": True,
            "matches": [{
                "type": "id",
                "tag": "div",
                "path": "body > div:nth-child(1)",
                "text": "Main content",
                "attributes": {"id": "main"}
            }]
        }
    ]
    
    result = await handle_search_dom_js({
        "page_id": "test-page",
        "id": "main"
    })
    
    assert not result.get("isError")
    assert "Found 1 matches" in result["content"][0].text
    assert "Type: id" in result["content"][0].text
    assert "id: main" in result["content"][0].text.lower()


@pytest.mark.asyncio
async def test_attribute_search_success(mock_send_to_manager):
    """Test successful attribute search."""
    mock_send_to_manager.side_effect = [
        {},  # Successful injection
        {
            "success": True,
            "matches": [{
                "type": "attribute",
                "tag": "input",
                "path": "body > form > input:nth-child(1)",
                "text": "",
                "attributes": {"type": "text", "name": "username"}
            }]
        }
    ]
    
    result = await handle_search_dom_js({
        "page_id": "test-page",
        "attribute": {"name": "username"}
    })
    
    assert not result.get("isError")
    assert "Found 1 matches" in result["content"][0].text
    assert "Type: attribute" in result["content"][0].text
    assert "name: username" in result["content"][0].text.lower()


@pytest.mark.asyncio
async def test_multiple_search_criteria(mock_send_to_manager):
    """Test searching with multiple criteria."""
    mock_send_to_manager.side_effect = [
        {},  # Successful injection
        {
            "success": True,
            "matches": [{
                "type": "text",
                "tag": "div",
                "path": "path1",
                "text": "Hello",
                "attributes": {}
            }]
        },
        {
            "success": True,
            "matches": [{
                "type": "tag",
                "tag": "div",
                "path": "path2",
                "text": "World",
                "attributes": {}
            }]
        }
    ]
    
    result = await handle_search_dom_js({
        "page_id": "test-page",
        "text": "Hello",
        "tag": "div"
    })
    
    assert not result.get("isError")
    assert "Found 2 matches" in result["content"][0].text
    assert "Match #1" in result["content"][0].text
    assert "Match #2" in result["content"][0].text


@pytest.mark.asyncio
async def test_no_matches(mock_send_to_manager):
    """Test when no matches are found."""
    mock_send_to_manager.side_effect = [
        {},  # Successful injection
        {"success": True, "matches": []}
    ]
    
    result = await handle_search_dom_js({
        "page_id": "test-page",
        "text": "NonexistentText"
    })
    
    assert not result.get("isError")
    assert "No matches found" in result["content"][0].text


@pytest.mark.asyncio
async def test_partial_search_failure(mock_send_to_manager):
    """Test when some searches succeed and others fail."""
    mock_send_to_manager.side_effect = [
        {},  # Successful injection
        {
            "success": True,
            "matches": [{
                "type": "text",
                "tag": "div",
                "path": "path1",
                "text": "Hello",
                "attributes": {}
            }]
        },
        {"success": False, "error": "Failed to search by tag"}
    ]
    
    result = await handle_search_dom_js({
        "page_id": "test-page",
        "text": "Hello",
        "tag": "div"
    })
    
    assert not result.get("isError")
    assert "Found 1 matches" in result["content"][0].text
    assert "Match #1" in result["content"][0].text


@pytest.mark.asyncio
async def test_all_searches_fail(mock_send_to_manager):
    """Test when all searches fail."""
    mock_send_to_manager.side_effect = [
        {},  # Successful injection
        {"success": False, "error": "Failed to search by text"},
        {"success": False, "error": "Failed to search by tag"}
    ]
    
    result = await handle_search_dom_js({
        "page_id": "test-page",
        "text": "Hello",
        "tag": "div"
    })
    
    assert result["isError"] is True
    assert "Failed to search by text" in result["content"][0].text
    assert "Failed to search by tag" in result["content"][0].text 