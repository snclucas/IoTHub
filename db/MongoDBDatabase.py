import json
import bson
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from util import date_util
from db.Database import Database

from util.JSONEncoder import JSONEncoder

PROJECT_DB = 'stashy'


class MongoDBDatabase(Database):

    def __init__(self, mongodb_uri):
        super(Database, self).__init__()
        self.db_connection = MongoClient(mongodb_uri)
        self.db = self.db_connection[PROJECT_DB]

    def get_one_by_id(self, table, doc_id):
        try:
            result = self.db[table].find_one({"_id": ObjectId(doc_id)})
            if result is not None:
                if "expiry" in result and date_util.__check_date__(result['expiry']):
                    expiry_date = date_util.parse_date(result['expiry'])
                    now = date_util.get_now()
                    if date_util.get_date_delta(now, expiry_date) >= 0:
                        # Now check expiry date, if after delete document
                        self.delete_one(table, doc_id)
                        return json.dumps({"status": "Fail", "message": "Document not found"})
                else:
                    return json.dumps(result, cls=JSONEncoder).replace('_id', 'id')
            else:
                return json.dumps({"status": "Fail", "message": "Document not found"})

        except bson.errors.InvalidId:
            return json.dumps({"status": "Fail", "message": "Document not found"})
        except OperationFailure:
            return json.dumps({"status": "fail", "message": "Could not connect to DB"})

    def find_where(self, table, criteria):
        self.db[table].find(criteria)

    def get_all(self, table, filter_by=None, select_by=None, sort=None):
        if filter_by is None:
            filter_by = {}
        if select_by is None:
            select_by = None
        if sort is None:
            sort = [('_id', 1)]
        try:
            cursor = self.db[table].find(filter_by, select_by).sort(sort)
            if cursor.count() == 0:
                return None
            result = [i for i in cursor]
            return json.dumps(result, cls=JSONEncoder).replace('_id', 'id')
        except OperationFailure:
            return json.dumps({"status": "fail", "message": "Could not connect to DB"})

    def save(self, json_data, table):
        result = self.db[table].insert_one(json_data)
        return result.inserted_id

    def add_table(self, table):
        pass

    def update(self, table, doc_id, doc):
        criteria = {"_id": doc_id}
        result = self.db[table].update_one(criteria, doc)
        return json.dumps(result)

    def delete_all(self, table):
        result = self.db[table].delete_many({})
        return result.deleted_count

    def delete(self, table, filter_by=None):
        return self.db[table].delete_many(filter_by)


