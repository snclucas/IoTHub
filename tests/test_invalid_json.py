import json

from tests.stashy_test_case import StashyTestCase


class TestStashyAuthorization(StashyTestCase):

    def test_post_string(self):
        bad_json = "{'l': 'l'}"
        result = self.simulate_request(method='POST', path='/d/test/docs',
                                       headers=self.header_with_user1_token, protocol='http',
                                       body=json.dumps(bad_json))

        self.assertEqual(result.json, {"message": "Bad JSON", "status": "fail"})
