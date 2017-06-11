from db import RethinkDBDatabase


class DatabaseManager:

    def __init__(self, config_json):
        if 'database' not in config_json:
            raise ValueError("No database supplied")
        else:
            database = config_json['database']
            if database not in config_json:
                raise ValueError("No section for " + database + " supplied")
            else:
                if 'RethinkDB' == database:
                    self.db = RethinkDBDatabase.RethinkDBDatabaseManager(config_json[database])

    def get_db(self):
        return self.db
