"""AI agent handler module."""
from typing import Dict, Any
import asyncio

from ....utils.logging import setup_logging
from ..base import BaseHandler
from .tools import create_agent
from .job_store import job_store  # Import the singleton directly
# from pydantic_ai.usage import UsageLimits

# Set up logging properly using project's utility
logger = setup_logging("playwright_mcp.browser_daemon.handlers.ai_agent", "ai_agent_log.log")


class AIAgentHandler(BaseHandler):
    def __init__(self, session_manager):
        super().__init__(session_manager)
        self.required_args = ["page_id", "query"]

    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI agent commands."""
        command = args.get("command")
        logger.debug(f"Handling command: {command} with args: {args}")
        
        if command == "ai-agent":
            return await self._handle_ai_agent(args)
        else:
            logger.error(f"Unknown AI agent command: {command}")
            raise Exception(f"Unknown AI agent command: {command}")

    async def _handle_ai_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI agent command."""
        logger.debug("Starting _handle_ai_agent method")
        if not self._validate_required_args(args, self.required_args):
            logger.error(f"Missing required arguments: {self.required_args}")
            raise Exception("Missing required arguments for AI agent")

        try:
            # Get async parameter with default True for backward compatibility
            is_async = args.get("async", True)
            logger.debug(f"Running in {'async' if is_async else 'sync'} mode")

            if is_async:
                # Create a new job in the job store using singleton
                job_id = await job_store.create_job(
                    page_id=args["page_id"],
                    query=args["query"],
                    max_actions=args.get("max_actions", 5)
                )
                logger.info(f"Created job {job_id} for AI agent request")

                # Start the AI agent processing in the background
                async def process_job():
                    try:
                        # Create agent with page_id
                        agent = create_agent(args["page_id"])
                        # Set job to running
                        job_store.set_running(job_id)
                        # Run the agent with the query and usage limits
                        result = await agent.run(
                            args["query"], 
                            deps=args["page_id"]
                        )
                        logger.info(f"AI agent job {job_id} completed with result: {result.data}")
                        job_store.complete_job(job_id, result.data)
                    except Exception as e:
                        logger.error(f"Error in AI agent job {job_id}: {e}", exc_info=True)
                        job_store.fail_job(job_id, str(e))

                # Start processing in background and store the task
                task = asyncio.create_task(process_job())
                job_store.set_task(job_id, task)

                # Return job ID to client
                return {
                    "status": "running",
                    "job_id": job_id,
                    "message": "Job started successfully"
                }
            else:
                # Run synchronously - no job creation needed
                try:
                    # Create agent with page_id
                    agent = create_agent(args["page_id"])
                    # Run the agent with the query and usage limits
                    result = await agent.run(
                        args["query"], 
                        deps=args["page_id"]
                    )
                    logger.info(f"AI agent job {job_id} completed with result: {result['result']}")
                    return {
                        "status": "completed",
                        "result": result["result"],
                        "message": "Query completed successfully"
                    }
                except Exception as e:
                    logger.error(f"Error in sync AI agent execution: {e}", exc_info=True)
                    return {
                        "status": "error",
                        "error": str(e),
                        "message": "Query failed"
                    }

        except Exception as e:
            logger.error(f"Error handling AI agent request: {e}", exc_info=True)
            raise Exception(f"Error handling AI agent request: {str(e)}") 