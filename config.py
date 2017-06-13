import os
import json


def read_config():
    mongodb_uri = os.getenv('MONGODB_URI', "")
    config_json = __read_config_file__()
    return config_json


def __read_config_file__():
    with open('config.json', 'r') as f:
        return json.load(f)
