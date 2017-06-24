import json
from bson import ObjectId
from pymongo import MongoClient

from db.Database import Database

from util.JSONEncoder import JSONEncoder

PROJECT_DB = 'stashy'


class MongoDBDatabase(Database):

    def __init__(self, mongodb_uri):
        super(Database, self).__init__()
        self.db_connection = MongoClient(mongodb_uri)
        self.db = self.db_connection[PROJECT_DB]

    def get_one_by_id(self, table, doc_id):
        pass

    def get_one_where(self, table, where, is_val):
        pass

    def find_where(self, table, criteria):
        self.db[table].find(criteria)

    def get_all(self, table):
        cursor = self.db[table].find({})
        result = [i for i in cursor]
        return json.dumps(result, cls=JSONEncoder).replace('_id', 'id')

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
        result = self.db[table].drop()
        return json.dumps(result)

    def delete_one(self, table, doc_id):
        result = self.db[table].delete_one({'_id': ObjectId(doc_id)})
        return json.dumps(result)

    def delete_where(self, table, where, is_val):
        result = self.db[table].delete_many({where: is_val})
        return json.dumps(result)

