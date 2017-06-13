from db import RethinkDBDatabase, MongoDBDatabase


class DatabaseManager:

    def __init__(self, config_json):
        if 'database' not in config_json:
            raise ValueError("No database supplied")
        else:
            database = config_json['database']
            if database not in config_json:
                raise ValueError("No section for " + database + " supplied")
            else:
                if 'rethinkdb' == database.lower():
                    self.db = RethinkDBDatabase.RethinkDBDatabaseManager(config_json[database])
                elif 'mongodb' == database.lower():
                    self.db = MongoDBDatabase.MongoDBDatabase(config_json[database])

    def get_db(self):
        return self.db
