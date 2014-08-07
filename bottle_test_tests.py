from webtest import TestApp, TestResponse
from unittest import TestCase
import bottle_test


class BottleTestTests(TestCase):

    def setUp(self):
        self.app = TestApp(bottle_test.app)
        for r in bottle_test.app.routes:
            print r

    def test_index(self):
        resp = self.app.get("/")
        print type(resp)
        assert isinstance(resp, TestResponse)
        self.assertEqual(resp.status, "200 OK")
        self.assertIn(resp.body, "<h1>Index Page</h1>")

    def test_hello_test(self):
        response = self.app.get("/hello")
        print response.body
        self.assertEqual(response.status, "200 OK")
        self.assertTrue(len(response.body) > 0)

    def test_hello_param_test(self):
        response = self.app.get("/hello/Bob")
        print response.body
        self.assertIn("<b>Hello Bob</b>!", response.body)

    def test_markdown_test(self):
        response = self.app.get("/markdown_test")
        self.assertEqual(response.status, "200 OK")
        self.assertTrue(len(response.body) > 0)
        self.assertIn("<h1>An h1 header</h1>", response.body)
