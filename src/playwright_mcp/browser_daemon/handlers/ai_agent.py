"""AI agent handler module."""
from typing import Dict, Any
import asyncio

from ...utils.logging import setup_logging
from .base import BaseHandler
from ..tools.handlers.ai_agent.tools import create_agent
from pydantic_ai.usage import UsageLimits

# Set up logging properly using project's utility
logger = setup_logging("playwright_mcp.browser_daemon.handlers.ai_agent")


class AIAgentHandler(BaseHandler):
    def __init__(self, session_manager):
        super().__init__(session_manager)
        self.required_args = ["page_id", "query"]

    async def handle(self, args: Dict[str, Any], daemon=None) -> Dict[str, Any]:
        """Handle AI agent commands."""
        if not daemon:
            logger.error("Daemon instance required for AI agent operations")
            return {"error": "Daemon instance required for AI agent operations"}
            
        command = args.get("command")
        logger.debug(f"Handling command: {command} with args: {args}")
        
        if command == "ai-agent":
            return await self._handle_ai_agent(args, daemon)
        else:
            logger.error(f"Unknown AI agent command: {command}")
            return {"error": f"Unknown AI agent command: {command}"}

    async def _handle_ai_agent(self, args: Dict[str, Any], daemon) -> Dict[str, Any]:
        """Handle AI agent command."""
        logger.debug("Starting _handle_ai_agent method")
        if not self._validate_required_args(args, self.required_args):
            logger.error(f"Missing required arguments: {self.required_args}")
            return {"error": "Missing required arguments for AI agent"}

        try:
            # Create a new job in the job store
            job_id = await daemon.job_store.create_job(
                page_id=args["page_id"],
                query=args["query"],
                max_actions=args.get("max_actions", 5)
            )
            logger.info(f"Created job {job_id} for AI agent request")

            # Start the AI agent processing in the background
            async def process_job():
                try:
                    logger.debug("Creating AI agent")
                    # Create and run the AI agent
                    agent = create_agent(args["page_id"])
                    logger.debug(f"Created agent for page {args['page_id']}")
                    
                    logger.debug(f"Running AI agent with query: {args['query']}")
                    result = await agent.run(
                        args["query"], 
                        deps=args["page_id"],
                        usage_limits=UsageLimits(request_limit=25)
                    )
                    logger.debug(f"Agent run completed, result type: {type(result)}")
                    
                    if isinstance(result, Exception):
                        logger.error(f"AI agent execution failed: {result}")
                        daemon.job_store.fail_job(job_id, str(result))
                    else:
                        logger.info(f"AI agent execution successful: {result}")
                        daemon.job_store.complete_job(job_id, result.data)
                        
                except Exception as e:
                    logger.error(f"AI agent execution failed with exception: {e}", exc_info=True)
                    daemon.job_store.fail_job(job_id, str(e))

            # Start the background task
            task = asyncio.create_task(process_job())
            daemon.job_store.set_task(job_id, task)
            daemon.job_store.set_running(job_id)
            
            # Return the job ID immediately
            return {
                "job_id": job_id,
                "status": "running",
                "message": "AI agent job started successfully"
            }

        except Exception as e:
            logger.error(f"AI agent execution failed with exception: {e}", exc_info=True)
            return {"error": f"AI agent execution failed: {str(e)}"} 