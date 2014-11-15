from unittest import TestCase
from site_utils import SiteUtils

class SiteUtilsTest(TestCase):

    def test_make_wiki_page(self):
        wu = self.su.wu
        cat_id = wu.create_wiki_category(wu.wiki_root_category(), "Domestic pets")
        slug, title, body_md = ("Ocelots_(Pets)", "Ocelots make good pets", "**Ocelots (WIP)")
        wiki_article_id = self.su.wu.create_wiki_article(cat_id, slug, title, body_md)
        art = self.su.redis_conn.get('wiki_article_%s' % wiki_article_id)
        self.assertIsNotNone(art)

    def test_make_user(self):
        self.su.make_user("bob", "password1")

    def test_change_user_password(self):
        username = 'alice'
        old_pass = 'puppies'
        new_pass = 'kittens'
        self.su.change_user_password(username, old_pass, new_pass)
        login_result = self.su.do_login(username, new_pass)
        self.assertIsNotNone(login_result)

    def setUp(self):
        self.su = SiteUtils()
