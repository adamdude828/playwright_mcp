"""Centralized logging configuration."""
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def setup_logging(name: str) -> logging.Logger:
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logger = logging.getLogger(name)
    
    # Set level from .env, default to INFO if not set
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level))

    # Single file handler for all logs
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.DEBUG)  # Capture all levels, filtering happens at logger level
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d'
    )
    file_handler.setFormatter(formatter)
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()
    logger.addHandler(file_handler)
    
    # Ensure we propagate to root logger
    logger.propagate = True

    return logger 