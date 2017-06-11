import json
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

from DatabaseManager import DatabaseManager

RDB_HOST = 'localhost'
RDB_PORT = 28015
PROJECT_DB = 'todo'


class RethinkDBDatabaseManager(DatabaseManager):

    def __init__(self):
        super(DatabaseManager, self).__init__()
        # Set up db connection client
        self.db_connection = r.connect(RDB_HOST, RDB_PORT)

    def get_one(self, table, doc_id):
        result = r.db(PROJECT_DB).table(table).get(doc_id).run(self.db_connection)
        print(result)
        if result is None or "expiry" in result:
            # Now check expiry date, if after delete document
            self.delete_one(table, doc_id)
            return json.dumps({"Success": "Fail", "message": "Document not found"})
        return json.dumps(result)

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

    def delete_where_is(self, table, where, is_val):
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
            except:
                print('Table already exists. Nothing to do')
