import asyncio

from .core.logging import setup_logging
from .core.server import UnixSocketServer
from .core.session import session_manager
from .handlers.navigation import NavigationHandler
from .handlers.dom import DOMHandler
from .handlers.screenshot import ScreenshotHandler
from .handlers.session import SessionHandler

logger = setup_logging("browser_manager")


class BrowserManager:
    def __init__(self):
        # Use the shared session manager instance
        self.session_manager = session_manager
        logger.debug(f"BrowserManager using session manager instance: {id(self.session_manager)}")
        
        self.server = UnixSocketServer()
        
        # Initialize handlers with the same session manager instance
        nav_handler = NavigationHandler(self.session_manager)
        dom_handler = DOMHandler(self.session_manager)
        screenshot_handler = ScreenshotHandler(self.session_manager)
        session_handler = SessionHandler(self.session_manager)

        # Map commands to handlers
        self.handlers = {
            # Navigation commands
            "navigate": nav_handler,
            "new-tab": nav_handler,
            
            # DOM commands
            "execute-js": dom_handler,
            "explore-dom": dom_handler,
            "search-dom": dom_handler,
            
            # Screenshot commands
            "screenshot": screenshot_handler,
            "highlight-element": screenshot_handler,
            
            # Session management commands
            "close-browser": session_handler,
            "close-tab": session_handler
        }

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a connection from a client."""
        try:
            request = await self.server.read_command(reader)
            logger.debug(f"Received request: {request}")
            
            command = request.get("command")
            args = request.get("args", {})
            if not command:
                response = {"error": "No command specified"}
            elif command == "ping":
                response = {"result": "pong"}
            else:
                handler = self.handlers.get(command)
                if not handler:
                    response = {"error": f"Unknown command: {command}"}
                else:
                    # Add command to args so handler knows what to do
                    args["command"] = command
                    response = await handler.handle(args)
            
            await self.server.send_response(writer, response)

        except Exception as e:
            logger.error(f"Error handling connection: {e}")
            error_response = {"error": str(e)}
            await self.server.send_response(writer, error_response)

    async def start(self):
        """Start the browser manager service."""
        logger.info("Starting browser manager service")
        await self.server.start(self.handle_connection)

    async def shutdown(self):
        """Shutdown the browser manager service."""
        logger.info("Shutting down browser manager service")
        await self.session_manager.shutdown()
        self.server.cleanup()


async def main():
    manager = BrowserManager()
    try:
        await manager.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
