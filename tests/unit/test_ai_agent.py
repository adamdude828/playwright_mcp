"""Tests for AI agent handlers."""

import pytest
from unittest.mock import Mock
from datetime import datetime
import asyncio

from playwright_mcp.browser_daemon.tools.handlers.ai_agent.job_store import JobStore
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.handler import handle_ai_agent
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.get_result import handle_get_ai_result


@pytest.fixture
def mock_daemon():
    """Create a mock daemon with job store."""
    daemon = Mock()
    daemon.job_store = JobStore()
    return daemon


def test_job_store_create_job():
    """Test job store creation."""
    store = JobStore()
    job_id = asyncio.run(store.create_job(
        page_id="test_page",
        query="test query"
    ))
    assert job_id is not None
    job = store.get_job(job_id)
    assert job.id == job_id
    assert job.status == "pending"
    assert isinstance(job.created_at, datetime)
    assert job.page_id == "test_page"
    assert job.query == "test query"


def test_job_store_complete_job():
    """Test job store completion."""
    store = JobStore()
    job_id = asyncio.run(store.create_job(
        page_id="test_page",
        query="test query"
    ))
    result = {"test": "result"}
    store.complete_job(job_id, result)
    job = store.get_job(job_id)
    assert job.status == "completed"
    assert job.result == result
    assert isinstance(job.completed_at, datetime)


def test_job_store_fail_job():
    """Test job store failure."""
    store = JobStore()
    job_id = asyncio.run(store.create_job(
        page_id="test_page",
        query="test query"
    ))
    error = "Test error"
    store.fail_job(job_id, error)
    job = store.get_job(job_id)
    assert job.status == "error"
    assert job.error == error
    assert isinstance(job.completed_at, datetime)


@pytest.mark.asyncio
async def test_handle_ai_agent_missing_page_id(mock_daemon):
    """Test AI agent handler with missing page_id."""
    result = await handle_ai_agent(mock_daemon, {
        "query": "test query"
    })
    assert result["isError"] is True
    assert "page_id" in result["error"]


@pytest.mark.asyncio
async def test_handle_ai_agent_missing_query(mock_daemon):
    """Test AI agent handler with missing query."""
    result = await handle_ai_agent(mock_daemon, {
        "page_id": "test_page"
    })
    assert result["isError"] is True
    assert "query" in result["error"]


@pytest.mark.asyncio
async def test_handle_ai_agent_success(mock_daemon):
    """Test successful AI agent job creation."""
    result = await handle_ai_agent(mock_daemon, {
        "page_id": "test_page",
        "query": "test query"
    })
    assert result["isError"] is False
    assert "job_id" in result


@pytest.mark.asyncio
async def test_handle_get_ai_result_missing_job_id(mock_daemon):
    """Test get-ai-result handler with missing job_id."""
    result = await handle_get_ai_result(mock_daemon, {})
    assert result["isError"] is True
    assert "job_id" in result["error"]


@pytest.mark.asyncio
async def test_handle_get_ai_result_not_found(mock_daemon):
    """Test get-ai-result handler with non-existent job."""
    result = await handle_get_ai_result(mock_daemon, {
        "job_id": "non_existent"
    })
    assert result["isError"] is True
    assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_handle_get_ai_result_success(mock_daemon):
    """Test successful retrieval of job result."""
    # Create a job first
    job_id = await mock_daemon.job_store.create_job(
        page_id="test_page",
        query="test query"
    )
    test_result = {"test": "result"}
    mock_daemon.job_store.complete_job(job_id, test_result)

    result = await handle_get_ai_result(mock_daemon, {
        "job_id": job_id
    })
    assert result["isError"] is False
    assert result["job_status"] == "completed"
    assert result["result"] == test_result 