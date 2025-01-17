import logging
from .session import SessionManager
from .tools.handlers.ai_agent.job_store import JobStore


logger = logging.getLogger("browser_daemon")


class BrowserDaemon:
    def __init__(self):
        self.session_manager = SessionManager()
        self.job_store = JobStore()  # Initialize job store
        logger.info("Browser daemon initialized with job store") 