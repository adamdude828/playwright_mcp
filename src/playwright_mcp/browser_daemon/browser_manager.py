import asyncio

from .core.logging import setup_logging
from .core.server import UnixSocketServer
from .core.session import session_manager
from .handlers.navigation import NavigationHandler
from .handlers.dom import DOMHandler
from .handlers.screenshot import ScreenshotHandler
from .handlers.session import SessionHandler
from .handlers.interaction import InteractionHandler
from .tools.handlers.ai_agent.handler import AIAgentHandler
from .tools.handlers.ai_agent.get_result import GetAIResultHandler
from .daemon import BrowserDaemon

logger = setup_logging("browser_manager")


class BrowserManager:
    def __init__(self):
        # Initialize the browser daemon
        self.daemon = BrowserDaemon()
        
        # Use the shared session manager instance
        self.session_manager = session_manager
        logger.debug(f"BrowserManager using session manager instance: {id(self.session_manager)}")
        
        self.server = UnixSocketServer()
        
        # Initialize handlers with the same session manager instance
        nav_handler = NavigationHandler(self.session_manager)
        dom_handler = DOMHandler(self.session_manager)
        screenshot_handler = ScreenshotHandler(self.session_manager)
        session_handler = SessionHandler(self.session_manager)
        interaction_handler = InteractionHandler(self.session_manager)
        ai_agent_handler = AIAgentHandler()
        get_ai_result_handler = GetAIResultHandler()

        # Map commands to handlers and whether they need daemon access
        self.handlers = {
            # Navigation commands
            "navigate": {"handler": nav_handler, "needs_daemon": False},
            "new-tab": {"handler": nav_handler, "needs_daemon": False},
            
            # DOM commands
            "execute-js": {"handler": dom_handler, "needs_daemon": False},
            "explore-dom": {"handler": dom_handler, "needs_daemon": False},
            "search-dom": {"handler": dom_handler, "needs_daemon": False},
            
            # Screenshot commands
            "screenshot": {"handler": screenshot_handler, "needs_daemon": False},
            "highlight-element": {"handler": screenshot_handler, "needs_daemon": False},
            
            # Session management commands
            "close-browser": {"handler": session_handler, "needs_daemon": False},
            "close-tab": {"handler": session_handler, "needs_daemon": False},
            
            # Interaction commands
            "interact-dom": {"handler": interaction_handler, "needs_daemon": False},
            
            # AI agent commands
            "ai-agent": {"handler": ai_agent_handler, "needs_daemon": True},
            "get-ai-result": {"handler": get_ai_result_handler, "needs_daemon": True}
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
                handler_info = self.handlers.get(command)
                if not handler_info:
                    response = {"error": f"Unknown command: {command}"}
                else:
                    # Add command to args so handler knows what to do
                    args["command"] = command
                    # Only pass daemon to handlers that need it
                    if handler_info["needs_daemon"]:
                        response = await handler_info["handler"].handle(args, daemon=self.daemon)
                    else:
                        response = await handler_info["handler"].handle(args)
            
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
