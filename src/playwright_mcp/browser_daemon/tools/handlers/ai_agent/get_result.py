"""Handler for getting AI agent results."""

from typing import Dict, Any
from pydantic import BaseModel, Field
from ...base import ToolHandler


class GetAIResultInput(BaseModel):
    """Input model for get-ai-result tool."""
    job_id: str = Field(..., description="ID of the job to check")


class GetAIResultHandler(ToolHandler):
    """Handler for get-ai-result tool."""
    name = "get-ai-result"
    description = (
        "Get the result of a previously started AI agent job. "
        "Returns the job status and result if completed."
    )
    input_model = GetAIResultInput

    async def handle(self, args: GetAIResultInput, daemon=None) -> Dict[str, Any]:
        """Handle the get-ai-result tool request."""
        try:
            # Get job status and result
            status = await daemon.job_store.get_job_status(args.job_id)
            result = await daemon.job_store.get_job_result(args.job_id)

            return {
                "isError": False,
                "job_status": status,
                "result": result
            }

        except Exception as e:
            return {
                "isError": True,
                "error": f"Failed to get AI agent job result: {str(e)}"
            }


# Create handler instance for function-based interface
_handler = GetAIResultHandler()


async def handle_get_ai_result(arguments: Dict[str, Any], daemon=None) -> Dict[str, Any]:
    """Function-based interface for backward compatibility."""
    try:
        return await _handler.handle(GetAIResultInput(**arguments), daemon=daemon)
    except Exception as e:
        return {
            "isError": True,
            "error": str(e)
        } 