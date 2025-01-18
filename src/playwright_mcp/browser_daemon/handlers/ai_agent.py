from typing import Dict, Any, Optional
import asyncio

from ..core.logging import setup_logging
from .base import BaseHandler
from ..tools.handlers.ai_agent.tools import create_agent
from ..daemon import BrowserDaemon

logger = setup_logging("ai_agent_handler")


class AIAgentHandler(BaseHandler):
    def __init__(self, session_manager):
        super().__init__(session_manager)
        self.required_args = ["page_id", "query"]

    async def handle(self, args: Dict[str, Any], daemon=None) -> Dict[str, Any]:
        """Handle AI agent commands."""
        if not daemon:
            return {"error": "Daemon instance required for AI agent operations"}
            
        command = args.get("command")
        
        if command == "ai-agent":
            return await self._handle_ai_agent(args, daemon)
        else:
            return {"error": f"Unknown AI agent command: {command}"}

    async def _handle_ai_agent(self, args: Dict[str, Any], daemon) -> Dict[str, Any]:
        """Handle AI agent command."""
        if not self._validate_required_args(args, self.required_args):
            return {"error": "Missing required arguments for AI agent"}

        try:
            # Create new job using daemon's job store
            job_id = await daemon.job_store.create_job(
                page_id=args.get("page_id"),
                query=args.get("query"),
                max_actions=args.get("max_actions", 5)
            )

            # Set job to running state immediately
            daemon.job_store.set_running(job_id)

            # Start background task to process the job
            task = asyncio.create_task(self._process_job(job_id, args, daemon))
            daemon.job_store.set_task(job_id, task)

            return {
                "job_id": job_id,
                "message": "AI agent job started successfully"
            }

        except Exception as e:
            logger.error(f"AI agent job creation failed: {e}")
            return {"error": f"Failed to start AI agent job: {e}"}

    async def _process_job(self, job_id: str, args: Dict[str, Any], daemon) -> None:
        """Process an AI agent job in the background."""
        try:
            # Get the page from session manager
            page_id = args.get("page_id")
            page = self.session_manager.get_page(page_id)
            if not page:
                raise ValueError(f"Page {page_id} not found")

            # Set job to running state
            daemon.job_store.set_running(job_id)
            
            # Create AI agent with tools
            agent = create_agent(page_id)
            
            # Run the agent with the user's query
            try:
                result = await agent.run(args.get("query"), deps=page_id)
                if isinstance(result, dict) and result.get("error"):
                    raise ValueError(result["error"])
                daemon.job_store.complete_job(job_id, result)
            except Exception as agent_error:
                logger.error(f"Agent execution failed for job {job_id}: {agent_error}")
                daemon.job_store.fail_job(job_id, str(agent_error))

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}")
            daemon.job_store.fail_job(job_id, str(e)) 