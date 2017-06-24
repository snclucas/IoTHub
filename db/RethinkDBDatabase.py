import json
from util import date_util
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError
from rethinkdb.errors import ReqlOpFailedError

from db.Database import Database

PROJECT_DB = 'todo'


class RethinkDBDatabaseManager(Database):

    def __init__(self, host, port):
        super(Database, self).__init__()
        self.rdb_host = host
        self.rdb_port = port
        # Set up db connection client
        self.db_connection = r.connect(self.rdb_host, self.rdb_port)

    def get_one_by_id(self, table, doc_id):
        result = r.db(PROJECT_DB).table(table).get(doc_id).run(self.db_connection)
        if result is not None:
            if "expiry" in result and date_util.__check_date__(result['expiry']):
                expiry_date = date_util.parse_date(result['expiry'])
                now = date_util.get_now()
                print(date_util.get_date_delta(now, expiry_date))
                if date_util.get_date_delta(now, expiry_date) >= 0:
                    # Now check expiry date, if after delete document
                    self.delete_one(table, doc_id)
                    return json.dumps({"Success": "Fail", "message": "Document not found"})
            return json.dumps(result)
        else:
            return json.dumps({"Success": "Fail", "message": "Document not found"})

    def get_one_where(self, table, where, is_val):
        try:
            cursor = r.db(PROJECT_DB).table(table).filter({where: is_val}).run(self.db_connection)
            result = [i for i in cursor]
            if len(result) == 0:
                return None
            else:
                return json.dumps(result[0])
        except ReqlOpFailedError:
                return None

    def get_all(self, table):
        try:
            note_cursor = r.db(PROJECT_DB).table(table).run(self.db_connection)
            result = [i for i in note_cursor]
            return json.dumps(result)
        except ReqlOpFailedError:
            return None

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
