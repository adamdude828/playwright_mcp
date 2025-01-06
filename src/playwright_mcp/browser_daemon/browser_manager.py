import asyncio
from asyncio import StreamReader, StreamWriter
from playwright.async_api import async_playwright, BrowserContext, Page
import tempfile
from typing import Dict
import os
import logging
import logging.handlers
import json


def setup_logging(logger_name: str) -> logging.Logger:
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Get or create logger
    logger = logging.getLogger(logger_name)
    
    # Set level based on environment variable
    level = os.getenv("LOG_LEVEL", "ERROR")
    level = getattr(logging, level.upper())
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"{logger_name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(console_handler)

    return logger


logger = setup_logging("browser_manager")


class BrowserManager:
    def __init__(self):
        self.sessions: Dict[str, BrowserContext] = {}
        self.active_pages: Dict[str, Page] = {}
        self.playwright = None
        self._shutdown_task = None
        self._socket_path = os.path.join(tempfile.gettempdir(), 'playwright_mcp.sock')
        self.SHUTDOWN_DELAY = int(os.getenv('PLAYWRIGHT_MCP_SHUTDOWN_DELAY', 3600))  # Default 1 hour
        self._last_activity = asyncio.get_event_loop().time()

    async def _check_auto_shutdown(self):
        """Check if we should shut down due to inactivity."""
        while True:
            await asyncio.sleep(60)  # Check every minute
            current_time = asyncio.get_event_loop().time()
            
            if not self.sessions and (current_time - self._last_activity) > self.SHUTDOWN_DELAY:
                logger.info("No active browser sessions for over an hour, initiating shutdown...")
                await self.shutdown()
                break

    async def _update_activity(self):
        """Update the last activity timestamp."""
        self._last_activity = asyncio.get_event_loop().time()

    async def start_server(self):
        """Start the browser manager server."""
        # Remove existing socket if it exists
        try:
            os.unlink(self._socket_path)
        except OSError:
            if os.path.exists(self._socket_path):
                raise

        server = await asyncio.start_unix_server(
            self.handle_connection, self._socket_path
        )

        logger.info(f"Browser manager listening on {self._socket_path}")
        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader: StreamReader, writer: StreamWriter):
        """Handle a connection from the MCP server."""
        try:
            data = await reader.readline()
            if not data:
                return

            request = json.loads(data.decode())
            logger.debug(f"Received request: {request}")
            
            command = request.get("command")
            args = request.get("args", {})
            
            if command == "navigate":
                response = await self.handle_navigate(args)
            elif command == "ping":
                response = {"result": "pong"}
            elif command == "new-tab":
                session_id = args.get("session_id")
                if session_id not in self.sessions:
                    response = {"error": "invalid session id"}
                else:
                    browser = self.sessions[session_id]
                    page = await browser.new_page()
                    page_id = f"page_{id(page)}"
                    self.active_pages[page_id] = page
                    response = {"page_id": page_id}
            elif command == "close-browser":
                session_id = args.get("session_id")
                success = await self.close_browser(session_id)
                response = {"success": success}
            elif command == "close-tab":
                page_id = args.get("page_id")
                if page_id not in self.active_pages:
                    response = {"error": "invalid page id"}
                else:
                    page = self.active_pages[page_id]
                    await page.close()
                    del self.active_pages[page_id]
                    response = {"success": True}
            else:
                response = {"error": "unknown command"}
            
            writer.write(json.dumps(response).encode() + b"\n")
            await writer.drain()
        except Exception as e:
            logger.error(f"Error handling connection: {e}")
            writer.write(json.dumps({"error": str(e)}).encode() + b"\n")
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    async def handle_navigate(self, args: dict) -> dict:
        """Handle navigate command by combining launch, new page, and goto functionality."""
        await self._update_activity()
        
        try:
            # Get or create browser session
            session_id = args.get("session_id")
            created_session = False
            if not session_id or session_id not in self.sessions:
                browser_type = args.get("browser_type", "chromium")
                headless = args.get("headless", True)
                session_id = await self.launch_browser(browser_type, headless)
                created_session = True

            browser = self.sessions[session_id]
            
            # Get or create page
            page_id = args.get("page_id")
            created_page = False
            if not page_id or page_id not in self.active_pages:
                page = await browser.new_page()
                page_id = f"page_{id(page)}"
                self.active_pages[page_id] = page
                created_page = True
            
            page = self.active_pages[page_id]
            
            # Navigate to URL and wait for network idle
            await page.goto(args["url"], wait_until="networkidle")
            
            response = {
                "session_id": session_id,
                "page_id": page_id,
                "created_session": created_session,
                "created_page": created_page
            }

            # Take screenshot if path provided
            if screenshot_path := args.get("screenshot_path"):
                await page.screenshot(path=screenshot_path, full_page=True)
                response["screenshot_path"] = screenshot_path

            # If analysis is requested, perform it
            if args.get("analyze_after_navigation"):
                from .tools.page_analyzer import get_page_elements_map
                elements_map = await get_page_elements_map(page)
                response["analysis"] = elements_map

            return response
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"error": str(e)}

    async def launch_browser(self, browser_type: str, headless: bool = True) -> str:
        """Launch a browser and return its session ID."""
        await self._update_activity()
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

    async def close_browser(self, session_id: str) -> bool:
        """Close a browser session."""
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
        """Shutdown the browser manager and cleanup resources."""
        logger.info("Shutting down browser manager...")
        for session_id in list(self.sessions.keys()):
            await self.close_browser(session_id)
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

        # Remove the socket file
        if os.path.exists(self._socket_path):
            os.unlink(self._socket_path)

        # Exit the process
        os._exit(0)


async def main():
    logger.info("Starting browser manager service")
    manager = BrowserManager()
    await manager.start_server()


if __name__ == "__main__":
    asyncio.run(main())
