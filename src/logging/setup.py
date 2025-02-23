import logging
import os
from pathlib import Path


def setup_logger(
    name: str, log_file_path: str, level=logging.INFO
) -> logging.Logger:
    """
    Creates and returns a logger with a given name and file.

    Args:
        name (str): Name of the logger (e.g., "database_manager").
        log_file (str): Log file path.
        level: Logging level (default: INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_path = Path(log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Show more details in console

        # Log format
        log_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        file_handler.setFormatter(log_format)
        console_handler.setFormatter(log_format)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
