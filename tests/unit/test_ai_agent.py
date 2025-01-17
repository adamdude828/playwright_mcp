"""Tests for AI agent handlers."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
import asyncio

from playwright_mcp.browser_daemon.tools.handlers.ai_agent.job_store import JobStore, job_store, JobStatus
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.handler import handle_ai_agent
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.get_result import handle_get_ai_result


@pytest.fixture
def mock_daemon():
    """Create a mock daemon with job store."""
    daemon = Mock()
    daemon.job_store = JobStore()
    return daemon


@pytest.fixture
def clean_job_store():
    """Create a fresh job store for each test."""
    store = JobStore()
    return store


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
    assert job.completed_at is None
    assert job.error is None
    assert job.result is None


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
    assert job.error is None


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
    assert job.result is None


def test_job_store_set_running():
    """Test setting job to running state."""
    store = JobStore()
    job_id = asyncio.run(store.create_job(
        page_id="test_page",
        query="test query"
    ))
    store.set_running(job_id)
    job = store.get_job(job_id)
    assert job.status == "running"
    assert job.completed_at is None


def test_job_store_set_running_nonexistent():
    """Test setting running state for non-existent job."""
    store = JobStore()
    store.set_running("nonexistent")
    # Should not raise an exception, just log a warning


def test_job_store_complete_nonexistent():
    """Test completing a non-existent job."""
    store = JobStore()
    store.complete_job("nonexistent", {"result": "test"})
    # Should not raise an exception, just log an error


def test_job_store_fail_nonexistent():
    """Test failing a non-existent job."""
    store = JobStore()
    store.fail_job("nonexistent", "error")
    # Should not raise an exception, just log an error


@pytest.mark.asyncio
async def test_job_store_get_status_nonexistent():
    """Test getting status of non-existent job."""
    store = JobStore()
    with pytest.raises(ValueError, match="Job .* not found"):
        await store.get_job_status("nonexistent")


@pytest.mark.asyncio
async def test_job_store_get_result_nonexistent():
    """Test getting result of non-existent job."""
    store = JobStore()
    with pytest.raises(ValueError, match="Job .* not found"):
        await store.get_job_result("nonexistent")


def test_job_store_set_task():
    """Test associating a task with a job."""
    store = JobStore()
    job_id = asyncio.run(store.create_job(
        page_id="test_page",
        query="test query"
    ))
    mock_task = Mock(spec=asyncio.Task)
    store.set_task(job_id, mock_task)
    assert store._tasks[job_id] == mock_task


@pytest.mark.asyncio
async def test_job_store_concurrent_jobs():
    """Test handling multiple concurrent jobs."""
    store = JobStore()
    
    # Create multiple jobs
    job_ids = []
    for i in range(3):
        job_id = await store.create_job(
            page_id=f"page_{i}",
            query=f"query_{i}"
        )
        job_ids.append(job_id)
    
    # Set different states
    store.set_running(job_ids[0])
    store.complete_job(job_ids[1], {"result": "test"})
    store.fail_job(job_ids[2], "error")
    
    # Verify states
    assert (await store.get_job_status(job_ids[0])) == "running"
    assert (await store.get_job_status(job_ids[1])) == "completed"
    assert (await store.get_job_status(job_ids[2])) == "error"


def test_job_store_singleton():
    """Test that job store singleton maintains state."""
    # Use the singleton instance
    job_id = asyncio.run(job_store.create_job(
        page_id="test_page",
        query="test query"
    ))
    
    # Create a new reference to the singleton
    another_store = JobStore()
    
    # Both should see the same job
    assert job_store.get_job(job_id) == another_store.get_job(job_id)


def test_job_status_dataclass():
    """Test JobStatus dataclass initialization and attributes."""
    status = JobStatus(
        id="test_id",
        status="pending",
        page_id="test_page",
        query="test_query",
        max_actions=5
    )
    
    assert status.id == "test_id"
    assert status.status == "pending"
    assert status.page_id == "test_page"
    assert status.query == "test_query"
    assert status.max_actions == 5
    assert status.result is None
    assert status.error is None
    assert isinstance(status.created_at, datetime)
    assert status.completed_at is None


@pytest.mark.asyncio
async def test_handle_ai_agent_missing_page_id():
    """Test AI agent handler with missing page_id."""
    result = await handle_ai_agent({
        "query": "test query"
    })
    assert result["isError"] is True
    assert "page_id" in result["error"]


@pytest.mark.asyncio
async def test_handle_ai_agent_missing_query():
    """Test AI agent handler with missing query."""
    result = await handle_ai_agent({
        "page_id": "test_page"
    })
    assert result["isError"] is True
    assert "query" in result["error"]


@pytest.mark.asyncio
async def test_handle_ai_agent_success():
    """Test successful AI agent job creation."""
    result = await handle_ai_agent({
        "page_id": "test_page",
        "query": "test query"
    })
    assert result["isError"] is False
    assert "job_id" in result


@pytest.mark.asyncio
async def test_handle_ai_agent_with_daemon():
    """Test AI agent handler with daemon parameter."""
    mock_daemon = Mock()
    result = await handle_ai_agent({
        "page_id": "test_page",
        "query": "test query"
    }, daemon=mock_daemon)
    assert result["isError"] is False
    assert "job_id" in result


@pytest.mark.asyncio
async def test_handle_get_ai_result_missing_job_id():
    """Test get-ai-result handler with missing job_id."""
    result = await handle_get_ai_result({})
    assert result["isError"] is True
    assert "job_id" in result["error"]


@pytest.mark.asyncio
async def test_handle_get_ai_result_not_found():
    """Test get-ai-result handler with non-existent job."""
    mock_daemon = Mock()
    mock_daemon.job_store = Mock()
    mock_daemon.job_store.get_job_status = AsyncMock(side_effect=ValueError("Job not found"))
    mock_daemon.job_store.get_job_result = AsyncMock(side_effect=ValueError("Job not found"))
    
    result = await handle_get_ai_result({
        "job_id": "non_existent"
    }, daemon=mock_daemon)
    assert result["isError"] is True
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_handle_get_ai_result_success():
    """Test successful retrieval of job result."""
    # Create a mock daemon with mock job store
    mock_daemon = Mock()
    mock_daemon.job_store = Mock()
    mock_daemon.job_store.get_job_status = AsyncMock(return_value="completed")
    mock_daemon.job_store.get_job_result = AsyncMock(return_value={"test": "result"})

    result = await handle_get_ai_result({
        "job_id": "test_job"
    }, daemon=mock_daemon)
    
    assert result["isError"] is False
    assert result["job_status"] == "completed"
    assert result["result"] == {"test": "result"}


@pytest.mark.asyncio
async def test_handle_get_ai_result_without_daemon():
    """Test get-ai-result handler without daemon parameter."""
    result = await handle_get_ai_result({
        "job_id": "test_job"
    })
    assert result["isError"] is True
    assert "job_store" in result["error"].lower() 