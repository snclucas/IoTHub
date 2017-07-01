from db import MongoDBDatabase
import config


class DatabaseManager:

    def __init__(self):
        self.db = None
        if config.db is "":
            raise ValueError("No database supplied")
        else:
            database = config.db
            if 'mongodb' == database.lower():
                self.db = MongoDBDatabase.MongoDBDatabase(config.mongodb_uri)
            else:
                raise ValueError("No database")

    def get_db(self):
        return self.db
