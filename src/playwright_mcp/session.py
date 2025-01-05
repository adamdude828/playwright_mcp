from playwright.async_api import Page, Playwright, BrowserContext
from typing import Dict


class SessionManager:
    def __init__(self):
        self.active_playwright: Dict[str, Playwright] = {}
        self.active_contexts: Dict[str, BrowserContext] = {}
        self.active_pages: Dict[str, Page] = {}

    def add_session(self, session_id: str, playwright: Playwright, context: BrowserContext):
        """Add a new browser session."""
        self.active_playwright[session_id] = playwright
        self.active_contexts[session_id] = context

    def add_page(self, page_id: str, page: Page):
        """Add a new page."""
        self.active_pages[page_id] = page

    def get_context(self, session_id: str) -> BrowserContext:
        """Get browser context by session ID."""
        if session_id not in self.active_contexts:
            raise ValueError(f"No browser session found for ID: {session_id}")
        return self.active_contexts[session_id]

    def get_page(self, page_id: str) -> Page:
        """Get page by page ID."""
        if page_id not in self.active_pages:
            raise ValueError(f"No page found for ID: {page_id}")
        return self.active_pages[page_id]

    def get_playwright(self, session_id: str) -> Playwright:
        """Get playwright instance by session ID."""
        if session_id not in self.active_playwright:
            raise ValueError(f"No playwright instance found for ID: {session_id}")
        return self.active_playwright[session_id]

    async def close_session(self, session_id: str):
        """Close a browser session and clean up resources."""
        if session_id not in self.active_contexts:
            raise ValueError(f"No browser session found for ID: {session_id}")

        context = self.active_contexts[session_id]
        playwright = self.active_playwright[session_id]

        # Close all pages associated with this context
        pages_to_remove = []
        for page_id, page in self.active_pages.items():
            if page.context == context:
                await page.close()
                pages_to_remove.append(page_id)

        for page_id in pages_to_remove:
            del self.active_pages[page_id]

        # Close context and playwright instance
        await context.close()
        await playwright.stop()

        del self.active_contexts[session_id]
        del self.active_playwright[session_id]

    async def cleanup(self):
        """Clean up all active sessions. Called when server is shutting down."""
        # Make a copy of keys since we'll be modifying the dict
        session_ids = list(self.active_contexts.keys())
        
        for session_id in session_ids:
            try:
                await self.close_session(session_id)
            except Exception as e:
                print(f"Error cleaning up session {session_id}: {e}")


# Global session manager instance
session_manager = SessionManager() 