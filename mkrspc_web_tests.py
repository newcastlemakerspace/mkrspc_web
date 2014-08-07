from webtest import TestApp, TestResponse
import redis
from unittest import TestCase
import hashlib
import mkrspc_web_app

class MkrspcWebTest(TestCase):

    def _dummy_user(self, redis_conn):
        self.r.delete('mkrspc_superusers')
        self.r.lpush('mkrspc_superusers', 'dkpw')
        print self.r.lrange('mkrspc_superusers', 0, 6)
        dkpw_passwd = u'password1'
        hash_object = hashlib.sha256(b'development_salt_do_not_use_in_production' + dkpw_passwd)
        hex_dig = hash_object.hexdigest()
        print(hex_dig)
        self.r.set('User_Pwd_dkpw', hex_dig)

    def setUp(self):
        self.app = TestApp(mkrspc_web_app.app, extra_environ={'debug': 'True'})
        for route in mkrspc_web_app.app.routes:
            print "App route: ", route
        self.r = redis.StrictRedis(db=3)  # 3 for testing
        self._dummy_user(self.r)

        wiki_md = """
Markdown test page
========

Sub-heading
-------

*bold*

--italic--

[[WikiStyleLink]]

[external link](http://example.com/page.html)

            """
        self.r.set('wiki_TestPage', wiki_md)
        wiki_index = """

Makerspace Wiki Index
--------------------

Markdown **bold** *italic*

 * [[Index]]
 * [[TestPage]]

"""

        self.r.set('wiki_Index', wiki_index)

    def test_index(self):
        response = self.app.get("/")
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        print response.body
        self.assertIn("<title>Home - Newcastle Makerspace</title>", response.body)
        self.assertIn("Casablanca", response.body)

    def test_about(self):
        response = self.app.get("/about")
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        print response.body
        self.assertIn("<title>About - Newcastle Makerspace</title>", response.body)
        self.assertIn("was started in early 2014", response.body)

    def test_contact(self):
        response = self.app.get("/contact")
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        print response.body
        self.assertIn("<title>Contact - Newcastle Makerspace</title>", response.body)
        self.assertIn("21 Gordon Avenue", response.body)

    def test_login_page_unauthed(self):
        response = self.app.post("/login", params={'username': 'Bob', 'password': 'test'})
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn('<b>Hello Bob! Nice to meet you. Bye!</b>', response.body)

    def test_login_page_authed_wrong_password(self):
        response = self.app.post("/login", params={'username': 'dkpw', 'password': '1234'})
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn('<b>Hello "dkpw", not even close.</b>', response.body)

    def test_login_page_authed_correct_password(self):
        response = self.app.post("/login", params={'username': 'dkpw', 'password': 'password1'})
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn('<b>Hello dkpw, welcome back!</b>', response.body)

    def test_wiki_page_read(self):
        response = self.app.get("/wiki/TestPage")
        print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn("<em>bold</em>", response.body)

    def test_wiki_index_read(self):
        response = self.app.get("/wiki/Index")
        print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn("Makerspace", response.body)

    def test_admin_page_unauthed(self):
        response = self.app.get("/admin", expect_errors=True, status=403)
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "403 Forbidden")

    def test_admin_page_authed(self):
        # do login first
        response = self.app.post("/login", params={'username': 'dkpw', 'password': 'password1'})
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        # check admin page
        response = self.app.get("/admin")
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")

