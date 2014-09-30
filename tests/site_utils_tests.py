from unittest import TestCase
from site_utils import SiteUtils

class SiteUtilsTest(TestCase):

    def test_make_wiki_page(self):
        slug, title, body_md = ("SuTests", "site utils testing", "**markdown")
        self.su.create_wiki_page(slug, title, body_md)

    def test_make_user(self):
        self.su.make_user("bob", "password1")

    def setUp(self):
        self.su = SiteUtils()
