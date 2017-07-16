import json

from tests.stashy_test_case import StashyTestCase


class TestStashyAuthorization(StashyTestCase):

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
