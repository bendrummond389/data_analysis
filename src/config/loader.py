from pathlib import Path
import yaml
from typing import Optional, Dict, Any

from src.config.paths import find_project_root


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
            root = find_project_root()
            config_path = root / "config/config.yaml"

        with config_path.open("r") as file:
            return yaml.safe_load(file)

    except FileNotFoundError:

        raise
    except yaml.YAMLError as e:

        raise
