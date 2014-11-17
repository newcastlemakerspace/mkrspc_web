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
        existing_root = self.r.get("wiki_root_category")
        assert existing_root is None
        root_cat = str(uuid.uuid4())
        self.r.set("wiki_root_category", root_cat)
        self.r.set("wiki_category_name_%s" % root_cat, 'wiki_root')
        return root_cat

    def wiki_root_category(self):
        root_uuid = self.r.get("wiki_root_category")
        assert root_uuid is not None
        return root_uuid

    def create_wiki_category(self, parent_id, cat_name):
        #print("creating category in parent category with id %s" % parent_id)
        parent_uuid = uuid.UUID(parent_id)
        subcats_key = "wiki_sub_categories_%s" % parent_uuid
        #print("The subcats key is %s" % subcats_key)
        new_cat_id = str(uuid.uuid4())
        #print("New category id is %s" % new_cat_id)
        self.r.rpush(subcats_key, new_cat_id)
        self.r.set("wiki_category_name_%s" % new_cat_id, cat_name)
        return new_cat_id

    def wiki_root_categories(self):
        wiki_root_id = self.wiki_root_category()
        return self.wiki_categories_in_category(wiki_root_id)

    def name_for_wiki_cat_id(self, cat_id):
        key = "wiki_category_name_%s" % cat_id
        #print("name_for_wiki_cat_id = %s" % key)
        cat_name = self.r.get(key)
        return cat_name

    def create_wiki_article(self, cat_id, slug, title, body):
        r = self.redis_conn
        article_id = str(uuid.uuid4())
        #print("New article id is %s" % article_id)
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

    def wiki_categories_in_category(self, cat_id):
        cat_cats_key = "wiki_sub_categories_%s" % cat_id
        cat_count = self.r.llen(cat_cats_key)
        cat_ids = self.r.lrange(cat_cats_key, 0, cat_count)
        return cat_ids

    def wiki_article_body(self, art_id):
        r = self.redis_conn
        art_key = 'wiki_article_%s' % art_id
        body = r.get(art_key)
        return body

    def wiki_article_title(self, art_id):
        r = self.redis_conn
        art_key = 'wiki_article_title_%s' % art_id
        title = r.get(art_key)
        return title

    def wiki_article_slug(self, art_id):
        art_key = 'wiki_article_slug_%s' % art_id
        return self.r.get(art_key)
