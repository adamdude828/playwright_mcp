"""Store for managing AI agent jobs and their results."""

import asyncio
from typing import Dict, Optional, Any
import uuid
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger("job_store")


@dataclass
class JobStatus:
    """Status of an AI agent job."""
    id: str
    status: str  # "running", "completed", "error"
    page_id: str
    query: str
    max_actions: Optional[int] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None


class JobStore:
    """Store for managing AI agent jobs."""
    
    def __init__(self):
        self._jobs: Dict[str, JobStatus] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        logger.info("JobStore initialized")
    
    async def create_job(self, page_id: str, query: str, max_actions: Optional[int] = None) -> str:
        """Create a new job and return its ID."""
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = JobStatus(
            id=job_id,
            status="pending",
            page_id=page_id,
            query=query,
            max_actions=max_actions
        )
        logger.info(f"Created new job with ID: {job_id}")
        logger.debug(f"Current jobs: {list(self._jobs.keys())}")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[JobStatus]:
        """Get the status of a job."""
        job = self._jobs.get(job_id)
        if job:
            logger.info(f"Retrieved job {job_id} with status: {job.status}")
        else:
            logger.warning(f"Job {job_id} not found. Current jobs: {list(self._jobs.keys())}")
        return job
    
    async def get_job_status(self, job_id: str) -> str:
        """Get the status of a job."""
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job.status
    
    async def get_job_result(self, job_id: str) -> Any:
        """Get the result of a job."""
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job.result
    
    def set_task(self, job_id: str, task: asyncio.Task) -> None:
        """Associate an asyncio task with a job."""
        self._tasks[job_id] = task
        logger.info(f"Set task for job {job_id}")
    
    def complete_job(self, job_id: str, result: Any) -> None:
        """Mark a job as completed with its result."""
        if job_id in self._jobs:
            self._jobs[job_id].status = "completed"
            self._jobs[job_id].result = result
            self._jobs[job_id].completed_at = datetime.now()
            logger.info(f"Completed job {job_id} with result")
            logger.debug(f"Result: {result}")
        else:
            logger.error(f"Attempted to complete nonexistent job {job_id}")
    
    def fail_job(self, job_id: str, error: str) -> None:
        """Mark a job as failed with an error message."""
        if job_id in self._jobs:
            self._jobs[job_id].status = "error"
            self._jobs[job_id].error = error
            self._jobs[job_id].completed_at = datetime.now()
            logger.error(f"Failed job {job_id} with error: {error}")
        else:
            logger.error(f"Attempted to fail nonexistent job {job_id}") 
    
    def set_running(self, job_id: str) -> None:
        """Set a job's status to running."""
        if job := self._jobs.get(job_id):
            job.status = "running"
            logger.info(f"Set job {job_id} status to running")
        else:
            logger.warning(f"Cannot set running status - job {job_id} not found")


# Create singleton instance
job_store = JobStore() 