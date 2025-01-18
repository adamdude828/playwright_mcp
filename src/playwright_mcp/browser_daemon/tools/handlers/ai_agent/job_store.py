"""Store for managing AI agent jobs and their results."""

import asyncio
from typing import Dict, Optional, Any
import uuid
from dataclasses import dataclass
from datetime import datetime
from ....core.logging import setup_logging

# Configure logging
logger = setup_logging("job_store")


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
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobStore, cls).__new__(cls)
            logger.info("Created new JobStore instance")
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._jobs: Dict[str, JobStatus] = {}
            self._tasks: Dict[str, asyncio.Task] = {}
            self._initialized = True
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
    
    async def get_job_result(self, job_id: str) -> dict:
        """Get the result of a job.
        
        Returns a dictionary containing:
        - job_id: The ID of the job
        - status: The current status ("pending", "running", "completed", "error")
        - result: The result if completed, or None
        - error: The error message if failed, or None
        """
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
            
        response = {
            "job_id": job.id,
            "status": job.status,
            "result": job.result
        }
        
        if job.status == "error":
            response["error"] = job.error
            
        return response
    
    def set_task(self, job_id: str, task: asyncio.Task) -> None:
        """Set the task for a job."""
        self._tasks[job_id] = task
        logger.info(f"Set task for job {job_id}")
    
    def get_task(self, job_id: str) -> Optional[asyncio.Task]:
        """Get the task for a job."""
        return self._tasks.get(job_id)
    
    def set_running(self, job_id: str) -> None:
        """Set a job's status to running."""
        job = self.get_job(job_id)
        if job:
            job.status = "running"
            logger.info(f"Set job {job_id} to running")
    
    def complete_job(self, job_id: str, result: Any) -> None:
        """Complete a job with its result."""
        job = self.get_job(job_id)
        if job:
            job.status = "completed"
            job.result = result
            job.completed_at = datetime.now()
            logger.info(f"Completed job {job_id} with result")
            logger.debug(f"Result: {result}")
    
    def fail_job(self, job_id: str, error: str) -> None:
        """Mark a job as failed with an error message."""
        job = self.get_job(job_id)
        if job:
            job.status = "error"
            job.error = error
            job.completed_at = datetime.now()
            logger.error(f"Job {job_id} failed: {error}")


# Create singleton instance
job_store = JobStore()
logger.info("Created job_store singleton instance") 