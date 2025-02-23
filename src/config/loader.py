from pathlib import Path
import logging
import yaml
from typing import Optional, Dict, Any

from src.config.paths import get_project_root


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from a YAML file.
    
    Args:
        config_path: Optional path to a specific config file.
                    If not provided, loads the default project config.
    
    Returns:
        Dictionary containing the configuration.
    
    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the YAML file is invalid
    """
    try:
        # Default to project config if no path provided
        if config_path is None:
            root = get_project_root()
            config_path = root / "config/config.yaml"
        
        with config_path.open("r") as file:
            return yaml.safe_load(file)
            
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Invalid YAML in config file: {e}")
        raise


def setup_logging(log_path):
    """Sets up logging with the specified log file path."""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # Configure file logging
    logging.basicConfig(filename=log_path, level=logging.INFO, format=log_format)

    # Configure console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))

    logging.getLogger().addHandler(console_handler)
