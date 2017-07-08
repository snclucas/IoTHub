import os

db = os.getenv('DB', "mongodb")

mongodb_uri = os.getenv('MONGODB_URI', "")
salt = os.getenv('salt', "")

rethink_db_host = os.getenv('RETHINK_DB_HOST', "localhost")
rethink_db_port = os.getenv('RETHINK_DB_PORT', "28015")


metadata_key = "stashy::"

reserved_words = ['sort', 'order', 'sortby', 'limit', 'skip']

token_secret = '0BR5zqTw7rlDyPOLtcHpRsmwwSQuDkZbij5yTMZgzZ9gi5kKRl'
