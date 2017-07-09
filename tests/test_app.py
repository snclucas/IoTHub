from falcon import testing
import json
from bson import ObjectId
from pymongo import MongoClient
import config

import app


class StashyTestCase(testing.TestCase):
    header_with_bad_token = {"Content-Type": "application/json", "Authorization": "Bearer 1"}
    header_with_token = {"Content-Type": "application/json", "Authorization": "Bearer 64504d74a4dc4bad26d863c0a4ab29e5"}
    test_url = 'https://stashy.io/api'

    test_user = {"_id": ObjectId("595fd9e5a2e6845470fa5d55"), "dataPrivacy": "public",
                "addDatestampToPosts": "true", "publicEndpoints": [{"name": "bffgjg", "endpoint":
                    "4533ffd4e9e3","_id": ObjectId("5956843316c9bb639fe9914f")}], "allowedPublicEndpoints": 1,
                 "tokens": [{"name": "my-token", "token": "64504d74a4dc4bad26d863c0a4ab29e5", "_id":
                     ObjectId("595fe42edf127b560b68963a")}], "local": {"displayName": "test_user"},
                 "accountType": "Free", "allowedTokens": 1}

    test_doc = {"spam": "1", "eggs": "2"}

    def setUp(self):
        super(StashyTestCase, self).setUp()
        self.app = app.api
        self.db_connection = MongoClient(config.mongodb_uri)
        self.db = self.db_connection['stashy']
        result = self.db['users'].find_one({"tokens.token": "64504d74a4dc4bad26d863c0a4ab29e5"})
        if result is None:
            self.db['users'].insert_one(self.test_user)


class TestStashyAuthorization(StashyTestCase):
    def test_get_no_token(self):
        headers = {"Content-Type": "application/json"}
        result = self.simulate_request(method='GET', path='/d/test/docs', headers=headers, protocol='http')
        self.assertEqual(result.json, {'status': 'fail', 'message': 'No authentication token supplied'})

    def test_get_invalid_token(self):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer 0d24a"}
        result = self.simulate_request(method='GET', path='/d/test/docs', headers=headers, protocol='http')
        self.assertEqual(result.json, {"status": "fail", "message": "No user with that token"})

    def test_get_valid_token_no_doc(self):
        result = self.get_document_with_good_header(doc_id="99")
        self.assertEqual(result.json, {'message': 'Document not found', 'status': 'Fail'})

    def test_post_get_delete_valid_token(self):
        newdoc_id = self.test_save_document()

        result = self.get_document_with_good_header(newdoc_id)

        json_data_get = result.json

        json_data_get.pop('id', None)
        self.assertEqual(self.ordered(json_data_get), self.ordered(self.test_doc))

        result = self.simulate_request(method='DELETE', path='/d/test/docs/' + newdoc_id,
                                       headers=self.header_with_token, protocol='http')

        self.assertEqual(result.json, {'status': 'success', 'id': newdoc_id})

        result = self.get_document_with_good_header(newdoc_id)

        json_data_get = result.json
        self.assertEqual(json_data_get, {'message': 'Document not found', 'status': 'Fail'})

    def test_delete_not_valid_token(self):
        newdoc_id = self.test_save_document()

        result = self.get_document_with_good_header(newdoc_id)

        json_data_get = result.json

        json_data_get.pop('id', None)
        self.assertEqual(self.ordered(json_data_get), self.ordered(self.test_doc))

        result = self.simulate_request(method='DELETE', path='/d/test/docs/' + newdoc_id,
                                       headers=self.header_with_bad_token, protocol='http')

        self.assertEqual(result.json, {'message': 'No user with that token', 'status': 'fail'})

    def test_save_document(self):
        result = self.simulate_request(method='POST', path='/d/test/docs',
                                       headers=self.header_with_token, protocol='http',
                                       body=json.dumps(self.test_doc))

        if isinstance(result.json, list):
            json_data = result.json[0]
        else:
            self.fail("Failed to save doc [" + json.dumps(result.json) + "]")

        self.assertIn('id', json_data)

        newdoc_id = json_data['id']

        json_data.pop('id', None)
        self.assertEqual(self.ordered(json_data), self.ordered(self.test_doc))

        return newdoc_id

    def get_document_with_good_header(self, doc_id):
        return self.simulate_request(method='GET', path='/d/test/docs/' + doc_id,
                                       headers=self.header_with_token, protocol='http')

    def ordered(self, obj):
        if isinstance(obj, dict):
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        else:
            return obj
