from webtest import TestApp, TestResponse
import redis
from unittest import TestCase
import hashlib
import mkrspc_web_app
from site_config import static_files_root, auth_salt_secret

class MkrspcWebTest(TestCase):


    def _make_user(self, username, password, redis_conn):
        hash_object = hashlib.sha256(auth_salt_secret + password)
        hex_dig = hash_object.hexdigest()
        self.r.set('User_Pwd_%s' % username, hex_dig)

    def _dummy_users(self, redis_conn):
        self.r.delete('mkrspc_superusers')
        self.r.lpush('mkrspc_superusers', u'dkpw')

        dkpw_passwd = u'password1'
        dkpw_user = u'dkpw'
        self._make_user(dkpw_user, dkpw_passwd, redis_conn)

        alice_passwd = u'puppies'
        alice_user = u'alice'
        self._make_user(alice_user, alice_passwd, redis_conn)

    def setUp(self):
        self.app = TestApp(mkrspc_web_app.app, extra_environ={'debug': 'True'})
        #for route in mkrspc_web_app.app.routes:
        #    print "App route: ", route
        #    pass
        self.r = redis.StrictRedis(db=3)  # 3 for testing
        self._dummy_users(self.r)

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

    def test_static_config(self):
        import os
        self.assertTrue(os.path.exists(static_files_root))

    def test_index(self):
        response = self.app.get("/")
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        #print response.body
        self.assertIn("<title>Home - Newcastle Makerspace</title>", response.body)
        self.assertIn("Casablanca", response.body)

    def test_about(self):
        response = self.app.get("/about")
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        #print response.body
        self.assertIn("<title>About - Newcastle Makerspace</title>", response.body)
        self.assertIn("was started in early 2014", response.body)

    def test_contact(self):
        response = self.app.get("/contact")
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        #print response.body
        self.assertIn("<title>Contact - Newcastle Makerspace</title>", response.body)
        self.assertIn("21 Gordon Avenue", response.body)

    def test_login_page_unauthed(self):
        response = self.app.post("/login", params={'username': 'Bob', 'password': 'test'})
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn('<b>Hello Bob! Nice to meet you. Bye!</b>', response.body)

    def test_login_page_authed_wrong_password(self):
        response = self.app.post("/login", params={'username': 'dkpw', 'password': '1234'})
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn('<b>Hello "dkpw", not even close.</b>', response.body)

    def test_login_page_authed_correct_password(self):
        response = self.app.post("/login", params={'username': 'dkpw', 'password': 'password1'})
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn('<b>Hello dkpw, welcome back!</b>', response.body)

    def test_wiki_page_read(self):
        response = self.app.get("/wiki/TestPage")
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn("<em>bold</em>", response.body)

    def test_wiki_index_read(self):
        response = self.app.get("/wiki/Index")
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn("Makerspace", response.body)

    def test_admin_page_unauthed(self):
        response = self.app.get("/admin", expect_errors=True, status=403)
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "403 Forbidden")

    def test_admin_page_authed_super(self):
        # do login first
        response = self.app.post("/login", params={'username': 'dkpw', 'password': 'password1'})
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        # check admin page
        response = self.app.get("/admin")
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")

    def test_admin_page_authed_nonsuper(self):
        # do login first
        response = self.app.post("/login", params={'username': 'alice', 'password': 'puppies'})
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "200 OK")
        # check admin page
        response = self.app.get("/admin")
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "403 Forbidden")
