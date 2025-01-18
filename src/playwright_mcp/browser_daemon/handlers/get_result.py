from typing import Dict, Any, Optional

from ..core.logging import setup_logging
from .base import BaseHandler
from ..daemon import BrowserDaemon

logger = setup_logging("get_result_handler")


class GetResultHandler(BaseHandler):
    def __init__(self, session_manager):
        super().__init__(session_manager)
        self.required_args = ["job_id"]

    async def handle(self, args: Dict[str, Any], daemon=None) -> Dict[str, Any]:
        """Handle get-result commands."""
        if not daemon:
            return {"error": "Daemon instance required for AI agent operations"}
            
        command = args.get("command")
        
        if command == "get-ai-result":
            return await self._handle_get_result(args, daemon)
        else:
            return {"error": f"Unknown get-result command: {command}"}

    async def _handle_get_result(self, args: Dict[str, Any], daemon) -> Dict[str, Any]:
        """Handle get-result command."""
        if not self._validate_required_args(args, self.required_args):
            return {"error": "Missing required arguments for get-result"}

        try:
            # Get job status and result using daemon's job store
            job_id = args.get("job_id")
            status = await daemon.job_store.get_job_status(job_id)
            result = await daemon.job_store.get_job_result(job_id)

            return {
                "job_id": job_id,
                "status": status,
                "result": result
            }

        except Exception as e:
            logger.error(f"Get result failed: {e}")
            return {"error": f"Failed to get result: {e}"}

    async def handle_get_ai_result(self, args: dict, daemon: Optional[BrowserDaemon] = None) -> dict:
        """Handle get-ai-result command."""
        if not daemon:
            return {
                "error": "Browser daemon is not running. Please call the 'start-daemon' tool first.",
                "isError": True
            }

        # Validate required arguments
        if "job_id" not in args:
            return {
                "error": "Missing required argument: job_id",
                "isError": True
            }

        job_id = args["job_id"]

        try:
            # Get job status and result
            status = await daemon.job_store.get_job_status(job_id)
            result = await daemon.job_store.get_job_result(job_id)

            return {
                "job_id": job_id,
                "status": status,
                "result": result,
                "isError": False
            }

        except Exception as e:
            return {
                "error": f"Failed to get result: {str(e)}",
                "isError": True
            } 