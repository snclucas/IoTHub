from falcon import testing
import json
from bson import ObjectId
from pymongo import MongoClient
import config

import app


class StashyTestCase(testing.TestCase):
    header_with_bad_token = {"Content-Type": "application/json", "Authorization": "Bearer 1"}
    header_with_user1_token = {"Content-Type": "application/json",
                               "Authorization": "Bearer 1111111111111111111111111"}
    header_with_user2_token = {"Content-Type": "application/json",
                               "Authorization": "Bearer 222222222222222222222"}

    testuser1_endpoint = "testuser1endpoint"
    testuser2_endpoint = "testuser2endpoint"

    test_user1 = {"_id": ObjectId("595fd9e5a2e6845470fa5d55"),
                  "dataPrivacy": "public",
                  "addDatestampToPosts": "true",
                  "publicEndpoints": [{"name": "bffgjg", "endpoint": "testuser1endpoint", "_id":
                      ObjectId("5956843316c9bb639fe9914f")}],
                  "allowedPublicEndpoints": 1,
                  "tokens": [{"name": "my-token1", "token": "1111111111111111111111111", "_id":
                      ObjectId("595fe42edf127b560b68963a")}], "local": {"displayName": "test_user"},
                  "accountType": "Free", "allowedTokens": 1}

    test_user2 = {"_id": ObjectId("595fd9e5a2e6845470fa5656"),
                  "dataPrivacy": "public",
                  "addDatestampToPosts": "true",
                  "publicEndpoints": [{"name": "bffgjg", "endpoint": "testuser2endpoint", "_id":
                      ObjectId("5956843316c9bb639fe9914f")}],
                  "allowedPublicEndpoints": 1,
                  "tokens": [{"name": "my-token2", "token": "222222222222222222222", "_id":
                      ObjectId("595fe42edf127b560b68963a")}], "local": {"displayName": "test_user"},
                  "accountType": "Free", "allowedTokens": 1}

    test_doc = {"spam": "1", "eggs": "2"}

    test_doc_explode = {"docs": [{"spam": "1", "eggs": "2"}, {"spam": "10", "eggs": "20"}]}

    def setUp(self):
        super(StashyTestCase, self).setUp()
        self.app = app.api
        # Insert a test user if not present
        self.db_connection = MongoClient(config.mongodb_uri)
        self.db = self.db_connection['stashy']
        result = self.db['users'].find_one({"tokens.token": "1111111111111111111111111"})
        if result is None:
            self.db['users'].insert_one(self.test_user1)
        result = self.db['users'].find_one({"tokens.token": "222222222222222222222"})
        if result is None:
            self.db['users'].insert_one(self.test_user2)


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
                                       headers=self.header_with_user1_token, protocol='http')

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
                                       headers=self.header_with_user1_token, protocol='http',
                                       body=json.dumps(self.test_doc))

        json_data = result.json

        self.assertIn('id', json_data)

        newdoc_id = json_data['id']

        json_data.pop('id', None)
        self.assertEqual(self.ordered(json_data), self.ordered(self.test_doc))

        return newdoc_id

    def test_save_document_with_explode(self):
        params = {"st::explode": "docs"}
        result = self.simulate_request(method='POST', path='/d/test/docs',
                                       headers=self.header_with_user1_token, protocol='http', params=params,
                                       body=json.dumps(self.test_doc_explode))

        if isinstance(result.json, list):
            json_data = result.json
        else:
            self.fail("Failed to save doc [" + json.dumps(result.json) + "]")

        for doc in json_data:
            self.assertIn('id', doc)

        self.assertEqual(len(json_data), 2)

    def test_post_to_public_endpoint(self):
        result = self.simulate_request(method='POST', path='/p/testuser1endpoint/docs',
                                       headers=self.header_with_user1_token, protocol='http',
                                       body=json.dumps(self.test_doc))

        json_data = result.json
        newdoc_id = json_data['id']
        json_data.pop('id', None)
        self.assertEqual(self.ordered(json_data), self.ordered(self.test_doc))

        result = self.simulate_request(method='POST', path='/p/testuser1endpoint/docs',
                                       headers=self.header_with_user2_token, protocol='http',
                                       body=json.dumps(self.test_doc))

        self.assertEqual(self.ordered({"status": "fail", "message": "Cannot post to this endpoint"}),
                         self.ordered(result.json))

        # Now both users get the public data
        result = self.simulate_request(method='GET', path='/p/testuser1endpoint/docs/' + newdoc_id,
                                       headers=self.header_with_user1_token, protocol='http')

        json_data = result.json
        json_data.pop('id', None)
        self.assertEqual(self.ordered(json_data), self.ordered(self.test_doc))

        result = self.simulate_request(method='GET', path='/p/testuser1endpoint/docs/' + newdoc_id,
                                       headers=self.header_with_user2_token, protocol='http')

        json_data = result.json
        json_data.pop('id', None)
        self.assertEqual(self.ordered(json_data), self.ordered(self.test_doc))

    def get_document_with_good_header(self, doc_id):
        return self.simulate_request(method='GET', path='/d/test/docs/' + doc_id,
                                     headers=self.header_with_user1_token, protocol='http')

    def ordered(self, obj):
        if isinstance(obj, dict):
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        else:
            return obj
