import asyncio
from typing import Dict, Optional
from playwright.async_api import async_playwright, BrowserContext, Page

from .logging import setup_logging

logger = setup_logging("session_manager")


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, BrowserContext] = {}
        self.active_pages: Dict[str, Page] = {}
        self.playwright = None
        self._shutdown_task = None
        self.SHUTDOWN_DELAY = int(asyncio.get_event_loop().get_debug())  # Default 1 hour

    async def _check_auto_shutdown(self):
        """Check if we should shut down due to inactivity."""
        while True:
            await asyncio.sleep(60)  # Check every minute
            current_time = asyncio.get_event_loop().time()
            
            if not self.sessions and (current_time - self._last_activity) > self.SHUTDOWN_DELAY:
                logger.info("No active browser sessions for over an hour, initiating shutdown...")
                await self.shutdown()
                break

    async def launch_browser(self, browser_type: str, headless: bool = True) -> str:
        """Launch a browser and return its session ID."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        browser_class = getattr(self.playwright, browser_type)
        browser = await browser_class.launch(headless=headless)
        session_id = f"{browser_type}_{id(browser)}"
        self.sessions[session_id] = browser

        # Start shutdown checker if it's not running
        if not self._shutdown_task or self._shutdown_task.done():
            self._shutdown_task = asyncio.create_task(self._check_auto_shutdown())

        return session_id

    async def new_page(self, session_id: str) -> Optional[str]:
        """Create a new page in the given browser session."""
        if session_id not in self.sessions:
            logger.error(f"No browser session found for ID: {session_id}")
            return None

        browser = self.sessions[session_id]
        page = await browser.new_page()
        page_id = f"page_{id(page)}"
        self.active_pages[page_id] = page
        return page_id

    def get_page(self, page_id: str) -> Optional[Page]:
        """Get a page by its ID."""
        return self.active_pages.get(page_id)

    async def close_page(self, page_id: str) -> bool:
        """Close a page by its ID."""
        if page_id in self.active_pages:
            page = self.active_pages[page_id]
            await page.close()
            del self.active_pages[page_id]
            return True
        return False

    async def close_browser(self, session_id: str) -> bool:
        """Close a browser session and all its pages."""
        if session_id in self.sessions:
            browser = self.sessions[session_id]
            
            # Close all pages associated with this browser
            pages_to_remove = []
            for page_id, page in self.active_pages.items():
                if page.context == browser:
                    await page.close()
                    pages_to_remove.append(page_id)
            
            for page_id in pages_to_remove:
                del self.active_pages[page_id]
            
            await browser.close()
            del self.sessions[session_id]
            return True
        return False

    async def shutdown(self):
        """Shutdown all browser sessions and cleanup resources."""
        logger.info("Shutting down session manager...")
        for session_id in list(self.sessions.keys()):
            await self.close_browser(session_id)
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None 