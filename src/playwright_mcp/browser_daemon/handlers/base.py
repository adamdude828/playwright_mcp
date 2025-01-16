from abc import ABC, abstractmethod
from typing import Dict, Any

from ..core.session import SessionManager
from ..core.logging import setup_logging

logger = setup_logging("handlers")


class BaseHandler(ABC):
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    @abstractmethod
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a command with the given arguments."""
        pass

    def _validate_required_args(self, args: Dict[str, Any], required: list) -> bool:
        """Validate that all required arguments are present."""
        missing = [arg for arg in required if arg not in args]
        if missing:
            logger.error(f"Missing required arguments: {missing}")
            return False
        return True

    async def _get_page(self, page_id: str) -> Dict[str, Any]:
        """Get a page by ID and return error response if not found."""
        page = self.session_manager.get_page(page_id)
        if not page:
            return {"error": f"No page found for ID: {page_id}"}
        return {"page": page} 