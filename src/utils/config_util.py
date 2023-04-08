import json
import os


def load_config():
    # Move up two directories in order to access the config directory
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
    # Find the config.json file and open it.
    with open(os.path.join(config_path, 'config.json'), 'r') as config_file:
        return json.load(config_file)
