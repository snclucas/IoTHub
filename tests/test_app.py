
from falcon import testing
from urllib.parse import urlparse
import http.client


class StashyTestCase(testing.TestCase):
    def setUp(self):
        super(StashyTestCase, self).setUp()


class TestStashy(StashyTestCase):
    def test_no_token(self):
        url = 'http://localhost:8000/d/test/docs'
        headers = {"Content-Type": "application/json"}
        domain = urlparse(url).netloc
        connection = http.client.HTTPConnection(domain)
        connection.request("GET", url, headers=headers)
        response = connection.getresponse()
        self.assertEqual(response.read().decode(), '{"status": "Fail", "message": "No authentication token supplied"}')

    def test_invalid_token(self):
        url = 'http://localhost:8000/d/test/docs'
        headers = {"Content-Type": "application/json", "Authorization": "Bearer 3453"}
        domain = urlparse(url).netloc
        connection = http.client.HTTPConnection(domain)
        connection.request("GET", url, headers=headers)
        response = connection.getresponse()
        self.assertEqual(response.read().decode(), '{"status": "Fail", "message": "Invalid token"}')
