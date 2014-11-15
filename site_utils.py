from __future__ import print_function
import redis
import hashlib
import uuid
import base64
import os
import datetime
from bottle import Request, response
from site_config import static_files_root, auth_salt_secret, REDIS_DB
from wiki_utils import WikiUtils

class SiteUtils(object):

    def __init__(self, redis_connection=None):
        if redis_connection is None:
            self.redis_conn = self.connect_redis()
        else:
            self.redis_conn = redis_connection
        self.wu = WikiUtils(self.redis_conn)
        self._check_db_version()  # will create initial data if missing

    def connect_redis(self):
        # TODO connection pooling
        #r = redis.StrictRedis(db=REDIS_DB)
        r = redis.Redis(db=REDIS_DB)
        assert isinstance(r, redis.Redis)
        return r

    def _init_wiki(self):
        #print("Wiki init **************************************************************")
        root_id = self.wu.create_wiki_root_category()

        default_text = """***Root article"""
        article_slug = 'Index'
        article_name = "Makerspace Wiki Index Page"
        self.wu.create_wiki_article(root_id, article_slug, article_name, default_text)

        default_text = """
Test article about badgers
===

We like __badgers__ because badgers are _awesome_

NB: unit tests look for this text.

        """
        article_slug = 'Badgers'
        article_name = "Test Page About Badgers"

        subcat_id = self.wu.create_wiki_category(root_id, "Wildlife")
        self.wu.create_wiki_article(subcat_id, article_slug, article_name, default_text)

    def _init_superuser(self):
        self.redis_conn.delete('mkrspc_superusers')
        dkpw_passwd = u'password1'
        dkpw_user = u'dkpw'
        self.redis_conn.lpush('mkrspc_superusers', dkpw_user)
        self.make_user(dkpw_user, dkpw_passwd)

        alice_passwd = u'puppies'
        alice_user = u'alice'
        self.make_user(alice_user, alice_passwd)

    def _check_db_version(self):
        key = 'mkrspc_db_version'
        r = self.redis_conn
        db_version = r.get(key)
        if db_version is None:
            db_version = "0.1.0"
            r.set(key, db_version)
            self._init_superuser()
            self._init_wiki()
        return db_version

    def make_user(self, username, password):
        hash_object = hashlib.sha256(auth_salt_secret + password)
        hex_dig = hash_object.hexdigest()
        self.redis_conn.set('User_Pwd_%s' % username, hex_dig)

    def user_exists(self, user):
        r = self.redis_conn
        user_passwd_record = r.get('User_Pwd_%s' % user)
        if user_passwd_record is not None:
            return True
        else:
            return False

    def change_user_password(self, username, old_passwd, new_password):
        if self._compare_password(username, old_passwd):
            hash_object = hashlib.sha256(auth_salt_secret + new_password)
            hex_dig = hash_object.hexdigest()
            self.redis_conn.set('User_Pwd_%s' % username, hex_dig)

    def do_login(self, user, passwd):
        r = self.redis_conn
        if self._compare_password(user, passwd):
            # The password is valid, so create a token.
            token = str(uuid.uuid4())
            # Store token in Redis. (Valid for 1000 milli-fortnights.)
            r.setex(('User_Auth_Cookie_%s' % token), user, 60 * 60 * 24 * 14)
            # Return token to be set as a cookie.
            return token
        else:
            return None

    def _compare_password(self, user, entered_password):
        r = self.redis_conn
        user_passwd_record = r.get('User_Pwd_%s' % user)
        if user_passwd_record is not None:
            hash_object = hashlib.sha256(auth_salt_secret + entered_password)
            hex_dig = hash_object.hexdigest()
            #print(hex_dig)
            if hex_dig == user_passwd_record:
                return True
            else:
                return False

    def take_backup(self):

        outdir = os.path.join(static_files_root, 'backups')
        if not os.path.exists(outdir):
            os.mkdir(outdir)

        dt = datetime.datetime
        outfilename = "mkrspc_web_backup_%s.txt" % (dt.now().isoformat())
        outpath = os.path.join(outdir, outfilename)
        outf = open(outpath, 'wt')
        
        def wr(line):
            print(line, file=outf)
        
        r = self.redis_conn
        keys = r.keys('*')
        wr("====BEGIN====")
        wr(len(keys))
        for k in keys:
            t = r.type(k)
            wr('--------------------------------')
            wr(len(k))
            wr(k)
            wr(len(t))
            wr(t)
            if t == 'list':
                list_length = r.llen(k)
                wr('%d' % list_length)
                list_items = r.lrange(k, 0, list_length)
                for li in list_items:
                    b64_li = base64.b64encode(li)
                    wr(len(b64_li))
                    wr(b64_li)
            elif t == 'string':
                val = r.get(k)
                b64_val = base64.b64encode(val)
                wr(len(b64_val))
                wr(b64_val)
            else:
                raise ValueError("Unhandled Redis value type: %s" % t)

        wr("====END====")
        outf.close()

        return outfilename

    def check_auth_cookie(self, req):
        assert isinstance(req, Request)
        req_token = req.cookies.ncms_auth
        if req_token is None:
            return None
        else:
            r = self.redis_conn
            auth_token_name = r.get('User_Auth_Cookie_%s' % req_token)
            if auth_token_name is None:
                #print(" - auth cookie not found in Redis")
                return None
            else:
                #print(" - auth cookie found OK")
                superusers = r.lrange('mkrspc_superusers', 0, 9)
                #print(superusers)
                if auth_token_name in superusers:
                    return (auth_token_name, True)
                else:
                    return (auth_token_name, False)

    def remove_auth_cookie(self, req):
        assert isinstance(req, Request)
        req_token = req.cookies.ncms_auth
        if req_token is None:
            return None
        else:
            r = self.redis_conn
            r.delete('User_Auth_Cookie_%s' % req_token)
            response.set_cookie('ncms_auth', '')

    def _menu_entry(self, label, url, icon, selection_id, selected_entry, nav_style='default'):

        if selection_id == selected_entry:
            selection_class = "selected"
        else:
            selection_class = "sibling"

        if nav_style == 'default':
            html = """
            <li class="%s">
                <a href="%s"><i class="fa %s fa-fw"></i>&nbsp;%s</a>
            </li>
            """ % (selection_class, url, icon, label)
        elif nav_style == 'wiki':
            html = """
            <li class="%s">
                <a href="%s"><i class="fa %s fa-fw"></i>&nbsp;&nbsp;&nbsp; %s</a>
            </li>
            """ % (selection_class, url, icon, label)
        else:
            raise Exception("Unknown nav_style [%s]" % nav_style)

        return html

    def menu(self, selected, user_info, nav_style='default'):

        _menu_entry = self._menu_entry  # local ref to function

        menu_template = """
                <ul class="%(nav_style)s icons">
                    %(home)s
                    %(about)s
                    %(wiki)s
                    %(admin)s
                </ul>
                """

        replacements = dict()
        replacements['nav_style'] = 'menu_%s' % nav_style
        if user_info and user_info[1] is True:
            assert isinstance(user_info, tuple)
            assert len(user_info) == 2
            replacements['admin'] = _menu_entry('Admin', '/admin', 'fa-cog', 'sel_admin', selected, nav_style)
        else:
            replacements['admin'] = ''

        replacements['home'] = _menu_entry('Home', '/', 'fa-home', 'sel_home', selected, nav_style)
        replacements['about'] = _menu_entry('About', '/about', 'fa-question-circle', 'sel_about', selected, nav_style)
        replacements['wiki'] = _menu_entry('Wiki', '/wiki/Index', 'fa-pencil-square-o', 'sel_wiki', selected, nav_style)

        return menu_template % replacements

    def user_greeting(self, user_info):
        if user_info is not None:
            assert isinstance(user_info, tuple)
            assert len(user_info) == 2
            links = '<a href="/user_profile">%s</a> - <a href="/logout">log out</a>' % (user_info[0])
            if user_info[1] == True:
                return "Hail " + links
            else:
                return 'Hi ' + links
        else:
            return None

    def wiki_index(self):

        root = self.wu.wiki_root_category()
        root_cats = self.wu.wiki_categories_in_category(root)

        cats = []
        for cat_key in root_cats:
            cat = self.wu.name_for_wiki_cat_id(cat_key)
            article_keys = self.wu.wiki_articles_in_category(cat_key)
            articles = []
            subcat_keys = self.wu.wiki_categories_in_category(cat_key)

            subcats = subcat_keys
            for art_key in article_keys:
                slug = self.wu.wiki_article_slug(art_key)
                title = self.wu.wiki_article_title(art_key)
                articles.append((slug, title))

            cats.append((cat_key, cat, articles, subcats))

        return cats

    def wiki_root_categories(self):
        r = self.redis_conn
        cat_count = r.llen("wiki_cats")
        cats = r.lrange("wiki_cats", 0, cat_count)
        return cats

            #"wiki_cat_%s" % str(uuid.uuid4())
        #r.set(cat_key, cat_name)
        #r.lpush("wiki_cats", cat_key)

