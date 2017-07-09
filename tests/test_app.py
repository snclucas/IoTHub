from falcon import testing
import json
import requests

import app


class StashyTestCase(testing.TestCase):

    header_with_token = {"Content-Type": "application/json", "Authorization": "Bearer 64504d74a4dc4bad26d863c0a4ab29e5"}
    test_url = 'https://stashy.io/api'

    test_user = {"_id": {"$oid": "5925bba47157aa4525b18580"}, "dataPrivacy": "public",
                "addDatestampToPosts": "true", "publicEndpoints": [{"name": "bffgjg","endpoint":
                    "4533ffd4e9e3","_id": {"$oid": "5956843316c9bb639fe9914f"}}],"allowedPublicEndpoints": 1,
                 "tokens": [{"name": "my-token","token": "64504d74a4dc4bad26d863c0a4ab29e5","_id":
                     {"$oid": "595fe42edf127b560b68963a"}}],"local": {"displayName": "test_user"},
                 "accountType": "Free", "allowedTokens": 1 }

    def setUp(self):
        super(StashyTestCase, self).setUp()
        self.app = app.api


class TestStashyAuthorization(StashyTestCase):
    def test_get_no_token(self):
        headers = {"Content-Type": "application/json"}
        result = self.simulate_request(method='GET', path='/d/test/docs', headers=headers, protocol='http')
        self.assertEqual(result.json, {'status': 'fail', 'message': 'No authentication token supplied'})

    def test_get_invalid_token(self):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer 0d24a"}
        result = self.simulate_request(method='GET', path='/d/test/docs', headers=headers, protocol='http')
        self.assertEqual(result.json, {"status": "fail", "message": "No user with that token"})

    def test_post_get_valid_token(self):

        result = self.simulate_request(method='POST', path='/d/test/docs',
                                       headers=self.header_with_token, protocol='http',
                                       body=json.dumps({"spam": "1", "eggs": "2"}))

        if isinstance(result.json, list):
            json_data = result.json[0]
        else:
            json_data = result.json

        self.assertIn('id', json_data)

        newdoc_id = json_data['id']

        self.assertIn('spam', json_data)
        self.assertEqual(json_data['spam'], "1")

        self.assertIn('eggs', json_data)
        self.assertEqual(json_data['eggs'], "2")

        result = self.simulate_request(method='GET', path='/d/test/docs/' + newdoc_id,
                                       headers=self.header_with_token, protocol='http')

        json_data_get = result.json

        self.assertIn('spam', json_data_get)
        self.assertEqual(json_data_get['spam'], "1")

        self.assertIn('eggs', json_data_get)
        self.assertEqual(json_data_get['eggs'], "2")

