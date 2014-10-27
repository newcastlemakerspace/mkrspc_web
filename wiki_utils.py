from __future__ import print_function
import redis
import hashlib
import uuid
import base64
import os
import datetime
from bottle import Request, response
from site_config import static_files_root, auth_salt_secret, REDIS_DB


class WikiUtils(object):

    def __init__(self, redis_conn):
        self.redis_conn = redis_conn
        self.r = redis_conn

    def create_wiki_root_category(self):
        root_cat = str(uuid.uuid4())
        self.r.set("wiki_root_category", root_cat)
        self.r.set("wiki_category_name_%s" % root_cat, 'wiki_root')

    def wiki_root_category(self):
        root_uuid = self.r.get("wiki_root_category")
        assert root_uuid is not None
        return root_uuid

    def create_wiki_category(self, parent_id, cat_name):
        print("creating category in parent category with id %s" % parent_id)
        parent_uuid = uuid.UUID(parent_id)
        subcats_key = "wiki_sub_categories_%s" % parent_uuid
        print("The subcats key is %s" % subcats_key)
        new_cat_id = str(uuid.uuid4())
        print("New category id is %s" % new_cat_id)
        self.r.rpush(subcats_key, new_cat_id)
        self.r.set("wiki_category_name_%s" % new_cat_id, cat_name)
        return new_cat_id

    def wiki_root_categories(self):
        wiki_root_id = self.wiki_root_category()
        subcats_list_key = "wiki_sub_categories_%s" % wiki_root_id
        cat_count = self.r.llen(subcats_list_key)
        cat_ids = self.r.lrange(subcats_list_key, 0, cat_count)
        return cat_ids

    def name_for_wiki_cat_id(self, cat_id):
        cat_name = self.r.get("wiki_category_name_%s" % cat_id)
        return cat_name

    def create_wiki_article(self, cat_id, slug, title, body):
        r = self.redis_conn
        article_id = str(uuid.uuid4())
        print("New article id is %s" % article_id)
        art_key = 'wiki_article_%s' % article_id
        r.set(art_key, body)
        r.set('wiki_slug_%s' % slug, article_id)
        r.set('wiki_article_slug_%s' % article_id, slug)
        r.set('wiki_article_title_%s' % article_id, title)
        cat_articles_key = "wiki_category_articles_%s" % cat_id
        r.rpush(cat_articles_key, article_id)
        return article_id

    def wiki_articles_in_category(self, cat_id):
        cat_articles_key = "wiki_category_articles_%s" % cat_id
        return self.r.lrange(cat_articles_key, 0, 999)

    def wiki_article_body(self, art_id):
        r = self.redis_conn
        art_key = 'wiki_article_%s' % art_id
        print ("Fetch article body for %s" % art_key)
        body = r.get(art_key)
        return body

    # these were for the old categories structure

    # def create_wiki_category(self, cat_name):
    #     r = self.redis_conn
    #     cat_id = str(uuid.uuid4())
    #     cat_key = "wiki_cat_%s" % cat_id
    #     r.set(cat_key, cat_name)
    #     r.lpush("wiki_cats", cat_key)
    #     return cat_id

    # def test_make_wiki_page(self):
    #     slug, title, body_md = ("SuTests", "site utils testing", "**markdown")
    #     self.su.create_wiki_page(slug, title, body_md)


    # =============================================

    # todo





    def _init_wiki(self):
        default_text = """***Root article"""
        article_slug = 'Index'
        article_name = "Makerspace Wiki Index Page"
        self.create_wiki_page(article_slug, article_name, default_text)

        default_text = """
Test article
===

This text is _italic_

This text is __bold__

NB: unit tests look for this text.

        """
        article_slug = 'TestPage'
        article_name = "Makerspace Wiki Test Page"
        self.create_wiki_page(article_slug, article_name, default_text)
    #
    # def create_wiki_page(self, slug, title, body):
    #     r = self.redis_conn
    #     article_id = str(uuid.uuid4())
    #     art_key = 'wiki_article_%s' % article_id
    #     r.set(art_key, body)
    #     r.set('wiki_slug_%s' % slug, article_id)
    #     r.set('wiki_article_slug_%s' % article_id, slug)
    #     r.set('wiki_article_title_%s' % article_id, title)
    #
    # def create_wiki_category(self, cat_name):
    #     r = self.redis_conn
    #     cat_id = str(uuid.uuid4())
    #     cat_key = "wiki_cat_%s" % cat_id
    #     r.set(cat_key, cat_name)
    #     r.lpush("wiki_cats", cat_key)
    #     return cat_id
    #
    # def wiki_index(self):
    #     r = self.redis_conn
    #     cat_keys = r.lrange("wiki_cats", 0, 99)
    #     cats = []
    #     for cat_key in cat_keys:
    #         cat = r.get(cat_key)
    #         #print(cat_key, cat)
    #         subcats_key = "wiki_subcats_%s" % cat_key
    #         subcat_keys = r.lrange(subcats_key, 0, 99)
    #         subcats = []
    #         for sc_key in subcat_keys:
    #             subcat = r.get(sc_key)
    #             #print(" - sub %s %s" % (sc_key, subcat))
    #             subcats.append((sc_key, subcat,))
    #
    #         cats.append((cat_key, cat, subcats))
    #
    #     return cats
    #
    # def wiki_root_categories(self):
    #     r = self.redis_conn
    #     cat_count = r.llen("wiki_cats")
    #     cats = r.lrange("wiki_cats", 0, cat_count)
    #     return cats
    #
    #         #"wiki_cat_%s" % str(uuid.uuid4())
    #     #r.set(cat_key, cat_name)
    #     #r.lpush("wiki_cats", cat_key)
    #
