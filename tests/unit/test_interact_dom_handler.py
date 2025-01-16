import pytest
from unittest.mock import patch

from playwright_mcp.browser_daemon.tools.handlers.interact_dom import handle_interact_dom


@pytest.mark.asyncio
async def test_interact_dom_success():
    """Test successful DOM interaction."""
    with patch("playwright_mcp.browser_daemon.tools.handlers.interact_dom.send_to_manager") as mock_send:
        mock_send.return_value = {"success": True}
        
        result = await handle_interact_dom({
            "page_id": "page1",
            "selector": "#test",
            "action": "click"
        })
        
        assert not result.get("isError")
        assert len(result["content"]) == 1
        assert "Successfully clicked" in result["content"][0].text
        mock_send.assert_called_once_with("interact-dom", {
            "page_id": "page1",
            "selector": "#test",
            "action": "click"
        })


@pytest.mark.asyncio
async def test_interact_dom_with_options():
    """Test DOM interaction with options."""
    with patch("playwright_mcp.browser_daemon.tools.handlers.interact_dom.send_to_manager") as mock_send:
        mock_send.return_value = {"success": True}
        
        result = await handle_interact_dom({
            "page_id": "page1",
            "selector": "#test",
            "action": "click",
            "options": {
                "button": "left",
                "clickCount": 2
            }
        })
        
        assert not result.get("isError")
        assert len(result["content"]) == 1
        assert "Successfully clicked" in result["content"][0].text
        mock_send.assert_called_once_with("interact-dom", {
            "page_id": "page1",
            "selector": "#test",
            "action": "click",
            "options": {
                "button": "left",
                "clickCount": 2
            }
        })


@pytest.mark.asyncio
async def test_interact_dom_type_with_value():
    """Test type interaction with value."""
    with patch("playwright_mcp.browser_daemon.tools.handlers.interact_dom.send_to_manager") as mock_send:
        mock_send.return_value = {"success": True}
        
        result = await handle_interact_dom({
            "page_id": "page1",
            "selector": "#test",
            "action": "type",
            "value": "Hello World"
        })
        
        assert not result.get("isError")
        assert len(result["content"]) == 1
        assert "Successfully typed" in result["content"][0].text
        mock_send.assert_called_once_with("interact-dom", {
            "page_id": "page1",
            "selector": "#test",
            "action": "type",
            "value": "Hello World"
        })


@pytest.mark.asyncio
async def test_interact_dom_error_response():
    """Test handling of error response from manager."""
    with patch("playwright_mcp.browser_daemon.tools.handlers.interact_dom.send_to_manager") as mock_send:
        mock_send.return_value = {"error": "Element not found"}
        
        result = await handle_interact_dom({
            "page_id": "page1",
            "selector": "#test",
            "action": "click"
        })
        
        assert result["isError"]
        assert len(result["content"]) == 1
        assert "Element not found" in result["content"][0].text


@pytest.mark.asyncio
async def test_interact_dom_exception():
    """Test handling of exceptions."""
    with patch("playwright_mcp.browser_daemon.tools.handlers.interact_dom.send_to_manager") as mock_send:
        mock_send.side_effect = Exception("Connection failed")
        
        result = await handle_interact_dom({
            "page_id": "page1",
            "selector": "#test",
            "action": "click"
        })
        
        assert result["isError"]
        assert len(result["content"]) == 1
        assert "Connection failed" in result["content"][0].text


@pytest.mark.asyncio
async def test_interact_dom_press_key():
    """Test press key interaction."""
    with patch("playwright_mcp.browser_daemon.tools.handlers.interact_dom.send_to_manager") as mock_send:
        mock_send.return_value = {"success": True}
        
        result = await handle_interact_dom({
            "page_id": "page1",
            "selector": "#test",
            "action": "press",
            "value": "Enter"
        })
        
        assert not result.get("isError")
        assert len(result["content"]) == 1
        assert "Successfully pressed key 'Enter'" in result["content"][0].text
        mock_send.assert_called_once_with("interact-dom", {
            "page_id": "page1",
            "selector": "#test",
            "action": "press",
            "value": "Enter"
        })


@pytest.mark.asyncio
async def test_interact_dom_select():
    """Test select interaction."""
    with patch("playwright_mcp.browser_daemon.tools.handlers.interact_dom.send_to_manager") as mock_send:
        mock_send.return_value = {"success": True}
        
        result = await handle_interact_dom({
            "page_id": "page1",
            "selector": "#test",
            "action": "select",
            "value": "option1"
        })
        
        assert not result.get("isError")
        assert len(result["content"]) == 1
        assert "Successfully selected option" in result["content"][0].text
        mock_send.assert_called_once_with("interact-dom", {
            "page_id": "page1",
            "selector": "#test",
            "action": "select",
            "value": "option1"
        }) 