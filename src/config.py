import os
import json

CONFIG_PATH = os.path.expanduser('~/.config/mariadb_login.json')

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as file:
            return json.load(file)
    return None

def save_config(config_data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as config_file:
        json.dump(config_data, config_file)
