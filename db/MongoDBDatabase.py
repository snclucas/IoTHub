import json
from bson.objectid import ObjectId

from pymongo import MongoClient

from db.Database import Database

PROJECT_DB = 'todo'


class MongoDBDatabase(Database):

    def __init__(self, config):
        super(Database, self).__init__()
        self.db_connection = MongoClient(config['mongo_url'])
        self.db = self.db_connection[PROJECT_DB]

    def get_one_by_id(self, table, doc_id):
        pass

    def get_one_where(self, table, where, is_val):
        pass

    def get_all(self, table):
        cursor = self.db[table].find()
        result = [i for i in cursor]
        return json.dumps(result)

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

