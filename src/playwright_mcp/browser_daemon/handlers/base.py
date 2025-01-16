from typing import Dict, Any, List

from ..core.session import SessionManager
from ..core.logging import setup_logging

logger = setup_logging("base_handler")


class BaseHandler:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def _validate_required_args(self, args: Dict[str, Any], required_args: List[str]) -> bool:
        """Validate that all required arguments are present."""
        return all(arg in args for arg in required_args)

    async def _get_page(self, page_id: str) -> Dict[str, Any]:
        """Get a page by its ID."""
        page = self.session_manager.get_page(page_id)
        if not page:
            return {"error": f"No page found with ID: {page_id}"}
        return {"page": page} 