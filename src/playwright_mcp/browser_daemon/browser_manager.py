import asyncio
import json
from asyncio import StreamReader, StreamWriter
from playwright.async_api import async_playwright, BrowserContext, Page, Playwright
import tempfile
from typing import Dict
import os
import traceback
import logging
import logging.handlers


def setup_logging():
    """Set up logging configuration."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "browser_manager.log")

    # Configure logging
    logger = logging.getLogger("browser_manager")
    logger.setLevel(logging.DEBUG)

    # File handler with rotation
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logging()


class BrowserManager:
    def __init__(self):
        self.active_playwright: Dict[str, Playwright] = {}
        self.active_contexts: Dict[str, BrowserContext] = {}
        self.active_pages: Dict[str, Page] = {}
        self._socket_path = os.path.join(tempfile.gettempdir(), 'playwright_mcp.sock')

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
        while True:
            try:
                data = await reader.readline()
                if not data:
                    break

                logger.debug(f"Received request: {data.decode()}")
                request = json.loads(data.decode())
                response = await self.handle_request(request)
                logger.debug(f"Sending response: {response}")

                writer.write(json.dumps(response).encode() + b'\n')
                await writer.drain()
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                logger.error(traceback.format_exc())
                writer.write(json.dumps({"error": str(e)}).encode() + b'\n')
                await writer.drain()

    async def handle_request(self, request: dict) -> dict:
        """Handle a request from the MCP server."""
        command = request.get("command")
        args = request.get("args", {})
        logger.info(f"Processing command: {command} with args: {args}")

        if command == "launch":
            return await self._launch_browser(args)
        elif command == "new_page":
            return await self._new_page(args)
        elif command == "goto":
            return await self._goto(args)
        elif command == "close":
            return await self._close_browser(args)
        elif command == "close_page":
            return await self._close_page(args)
        else:
            return {"error": f"Unknown command: {command}"}

    async def _launch_browser(self, args: dict) -> dict:
        """Launch a new browser instance."""
        try:
            browser_type = args.get("browser_type")
            headless = args.get("headless", True)
            logger.info(f"Launching {browser_type} browser (headless={headless})")

            playwright = await async_playwright().start()
            browser_launcher = getattr(playwright, browser_type)

            user_data_dir = tempfile.mkdtemp(prefix='playwright_mcp_')
            logger.debug(f"Using user data dir: {user_data_dir}")

            context = await browser_launcher.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                args=['--no-sandbox', '--start-maximized'],
                viewport=None,
                no_viewport=True
            )

            session_id = f"{browser_type}_{id(context)}"
            self.active_playwright[session_id] = playwright
            self.active_contexts[session_id] = context

            # Create initial page
            page = await context.new_page()
            await page.goto('about:blank')
            logger.info(f"Browser launched successfully with session ID: {session_id}")

            return {"success": True, "session_id": session_id}
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    async def _new_page(self, args: dict) -> dict:
        """Create a new page in a browser session."""
        try:
            session_id = args.get("session_id")
            context = self.active_contexts.get(session_id)
            if not context:
                logger.error(f"Invalid session ID: {session_id}")
                return {"error": "Invalid session ID"}

            page = await context.new_page()
            page_id = f"page_{id(page)}"
            self.active_pages[page_id] = page
            logger.info(f"Created new page with ID: {page_id}")

            return {"success": True, "page_id": page_id}
        except Exception as e:
            logger.error(f"Error creating new page: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    async def _goto(self, args: dict) -> dict:
        """Navigate to a URL in a page."""
        try:
            page_id = args.get("page_id")
            url = args.get("url")
            page = self.active_pages.get(page_id)
            if not page:
                logger.error(f"Invalid page ID: {page_id}")
                return {"error": "Invalid page ID"}

            logger.info(f"Navigating page {page_id} to {url}")
            await page.goto(url)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error navigating to URL: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    async def _close_page(self, args: dict) -> dict:
        """Close a specific page in a browser session."""
        try:
            session_id = args.get("session_id")
            page_id = args.get("page_id")

            # Verify session exists
            if session_id not in self.active_contexts:
                logger.error(f"Invalid session ID: {session_id}")
                return {"error": "Invalid session ID"}

            # Verify page exists
            page = self.active_pages.get(page_id)
            if not page:
                logger.error(f"Invalid page ID: {page_id}")
                return {"error": "Invalid page ID"}

            # Verify page belongs to the specified session
            if page.context != self.active_contexts[session_id]:
                logger.error(f"Page {page_id} does not belong to session {session_id}")
                return {"error": "Page does not belong to specified session"}

            # Close the page
            await page.close()
            del self.active_pages[page_id]
            logger.info(f"Closed page: {page_id}")

            return {"success": True}
        except Exception as e:
            logger.error(f"Error closing page: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    async def _close_browser(self, args: dict) -> dict:
        """Close a browser session."""
        try:
            session_id = args.get("session_id")
            context = self.active_contexts.get(session_id)
            playwright = self.active_playwright.get(session_id)
            if not context or not playwright:
                logger.error(f"Invalid session ID: {session_id}")
                return {"error": "Invalid session ID"}

            # Close all pages associated with this context
            pages_to_remove = []
            for page_id, page in self.active_pages.items():
                if page.context == context:
                    await page.close()
                    pages_to_remove.append(page_id)

            for page_id in pages_to_remove:
                del self.active_pages[page_id]
                logger.debug(f"Removed page: {page_id}")

            await context.close()
            await playwright.stop()

            del self.active_contexts[session_id]
            del self.active_playwright[session_id]
            logger.info(f"Closed browser session: {session_id}")

            return {"success": True}
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}


async def main():
    logger.info("Starting browser manager service")
    manager = BrowserManager()
    await manager.start_server()


if __name__ == "__main__":
    asyncio.run(main())
