import os
import logging
import yaml


def get_project_root():
    """Returns the absolute path to the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_config():
    """Loads the configuration file from the project root."""
    config_path = os.path.join(get_project_root(), "config/config.yaml")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def setup_logging(log_path):
    """Sets up logging with the specified log file path."""
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    # Optionally also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger("").addHandler(console)
