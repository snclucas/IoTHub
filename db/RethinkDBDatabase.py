import json

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

from db.Database import Database

PROJECT_DB = 'todo'


class RethinkDBDatabaseManager(Database):

    def __init__(self, config):
        super(Database, self).__init__()
        self.rdb_host = config['rdb_host']
        self.rdb_port = config['rdb_port']
        # Set up db connection client
        self.db_connection = r.connect(self.rdb_host, self.rdb_port)

    def get_one_by_id(self, table, doc_id):
        result = r.db(PROJECT_DB).table(table).get(doc_id).run(self.db_connection)
        if result is None or "expiry" in result:
            # Now check expiry date, if after delete document
            self.delete_one(table, doc_id)
            return json.dumps({"Success": "Fail", "message": "Document not found"})
        return json.dumps(result)

    def get_one_where(self, table, where, is_val):
        cursor = r.db(PROJECT_DB).table(table).filter({where: is_val}).run(self.db_connection)
        result = [i for i in cursor]
        if len(result) == 0:
            return None
        else:
            return json.dumps(result[0])

    def get_all(self, table):
        note_cursor = r.db(PROJECT_DB).table(table).run(self.db_connection)
        result = [i for i in note_cursor]
        return json.dumps(result)

    def save(self, json_data, table):
        sid = r.db(PROJECT_DB).table(table).insert(json_data).run(
            self.db_connection)
        return sid['generated_keys'][0]

    def add_table(self, table):
        self.__db_setup__(table)

    def update(self, table, doc_id, doc):
        result = r.db(PROJECT_DB).table(table).get(doc_id).update(doc).run(self.db_connection)
        return json.dumps(result)

    def delete_all(self, table):
        result = r.db(PROJECT_DB).table(table).delete(return_changes=True).run(self.db_connection)
        return json.dumps(result)

    def delete_one(self, table, doc_id):
        result = r.db(PROJECT_DB).table(table).get(doc_id).delete(return_changes=True).run(self.db_connection)
        return json.dumps(result)

    def delete_where(self, table, where, is_val):
        result = r.db(PROJECT_DB).table(table).filter({where: is_val}).delete().run(self.db_connection)
        return json.dumps(result)

    # Function is for cross-checking database and table exists
    def __db_setup__(self, table):
        try:
            r.db_create(PROJECT_DB).run(self.db_connection)
            print('Database setup completed.')
        except RqlRuntimeError:
            try:
                r.db(PROJECT_DB).table_create(table).run(self.db_connection)
                print('Table creation completed')
            except RqlRuntimeError:
                print('Table already exists. Nothing to do')
