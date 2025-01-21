import logging
from .session import SessionManager
from ..mcp_server.handlers.ai_agent.job_store import job_store


logger = logging.getLogger("browser_daemon")


class BrowserDaemon:
    def __init__(self):
        self.session_manager = SessionManager()
        self.job_store = job_store  # Use the singleton job store instance
        logger.info("Browser daemon initialized with job store") 