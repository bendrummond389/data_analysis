# src/logging/logger.py
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from src.config.paths import find_project_root

class AppLogger:
    """Centralized logging management for application components.
    
    Features:
    - Dual file/console logging
    - Configurable log levels
    - Automatic directory creation
    - Handler deduplication
    
    Usage:
    >>> logger = AppLogger(name="database", log_path="logs/app.log")
    >>> logger.info("System initialized")
    """
    
    def __init__(
        self,
        name: str,
        log_path: Path,
        file_level: int = logging.INFO,
        console_level: int = logging.DEBUG,
        fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ):
        """
        Initialize logger with direct parameters.
        
        Args:
            name: Logger identifier
            log_path: Absolute path to log file
            file_level: Minimum level for file logging
            console_level: Minimum level for console logging
            fmt: Log message format
        """
        self._configure_path(log_path)
        self.logger = logging.getLogger(name)
        self._setup_handlers(log_path, file_level, console_level, fmt)


    @classmethod
    def from_yaml(
        cls, 
        config_path: Path, 
        project_root: Path  
    ) -> 'AppLogger':
        """
        Create logger from YAML configuration with explicit project root.
        
        Example notebook usage:
        >>> project_root = find_project_root(Path.cwd())
        >>> logger = AppLogger.from_yaml(project_root / "config/logging.yaml", project_root)
        """
        config = cls._load_logging_config(config_path)
        return cls(
            name=config['name'],
            log_path=project_root / config['path'],
            file_level=cls._parse_log_level(config['file_level']),
            console_level=cls._parse_log_level(config['console_level']),
            fmt=config.get('format', "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
    
    # --------------------------
    # Configuration Helpers
    # --------------------------
    
    @staticmethod
    def _load_logging_config(config_path: Path) -> Dict[str, Any]:
        """Load logging config without path resolution."""
        try:
            with config_path.open('r') as f:
                config = yaml.safe_load(f)
            
            if 'logging' not in config:
                raise ValueError("Config file missing 'logging' section")
                
            return config['logging']
            
        except Exception as e:
            raise RuntimeError(f"Config load failed: {e}") from e
        
    def _configure_path(self, log_path: Path) -> None:
        """Ensure log directory exists."""
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _setup_handlers(
        self,
        log_path: Path,
        file_level: int,
        console_level: int,
        fmt: str
    ) -> None:
        """Configure logging outputs with deduplication check."""
        if self.logger.handlers:
            return
            
        formatter = logging.Formatter(fmt)
        
        # File handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        
        self.logger.setLevel(min(file_level, console_level))
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    @staticmethod
    def _resolve_log_path(config_path: Path, log_path: str) -> Path:
        """Convert relative path to absolute using project root."""
        project_root = find_project_root(config_path)
        return (project_root / log_path).resolve()

    @staticmethod
    def _parse_log_level(level_str: str) -> int:
        """Convert string log level to logging constant."""
        try:
            return getattr(logging, level_str.upper())
        except AttributeError:
            valid_levels = [k for k in logging._nameToLevel if k.isupper()]
            raise ValueError(
                f"Invalid log level '{level_str}'. "
                f"Valid options: {', '.join(valid_levels)}"
            )
        
    # Simplified logging interface
    def debug(self, msg: str) -> None:
        self.logger.debug(msg)
        
    def info(self, msg: str) -> None:
        self.logger.info(msg)
        
    def warning(self, msg: str) -> None:
        self.logger.warning(msg)
        
    def error(self, msg: str) -> None:
        self.logger.error(msg)
        
    def exception(self, msg: str) -> None:
        self.logger.exception(msg)