import json

from db_client import *
from DatabaseManager import DatabaseManager


class RethinkDBDatabaseManager(DatabaseManager):

    def __init__(self):
        super(DatabaseManager, self).__init__()

    def get_one(self, table, doc_id):
        result = r.db(PROJECT_DB).table(table).get(doc_id).run(db_connection)
        return json.dumps(result)

    def get_all(self, table):
        note_cursor = r.db(PROJECT_DB).table(table).run(db_connection)
        result = [i for i in note_cursor]
        return json.dumps(result)

    def save(self, json_data, table):
        sid = r.db(PROJECT_DB).table(table).insert(json_data).run(
            db_connection)
        return sid['generated_keys'][0]

    def add_table(self, table):
        db_setup(table)

    def delete_all(self, table):
        r.db(PROJECT_DB).tableDrop(table)
