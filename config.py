import os
import json

mongodb_uri = os.getenv('MONGODB_URI', "")
salt = os.getenv('salt', "")


def read_config():
    config_json = __read_config_file__()
    return config_json


def __read_config_file__():
    with open('config.json', 'r') as f:
        return json.load(f)
