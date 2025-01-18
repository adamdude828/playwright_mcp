"""Integration tests for AI agent functionality."""

import pytest
from playwright_mcp.browser_daemon.tools.handlers.ai_agent.job_store import job_store


@pytest.mark.asyncio
async def test_job_store_flow():
    """Test the job store flow directly."""
    # Create a job directly in the job store
    job_id = await job_store.create_job(
        page_id="test_page_123",
        query="Test query",
        max_actions=5
    )
    
    # Verify job was created
    job = job_store.get_job(job_id)
    assert job is not None, "Job not found in job store"
    assert job.id == job_id, "Job ID mismatch"
    assert job.status == "pending", f"Unexpected job status: {job.status}"
    assert job.page_id == "test_page_123", "Page ID mismatch"
    assert job.query == "Test query", "Query mismatch"
    
    # Get job status
    status = await job_store.get_job_status(job_id)
    assert status == "pending", f"Unexpected status: {status}"
    
    # Complete the job
    job_store.complete_job(job_id, {"result": "Test result"})
    
    # Verify job was completed
    job = job_store.get_job(job_id)
    assert job.status == "completed", f"Job not completed, status: {job.status}"
    assert job.result == {"result": "Test result"}, "Result mismatch"
    
    # Try to get a non-existent job
    non_existent_job = job_store.get_job("non-existent")
    assert non_existent_job is None, "Should return None for non-existent job" 