from typing import Dict, Any

from .base import BaseHandler
from .ai_agent.job_store import job_store  # Import the singleton directly
from ...utils.logging import setup_logging

logger = setup_logging("get_result_handler", "get_result_handler.log")


class GetResultHandler(BaseHandler):
    def __init__(self, session_manager):
        super().__init__(session_manager)
        self.required_args = ["job_id"]

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get-result commands."""
        logger.info(f"Handling get-result command with args: {args}")
        command = args.get("command")
        
        if command == "get-ai-result":
            return await self._handle_get_result(args)
        else:
            raise Exception(f"Unknown get-result command: {command}")

    async def _handle_get_result(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get-result command."""
        if not self._validate_required_args(args, self.required_args):
            raise Exception("Missing required arguments for get-result")
        
        logger.info(f"Getting result for job {args.get('job_id')}")

        # Get job status and result using job store singleton
        job_id = args.get("job_id")
        status = await job_store.get_job_status(job_id)
        result = await job_store.get_job_result(job_id)

        logger.info(f"Got result for job {job_id}: {result}")

        return {
            "job_id": job_id,
            "status": status,
            "result": result["result"]
        }