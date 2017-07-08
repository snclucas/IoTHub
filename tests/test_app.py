from falcon import testing
import json
import requests

import app


class StashyTestCase(testing.TestCase):

    header_with_token = {"Content-Type": "application/json", "Authorization": "Bearer 0d24a98c5544578cedd7055d2a6eeb4d"}
    test_url = 'https://stashy.io/api'

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

        json_data = result.json[0]

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

