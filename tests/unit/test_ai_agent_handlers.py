"""Unit tests for AI agent handlers."""

import pytest
import json
from unittest.mock import patch

from playwright_mcp.browser_daemon.tools.handlers.ai_agent.handler import handle_ai_agent
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.get_result import handle_get_ai_result


@pytest.mark.asyncio
async def test_handle_ai_agent_missing_page_id():
    """Test AI agent handler with missing page_id."""
    result = await handle_ai_agent({"query": "test query"})
    assert result["isError"] is True
    assert "Missing required argument: page_id" in result["content"][0].text


@pytest.mark.asyncio
async def test_handle_ai_agent_missing_query():
    """Test AI agent handler with missing query."""
    result = await handle_ai_agent({"page_id": "test_page"})
    assert result["isError"] is True
    assert "Missing required argument: query" in result["content"][0].text


@pytest.mark.asyncio
@patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.handler.send_to_manager")
async def test_handle_ai_agent_success(mock_send):
    """Test AI agent handler with successful response."""
    mock_send.return_value = {
        "job_id": "test_job_123",
        "message": "AI agent job started successfully"
    }
    
    result = await handle_ai_agent({
        "page_id": "test_page",
        "query": "test query"
    })
    
    assert result["isError"] is False
    data = json.loads(result["content"][0].text)
    assert data["status"] == "running"
    assert data["job_id"] == "test_job_123"
    assert data["message"] == "AI agent job started successfully"


@pytest.mark.asyncio
@patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.handler.send_to_manager")
async def test_handle_ai_agent_error_response(mock_send):
    """Test AI agent handler with error in response."""
    mock_send.return_value = {
        "error": "Page not found"
    }
    
    result = await handle_ai_agent({
        "page_id": "test_page",
        "query": "test query"
    })
    
    assert result["isError"] is True
    assert "Page not found" in result["content"][0].text


@pytest.mark.asyncio
@patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.handler.send_to_manager")
async def test_handle_ai_agent_exception(mock_send):
    """Test AI agent handler when an exception occurs."""
    mock_send.side_effect = Exception("Connection failed")
    
    result = await handle_ai_agent({
        "page_id": "test_page",
        "query": "test query"
    })
    
    assert result["isError"] is True
    assert "Connection failed" in result["content"][0].text


@pytest.mark.asyncio
@patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.get_result.send_to_manager")
async def test_handle_get_result_success(mock_send):
    """Test successful retrieval of job result."""
    mock_send.return_value = {
        "job_id": "test_job_123",
        "status": "completed",
        "result": "Example Domain"
    }
    
    result = await handle_get_ai_result({
        "job_id": "test_job_123"
    })
    
    assert result["isError"] is False
    data = json.loads(result["content"][0].text)
    assert data["status"] == "completed"
    assert data["job_id"] == "test_job_123"
    assert data["result"] == "Example Domain"


@pytest.mark.asyncio
@patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.get_result.send_to_manager")
async def test_handle_get_result_error_response(mock_send):
    """Test get-result handler with error in response."""
    mock_send.return_value = {
        "error": "Job not found"
    }
    
    result = await handle_get_ai_result({
        "job_id": "invalid_job"
    })
    
    assert result["isError"] is True
    assert "Job not found" in result["content"][0].text


@pytest.mark.asyncio
@patch("playwright_mcp.browser_daemon.tools.handlers.ai_agent.get_result.send_to_manager")
async def test_handle_get_result_exception(mock_send):
    """Test get-result handler when an exception occurs."""
    mock_send.side_effect = Exception("Connection failed")
    
    result = await handle_get_ai_result({
        "job_id": "test_job_123"
    })
    
    assert result["isError"] is True
    assert "Connection failed" in result["content"][0].text 