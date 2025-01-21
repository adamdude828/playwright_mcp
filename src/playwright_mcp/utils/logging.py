"""Centralized logging configuration."""
import logging
import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def _sanitize_filename(filename: str) -> str:
    """Sanitize the filename to be file system friendly.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        A sanitized filename safe for file system use
    """
    # Replace invalid characters with underscore
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove any leading/trailing spaces or dots
    sanitized = sanitized.strip('. ')
    return sanitized or 'app.log'


def setup_logging(name: str, log_file: str = "app.log") -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        name: The logger name
        log_file: Optional custom log file name. Will be sanitized for file system safety.
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logger = logging.getLogger(name)
    
    # Set level from .env, default to INFO if not set
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    logger.setLevel(getattr(logging, log_level))

    # Sanitize and use the provided log filename
    safe_filename = _sanitize_filename(log_file)
    file_handler = logging.FileHandler(log_dir / safe_filename)
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