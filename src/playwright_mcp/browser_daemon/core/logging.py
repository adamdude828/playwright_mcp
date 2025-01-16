import os
import logging
import logging.handlers


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