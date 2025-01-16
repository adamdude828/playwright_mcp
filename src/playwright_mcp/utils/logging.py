"""Centralized logging configuration."""
import logging
import os
import sys
from pathlib import Path


def setup_logging(name: str) -> logging.Logger:
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

    # File handler for debug logs
    debug_handler = logging.FileHandler(log_dir / "debug.log")
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    debug_handler.setFormatter(debug_formatter)
    logger.addHandler(debug_handler)

    # File handler for errors
    error_handler = logging.FileHandler(log_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d\n'
    )
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger 