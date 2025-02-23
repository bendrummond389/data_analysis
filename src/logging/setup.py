# Standard library
import logging
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str, 
    log_path: str,  
    level: int = logging.INFO,
    console_level: Optional[int] = None 
) -> logging.Logger:
    """Configures and returns a logger with dual file/console output.
    
    Features:
    - Ensures log directory exists
    - Prevents duplicate handler registration
    - Separate log levels for file/console
    - Standardized log formatting
    
    Args:
        name: Logger namespace identifier (e.g. "data_pipeline")
        log_path: Output path for log file (str or Path-like)
        level: Primary logging threshold (default: INFO)
        console_level: Console-specific level (defaults to level param)
    
    Returns:
        Configured Logger instance with file and stream handlers
    """
    # --------------------------
    # Initialization
    # --------------------------
    log_file = Path(log_path)
    console_level = console_level or level 

    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # --------------------------
    # Logger Configuration
    # --------------------------
    logger = logging.getLogger(name)
    logger.setLevel(min(level, console_level)) 

    # Avoid duplicate handlers in notebook environments
    if logger.handlers:  
        return logger

    # --------------------------
    # Handler Setup
    # --------------------------
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    # --------------------------
    # Formatting
    # --------------------------
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    # --------------------------
    # Final Assembly
    # --------------------------
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger