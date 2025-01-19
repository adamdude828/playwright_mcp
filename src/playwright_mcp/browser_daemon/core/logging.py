import os
import logging
import logging.handlers


def setup_logging(logger_name: str) -> logging.Logger:
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    log_dir = os.path.join(project_root, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Get or create logger
    logger = logging.getLogger(logger_name)
    
    # Set level based on environment variable
    level = os.getenv("LOG_LEVEL", "DEBUG")
    level = getattr(logging, level.upper())
    logger.setLevel(level)
    
    # Ensure propagation is enabled
    logger.propagate = True
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # Debug file handler
        debug_handler = logging.FileHandler(os.path.join(log_dir, "debug.log"))
        debug_handler.setLevel(logging.DEBUG)
        debug_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        debug_handler.setFormatter(debug_formatter)
        logger.addHandler(debug_handler)

        # Error file handler
        error_handler = logging.FileHandler(os.path.join(log_dir, "error.log"))
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)

    return logger 