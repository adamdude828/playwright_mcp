"""Session management module."""
from playwright.async_api import Page, Playwright, BrowserContext
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Any] = {}
        self.pages: Dict[str, Any] = {}
        logger.debug("SessionManager initialized")

    def cleanup_session(self, session_id: str) -> None:
        """Clean up a browser session and its resources."""
        try:
            if session_id in self.sessions:
                # Clean up pages first
                pages_to_remove = []
                for page_id, page in self.pages.items():
                    if page.get("session_id") == session_id:
                        pages_to_remove.append(page_id)
                
                for page_id in pages_to_remove:
                    self.pages.pop(page_id, None)
                
                # Clean up the session
                self.sessions.pop(session_id, None)
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")

    def add_session(self, session_id: str, playwright: Playwright, context: BrowserContext):
        """Add a new browser session."""
        self.sessions[session_id] = {
            "playwright": playwright,
            "context": context
        }

    def add_page(self, page_id: str, page: Page):
        """Add a new page."""
        self.pages[page_id] = {
            "page": page,
            "session_id": page.context.session_id
        }

    def get_context(self, session_id: str) -> BrowserContext:
        """Get browser context by session ID."""
        if session_id not in self.sessions:
            raise ValueError(f"No browser session found for ID: {session_id}")
        return self.sessions[session_id]["context"]

    def get_page(self, page_id: str) -> Page:
        """Get page by page ID."""
        if page_id not in self.pages:
            raise ValueError(f"No page found for ID: {page_id}")
        return self.pages[page_id]["page"]

    def get_playwright(self, session_id: str) -> Playwright:
        """Get playwright instance by session ID."""
        if session_id not in self.sessions:
            raise ValueError(f"No playwright instance found for ID: {session_id}")
        return self.sessions[session_id]["playwright"]

    async def close_session(self, session_id: str):
        """Close a browser session and clean up resources."""
        if session_id not in self.sessions:
            raise ValueError(f"No browser session found for ID: {session_id}")

        context = self.sessions[session_id]["context"]
        playwright = self.sessions[session_id]["playwright"]

        # Close all pages associated with this context
        pages_to_remove = []
        for page_id, page in self.pages.items():
            if page["session_id"] == session_id:
                await page["page"].close()
                pages_to_remove.append(page_id)

        for page_id in pages_to_remove:
            self.pages.pop(page_id, None)

        # Close context and playwright instance
        await context.close()
        await playwright.stop()

        self.sessions.pop(session_id, None)

    async def cleanup(self):
        """Clean up all active sessions. Called when server is shutting down."""
        # Make a copy of keys since we'll be modifying the dict
        session_ids = list(self.sessions.keys())

        for session_id in session_ids:
            try:
                await self.close_session(session_id)
            except Exception as e:
                logger.error(f"Error cleaning up session {session_id}: {e}")


# Global session manager instance
session_manager = SessionManager()
