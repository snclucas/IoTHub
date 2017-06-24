import os

db = os.getenv('DB', "")

mongodb_uri = os.getenv('MONGODB_URI', "")
salt = os.getenv('salt', "")

rethink_db_host = os.getenv('RETHINK_DB_HOST', "localhost")
rethink_db_port = os.getenv('RETHINK_DB_PORT', "28015")
