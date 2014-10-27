from unittest import TestCase
from wiki_utils import WikiUtils
import redis


class WikiUtilsTest(TestCase):

    def setUp(self):
        self.r = redis.Redis(db=3)  # 3 for testing
        self.r.flushdb()
        self.wu = WikiUtils(self.r)
        self.wu.create_wiki_root_category()

    def test_create_category(self):
        cat_name = "TestCategory"
        wiki_root_cat_id = self.wu.wiki_root_category()
        print "Wiki root id is: %s" % wiki_root_cat_id
        self.wu.create_wiki_category(wiki_root_cat_id, cat_name)
        cats = self.wu.wiki_root_categories()
        existing_cat_names = []
        for cat_id in cats:
            existing_cat_names.append(self.wu.name_for_wiki_cat_id(cat_id))
        self.assertIn(cat_name, existing_cat_names)

    def test_new_article_in_category(self):
        cat_name = "CategoryA"
        root_cat_id = self.wu.wiki_root_category()
        new_cat_id = self.wu.create_wiki_category(root_cat_id, cat_name)

        title = 'Article in Category A'
        slug = 'ArticleInCategoryA'
        body = '##An Article about Aardvarks (WIP)'
        art_id = self.wu.create_wiki_article(new_cat_id, title, slug, body)

        print "The created article id is %s" % art_id

        art_body = self.wu.wiki_article_body(art_id)
        self.assertIsNotNone(art_body, "Wiki article body should exist.")

        art_ids = self.wu.wiki_articles_in_category(new_cat_id)
        self.assertIn(art_id, art_ids, "New article should be listed in category articles.")


    # def test_make_wiki_page(self):
    #     slug, title, body_md = ("SuTests", "site utils testing", "**markdown")
    #     self.su.create_wiki_page(slug, title, body_md)
