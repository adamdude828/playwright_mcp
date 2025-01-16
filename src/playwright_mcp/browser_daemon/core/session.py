"""Session management module."""
from typing import Dict, Optional
from playwright.async_api import Browser, Page, async_playwright
from .logging import setup_logging

logger = setup_logging("session")


class SessionManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.sessions: Dict[str, Browser] = {}
            self.pages: Dict[str, Page] = {}
            self.playwright = None
            self._initialized = True
            logger.debug("SessionManager initialized")

    @classmethod
    def get_instance(cls) -> 'SessionManager':
        """Get the singleton instance of SessionManager."""
        if cls._instance is None:
            cls._instance = SessionManager()
        return cls._instance

    async def _launch_browser(self, browser_type: str, headless: bool) -> Browser:
        """Internal method to launch browser - can be mocked for testing."""
        if not self.playwright:
            logger.debug("Starting playwright")
            self.playwright = await async_playwright().start()
            
        logger.debug(f"Launching {browser_type} browser (headless: {headless})")
        browser_class = getattr(self.playwright, browser_type)
        return await browser_class.launch(headless=headless)

    async def launch_browser(self, browser_type: str = "chromium", headless: bool = True) -> str:
        """Launch a browser and return its session ID."""
        browser = await self._launch_browser(browser_type, headless)
        session_id = f"{browser_type}_{id(browser)}"
        self.sessions[session_id] = browser
        logger.debug(f"Browser launched with session_id: {session_id}")
        return session_id

    async def new_page(self, session_id: str) -> Optional[str]:
        """Create a new page in the given browser session."""
        browser = self.get_session(session_id)
        if not browser:
            logger.error(f"No browser found for session_id: {session_id}")
            return None
            
        logger.debug(f"Creating new page in session: {session_id}")
        page = await browser.new_page()
        page_id = f"page_{id(page)}"
        self.pages[page_id] = page
        logger.debug(f"Created page with ID: {page_id}")
        logger.debug(f"Current pages: {list(self.pages.keys())}")
        return page_id

    def get_page(self, page_id: str) -> Optional[Page]:
        """Get a page by its ID."""
        page = self.pages.get(page_id)
        logger.debug(f"Getting page {page_id}: {'found' if page else 'not found'}")
        logger.debug(f"Available pages: {list(self.pages.keys())}")
        return page

    def add_page(self, page_id: str, page: Page):
        """Add a page to the session manager."""
        logger.debug(f"Adding page {page_id}")
        self.pages[page_id] = page
        logger.debug(f"Current pages: {list(self.pages.keys())}")

    def remove_page(self, page_id: str):
        """Remove a page from the session manager."""
        if page_id in self.pages:
            logger.debug(f"Removing page {page_id}")
            del self.pages[page_id]
            logger.debug(f"Current pages: {list(self.pages.keys())}")

    def get_session(self, session_id: str) -> Optional[Browser]:
        """Get a browser session by its ID."""
        session = self.sessions.get(session_id)
        logger.debug(f"Getting session {session_id}: {'found' if session else 'not found'}")
        return session

    def add_session(self, session_id: str, browser: Browser):
        """Add a browser session to the session manager."""
        logger.debug(f"Adding session {session_id}")
        self.sessions[session_id] = browser

    def remove_session(self, session_id: str):
        """Remove a browser session from the session manager."""
        if session_id in self.sessions:
            logger.debug(f"Removing session {session_id}")
            del self.sessions[session_id]

    async def close_page(self, page_id: str) -> bool:
        """Close a page by its ID."""
        page = self.get_page(page_id)
        if page:
            logger.debug(f"Closing page {page_id}")
            await page.close()
            self.remove_page(page_id)
            return True
        return False

    async def close_browser(self, session_id: str) -> bool:
        """Close a browser session and all its pages."""
        browser = self.get_session(session_id)
        if browser:
            logger.debug(f"Closing browser session {session_id}")
            await browser.close()
            self.remove_session(session_id)
            return True
        return False

    async def shutdown(self):
        """Close all browser sessions."""
        logger.debug("Shutting down all sessions")
        for browser in self.sessions.values():
            await browser.close()
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        self.sessions.clear()
        self.pages.clear()
        logger.debug("Shutdown complete")


# Create the singleton instance
session_manager = SessionManager.get_instance() 