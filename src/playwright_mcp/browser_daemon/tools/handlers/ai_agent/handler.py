"""Handler for AI agent requests."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from ...base import ToolHandler
from .job_store import job_store


class AIAgentInput(BaseModel):
    """Input model for ai-agent tool."""
    page_id: str = Field(..., description="Page ID to analyze")
    query: str = Field(..., description="Natural language query describing what to analyze or do")
    max_actions: Optional[int] = Field(5, description="Maximum number of actions the agent can take")


class AIAgentHandler(ToolHandler):
    """Handler for ai-agent tool."""
    name = "ai-agent"
    description = (
        "Start an AI agent job to analyze and interact with a web page using natural language. "
        "Returns a job ID immediately that can be used to check the result status."
    )
    input_model = AIAgentInput

    async def handle(self, args: AIAgentInput) -> Dict[str, Any]:
        """Handle the ai-agent tool request."""
        try:
            # Create new job
            job_id = await job_store.create_job(
                page_id=args.page_id,
                query=args.query,
                max_actions=args.max_actions
            )

            return {
                "isError": False,
                "job_id": job_id,
                "message": "AI agent job started successfully"
            }

        except Exception as e:
            return {
                "isError": True,
                "error": f"Failed to start AI agent job: {str(e)}"
            }


# Create handler instance for function-based interface
_handler = AIAgentHandler()


async def handle_ai_agent(daemon, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Function-based interface for backward compatibility."""
    try:
        return await _handler.handle(AIAgentInput(**arguments))
    except Exception as e:
        return {
            "isError": True,
            "error": str(e)
        } 