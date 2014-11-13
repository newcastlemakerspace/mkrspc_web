from webtest import TestApp, TestResponse
import redis
import uuid
from unittest import TestCase
import hashlib
from mkrspc_web_app import app
from site_config import static_files_root, auth_salt_secret
from wiki_utils import WikiUtils
from site_utils import SiteUtils

class MkrspcWebTest(TestCase):

    def _do_admin_login(self):
        response = self.app.post("/login", params={'username': 'dkpw', 'password': 'password1'})
        assert isinstance(response, TestResponse)
        self.assertEqual("302 Found", response.status)
        response = response.follow()
        self.assertEqual("200 OK", response.status)

    def setUp(self):
        self.app = TestApp(app, extra_environ={'debug': 'True'})
        self.r = redis.Redis(db=3)  # 3 for testing
        self.r.flushdb()
        self.su = SiteUtils(redis_connection=self.r)
        self.wu = self.su.wu

    def test_all_routes_present(self):
        """The point of all this is to preserve bookmarked URLs."""
        text = []
        columns_header = "%-10s %-30s %s" % ("Method", "Rule", "Callback")
        print columns_header
        text.append(columns_header)
        for route in app.routes:
            entry_text = "%-10s %-30s %s" % (route.method, route.rule, route.callback.__name__)
            print entry_text
            text.append(entry_text)

        current_text = '\n'.join(text)

        previously_generated_text = """Method     Rule                           Callback
GET        /wiki/<slug>                   wiki
GET        /wiki/<slug>/                  wiki
GET        /wiki/edit/<slug>              wiki_edit_page
GET        /wiki/edit/<slug>/             wiki_edit_page
GET        /wiki/category/<cat_id>        wiki_cat
GET        /wiki/category/<cat_id>/       wiki_cat
POST       /wiki/update_article           wiki_update_article
POST       /wiki/new_article              wiki_new_article
POST       /wiki/add_category             add_wiki_category
POST       /wiki/add_subcategory          add_wiki_subcategory
GET        /static/<filepath:path>        server_static
GET        /                              index
GET        /about                         about
GET        /admin                         admin
GET        /logout                        logout
POST       /login                         login_post
POST       /admin_add_user                admin_add_user
GET        /admin_do_backup               admin_do_backup"""

        self.assertEqual(previously_generated_text, current_text)


    def test_aardvark_redis_db_is_empty_at_tests_start(self):
        keycount = len(self.r.keys('*'))
        self.assertEqual(keycount, 18)
        # 2 users, superuser list, wiki root id, wiki root name, articles, subcats..

    def test_static_config(self):
        import os
        self.assertTrue(os.path.exists(static_files_root))

    def test_index(self):
        response = self.app.get("/")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        #print response.body
        self.assertIn("<h3>Meeting times:</h3>", response.body)
        # login form should be visible if not logged in
        self.assertIn("<h3 class='page-title'>Member login</h3>", response.body)

    def test_about(self):
        response = self.app.get("/about")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        #print response.body
        self.assertIn("<title>About - Newcastle Makerspace</title>", response.body)
        self.assertIn("was started in early 2014", response.body)

    def test_login_page_unauthed(self):
        response = self.app.post("/login", params={'username': 'Bob', 'password': 'test'})
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn("Login failed, invalid username or password.", response.body)

    def test_login_page_authed_wrong_password(self):
        response = self.app.post("/login", params={'username': 'dkpw', 'password': '1234'})
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn("Login failed, invalid username or password.", response.body)

    def test_login_page_authed_correct_password(self):
        response = self.app.post("/login", params={'username': 'dkpw', 'password': 'password1'})
        assert isinstance(response, TestResponse)
        self.assertEqual("302 Found", response.status)
        response = response.follow()
        self.assertEqual("200 OK", response.status)
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn("""<div id="user-greeting">Hail <a href="/user_profile">dkpw</a> - <a href="/logout">log out</a></div>""", response.body)

    def test_wiki_badgers_page_read(self):
        response = self.app.get("/wiki/Badgers")
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn("<h1>Test article about badgers</h1>", response.body)
        self.assertIn("<p>We like <strong>badgers</strong> because badgers are <em>awesome</em></p>", response.body)
        self.assertIn("<p>NB: unit tests look for this text.</p>", response.body)

    def test_wiki_root_article_read(self):
        response = self.app.get("/wiki/Index")
        #print response.body
        self.assertTrue(len(response.body) > 0)
        self.assertIn("Makerspace", response.body)

    def test_admin_page_unauthed(self):
        response = self.app.get("/admin", expect_errors=True, status=403)
        assert isinstance(response, TestResponse)
        self.assertEqual("403 Forbidden", response.status)

    def test_admin_page_authed_super(self):
        # do login first
        response = self.app.post("/login", params={'username': 'dkpw', 'password': 'password1'})
        assert isinstance(response, TestResponse)
        self.assertEqual("302 Found", response.status)
        response = response.follow()
        self.assertEqual("200 OK", response.status)
        # check admin page
        response = self.app.get("/admin")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)

    def test_admin_page_authed_nonsuper(self):
        # do login first
        response = self.app.post("/login", params={'username': 'alice', 'password': 'puppies'})
        assert isinstance(response, TestResponse)
        self.assertEqual("302 Found", response.status)
        response = response.follow()
        self.assertEqual("200 OK", response.status)
        #self.assertEqual("403 Forbidden", response.status)
        # check admin page
        response = self.app.get("/admin", expect_errors=True)
        assert isinstance(response, TestResponse)
        self.assertEqual(response.status, "403 Forbidden")

    def test_admin_page(self):
        self._do_admin_login()
        # check admin page
        response = self.app.get("/admin")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)

    def test_admin_create_new_user(self):
        self._do_admin_login()
        response = self.app.post("/admin_add_user", params={'newusername': 'mary', 'newpassword': 'eagle', 'confirmpassword': 'eagle'})
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        self.assertIn("User created successfully.", response.body)

        response = self.app.post("/login", params={'username': 'mary', 'password': 'eagle'})
        assert isinstance(response, TestResponse)
        self.assertEqual("302 Found", response.status)
        response = response.follow()
        self.assertEqual("200 OK", response.status)

    def test_admin_create_new_user_but_it_already_exists(self):
        self._do_admin_login()
        response = self.app.post("/admin_add_user", params={'newusername': 'alice', 'newpassword': 'sharks', 'confirmpassword': 'sharks'})
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        self.assertIn("User already exists, try another username.", response.body)

    def test_admin_create_new_user_with_password_typo(self):
        self._do_admin_login()
        response = self.app.post("/admin_add_user", params={'newusername': 'eve', 'newpassword': 'squid', 'confirmpassword': 'skwid'})
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        self.assertIn("Passwords do not match.", response.body)

    def test_admin_take_backup(self):
        self._do_admin_login()
        response = self.app.get("/admin_do_backup")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        self.assertIn("Backup successful.", response.body)

    def test_create_category_direct(self):
        cat_name = "TestCategory"
        wiki_root_cat_id = self.wu.wiki_root_category()
        print "Wiki root id is: %s" % wiki_root_cat_id
        self.wu.create_wiki_category(wiki_root_cat_id, cat_name)
        cats = self.wu.wiki_root_categories()
        existing_cat_names = []
        for cat_id in cats:
            existing_cat_names.append(self.wu.name_for_wiki_cat_id(cat_id))

        self.assertIn(cat_name, existing_cat_names)

    def test_create_category_via_page(self):
        self._do_admin_login()
        # check admin page
        response = self.app.get("/admin")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        cat_name = "TestCategory"
        wiki_root_cat_id = self.wu.wiki_root_category()
        print "Wiki root id is: %s" % wiki_root_cat_id
        response = self.app.post("/wiki/add_category", params={'category_name': cat_name, 'parent': wiki_root_cat_id})
        self.assertEqual("200 OK", response.status)
        cats = self.wu.wiki_root_categories()
        existing_cat_names = []
        for cat_id in cats:
            existing_cat_names.append(self.wu.name_for_wiki_cat_id(cat_id))

        self.assertIn(cat_name, existing_cat_names)

    def test_create_subcategory_via_page(self):
        self._do_admin_login()
        # check admin page
        response = self.app.get("/admin")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        cat_name = "TestCategory"
        wiki_root_cat_id = self.wu.wiki_root_category()
        print "Wiki root id is: %s" % wiki_root_cat_id
        response = self.app.post("/wiki/add_subcategory", params={'category_name': cat_name, 'parent': wiki_root_cat_id})
        self.assertEqual("200 OK", response.status)
        cats = self.wu.wiki_root_categories()
        existing_cat_names = []
        for cat_id in cats:
            existing_cat_names.append(self.wu.name_for_wiki_cat_id(cat_id))

        self.assertIn(cat_name, existing_cat_names)

    def test_create_subcategory_via_page_bad_id(self):
        self._do_admin_login()
        # check admin page
        response = self.app.get("/admin")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        cat_name = "TestCategoryZ"
        cat_id = "notarealuuid"
        response = self.app.post("/wiki/add_category", params={'category_name': cat_name, 'parent': cat_id})

    def test_wiki_new_article_in_category(self):
        self._do_admin_login()
        # check admin page
        response = self.app.get("/admin")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        cat_name = "CategoryA"
        root_cat_id = self.wu.wiki_root_category()
        new_cat_id = self.wu.create_wiki_category(root_cat_id, cat_name)

        response = self.app.post(
            '/wiki/new_article',
            params={
                'article_cat_id': new_cat_id,
                'article_title': 'Article in Category A',
                'article_slug': 'ArticleInCategoryA'
            }
        )

        self.assertEqual("200 OK", response.status)
        cats = self.wu.wiki_root_categories()
        self.assertNotIn("No article slug given.", response)
        self.assertNotIn("No article title given.", response)
        self.assertNotIn("Invalid category.", response)

        existing_cat_names = []
        for cat_id in cats:
            existing_cat_names.append(self.wu.name_for_wiki_cat_id(cat_id))

        self.assertIn(cat_name, existing_cat_names)
        articles = self.wu.wiki_articles_in_category(new_cat_id)
        self.assertEqual(len(articles), 1)


    def _add_root_wiki_cat(self, cat_name):
        wiki_root_cat_id = self.wu.wiki_root_category()
        subcat_id = self.wu.create_wiki_category(wiki_root_cat_id, cat_name)
        return subcat_id

    def test_zebra_wiki_index(self):

        space_subcat_id = self._add_root_wiki_cat("Space Travel")
        lunar_art_id = self.wu.create_wiki_article(space_subcat_id, "LunarBadgers", "Lunar Badgers", "###Moon badgers!! (WIP)")
        wildlife_subcat_id = self._add_root_wiki_cat("Wildlife")
        terr_art_id = self.wu.create_wiki_article(wildlife_subcat_id, "Badgers", "Terrestrial Badgers", "###Boring badgers (WIP)")

        response = self.app.get("/wiki/Index")
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)
        #print response.body
        self.assertIn('href="/wiki/category/%s"' % space_subcat_id, response.body)
        self.assertIn('href="/wiki/category/%s"' % wildlife_subcat_id, response.body)

        response = self.app.get("/wiki/category/%s" % space_subcat_id)
        assert isinstance(response, TestResponse)
        self.assertIn('<a href="/wiki/LunarBadgers">Lunar Badgers</a>', response.body)
        self.assertNotIn('0 articles', response.body)
        self.assertEqual("200 OK", response.status)

        response = self.app.get("/wiki/category/%s" % wildlife_subcat_id)
        self.assertIn('<a href="/wiki/Badgers">Terrestrial Badgers</a>', response.body)
        self.assertNotIn('0 articles', response.body)
        assert isinstance(response, TestResponse)
        self.assertEqual("200 OK", response.status)



