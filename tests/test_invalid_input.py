

from tests.stashy_test_case import StashyTestCase


class TestStashyAuthorization(StashyTestCase):

    def test_get_invalid_action(self):

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

        self.assertEqual(result.json, {"status": "fail", "message": "Endpoint not specified"})

    def test_get_invalid_endpoint_type(self):

        result = self.simulate_request(method='GET', path='/wrong',
                                       headers=self.header_with_user1_token, protocol='http')

        self.assertEqual(result.json, {"status": "fail", "message": "Invalid endpoint type"})

    def test_get_invalid_no_endpoint(self):

        result = self.simulate_request(method='GET', path='/',
                                       headers=self.header_with_user1_token, protocol='http')

        self.assertEqual(result.json, {"status": "fail", "message": "Missing endpoint type"})
