from pathlib import Path
import logging
import yaml


def load_config():
    """Loads the configuration file from the project root."""
    config_path = Path(__file__).resolve().parent.parent / "config/config.yaml"
    with config_path.open("r") as file:
        return yaml.safe_load(file)


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
