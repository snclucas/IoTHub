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

    def tearDown(self):
        super(StashyTestCase, self).tearDown()
        self.simulate_request(method='DELETE', path='/d/test/docs/all',
                              headers=self.header_with_user1_token, protocol='http')


class TestStashyAuthorization(StashyTestCase):

    def test_get_invalid_endpoint(self):

        result = self.simulate_request(method='GET', path='/d/test/wrong',
                                       headers=self.header_with_user1_token, protocol='http')

        self.assertEqual(result.json, {"status": "fail", "message": "Document not found"})

    def test_get_invalid_no_action(self):

        result = self.simulate_request(method='GET', path='/d/test',
                                       headers=self.header_with_user1_token, protocol='http')

        self.assertEqual(result.json, {"status": "fail", "message": "Document not found"})

    def test_get_invalid_no_table(self):

        result = self.simulate_request(method='GET', path='/d',
                                       headers=self.header_with_user1_token, protocol='http')

        self.assertEqual(result.json, {"status": "fail", "message": "Document not found"})

    def test_get_invalid_no_endpoint(self):

        result = self.simulate_request(method='GET', path='/',
                                       headers=self.header_with_user1_token, protocol='http')

        self.assertEqual(result.json, {"status": "fail", "message": "Document not found"})
