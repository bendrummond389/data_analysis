import logging
import yaml

def load_config(config_file='config/config.yaml'):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def setup_logging(log_path):
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Optionally also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
