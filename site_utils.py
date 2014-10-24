from __future__ import print_function
import redis
import hashlib
import uuid
import base64
import os
import datetime
from bottle import Request, response
from site_config import static_files_root, auth_salt_secret, REDIS_DB


class SiteUtils(object):

    def __init__(self):
        self.redis_conn = self.connect_redis()

    def connect_redis(self):
        # TODO connection pooling
        #r = redis.StrictRedis(db=REDIS_DB)
        r = redis.Redis(db=REDIS_DB)
        assert isinstance(r, redis.Redis)
        return r

    def make_user(self, username, password):
        hash_object = hashlib.sha256(auth_salt_secret + password)
        hex_dig = hash_object.hexdigest()
        self.redis_conn.set('User_Pwd_%s' % username, hex_dig)

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

    def _init_superuser(self):
        self.redis_conn.delete('mkrspc_superusers')
        dkpw_passwd = u'password1'
        dkpw_user = u'dkpw'
        self.redis_conn.lpush('mkrspc_superusers', dkpw_user)
        self.make_user(dkpw_user, dkpw_passwd)

        alice_passwd = u'puppies'
        alice_user = u'alice'
        self.make_user(alice_user, alice_passwd)

    def check_db_version(self):
        key = 'mkrspc_db_version'
        r = self.redis_conn
        db_version = r.get(key)
        if db_version is None:
            db_version = "0.1.0"
            r.set(key, db_version)
            self._init_superuser()
            self._init_wiki()
        return db_version

    def user_exists(self, user):
        r = self.redis_conn
        user_passwd_record = r.get('User_Pwd_%s' % user)
        if user_passwd_record is not None:
            return True
        else:
            return False

    def do_login(self, user, passwd):
        r = self.redis_conn
        user_passwd_record = r.get('User_Pwd_%s' % user)
        if user_passwd_record is not None:
            hash_object = hashlib.sha256(auth_salt_secret + passwd)
            hex_dig = hash_object.hexdigest()
            #print(hex_dig)
            if hex_dig == user_passwd_record:
                # The passwords match OK, so create a token.
                token = str(uuid.uuid4())
                # Store token in Redis. (Valid for 1000 milli-fortnights.)
                r.setex(('User_Auth_Cookie_%s' % token), user, 60 * 60 * 24 * 14)
                # Return token to be set as a cookie.
                return token
            else:
                return None

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

    def create_wiki_page(self, slug, title, body):
        r = self.redis_conn
        article_id = str(uuid.uuid4())
        art_key = 'wiki_article_%s' % article_id
        r.set(art_key, body)
        r.set('wiki_slug_%s' % slug, article_id)
        r.set('wiki_article_slug_%s' % article_id, slug)
        r.set('wiki_article_title_%s' % article_id, title)

    def wiki_index(self):
        r = self.redis_conn
        cat_keys = r.lrange("wiki_cats", 0, 99)
        cats = []
        for cat_key in cat_keys:
            cat = r.get(cat_key)
            #print(cat_key, cat)
            subcats_key = "wiki_subcats_%s" % cat_key
            subcat_keys = r.lrange(subcats_key, 0, 99)
            subcats = []
            for sc_key in subcat_keys:
                subcat = r.get(sc_key)
                #print(" - sub %s %s" % (sc_key, subcat))
                subcats.append((sc_key, subcat,))

            cats.append((cat_key, cat, subcats))

        return cats
