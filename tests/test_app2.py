# -----------------------------------------------------------------
# unittest
# -----------------------------------------------------------------

from falcon import testing
import app


class MyTestCase(testing.TestCase):
    def setUp(self):
        super(MyTestCase, self).setUp()

        # Assume the hypothetical `myapp` package has a
        # function called `create()` to initialize and
        # return a `falcon.API` instance.
        self.app = app.api


class TestMyApp(MyTestCase):
    def test_get_message(self):
        doc = {u'message': u'Hello world!'}

        result = self.simulate_get('/messages/42')

        print(result.json)
        self.assertEqual(False, True)
        #self.assertEqual(result.json, doc)