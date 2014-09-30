from __future__ import print_function

import markdown
import redis
import hashlib
import uuid

from bottle import request, response, run, template, Bottle, view, abort, Request, redirect
from bottle import static_file
from bottle import FormsDict
from collections import defaultdict

from site_config import static_files_root, auth_salt_secret
from site_utils import SiteUtils
from mkrspc_web_app_wiki_pages import wiki_app

app = Bottle(catchall=False)
app.merge(wiki_app)

def page_init():
    su = SiteUtils()
    return su

@app.route('/static/<filepath:path>')
def server_static(filepath):
    configured_static_filepath = static_files_root
    return static_file(filepath, root=configured_static_filepath)

@app.route('/')
@view('templates/home')
def index(message=None):
    su = page_init()  # su = a SiteUtils instance
    su.check_db_version()
    user_info = su.check_auth_cookie(request)
    #print(user_info)
    if user_info is None:
        showlogin = True
    else:
        showlogin = False

    context = {
        'title': "Home - Newcastle Makerspace",
        'menu': su.menu('sel_home', user_info),
        'user_message': su.user_greeting(user_info),
        'site_message': message,
        'show_login_form': showlogin
    }

    return context

@app.route('/about')
@view('templates/about')
def about():
    su = page_init()
    user_info = su.check_auth_cookie(request)
    context = {
        'title': "About - Newcastle Makerspace",
        'menu': su.menu('sel_about', user_info),
        'user_message': su.user_greeting(user_info),
        'site_message': None
    }
    return context


@app.route('/contact')
@view('templates/contact')
def about():
    su = page_init()
    user_info = su.check_auth_cookie(request)
    context = {
        'title': "Contact - Newcastle Makerspace",
        'menu': su.menu('sel_contact', user_info),
        'user_message': su.user_greeting(user_info),
        'site_message': None
    }
    return context

@app.route('/admin')
@view('templates/admin')
def admin():
    su = page_init()
    user_info = su.check_auth_cookie(request)
    if user_info is None:
        abort(403, "Forbidden")
    if user_info[1] is False:  # superuser?
        abort(403, "Forbidden")

    # Will need wiki categories to select as parent of subcategories
    wiki_cats = su.wiki_index()

    context = {
        'title': "Administration - Newcastle Makerspace",
        'menu': su.menu('sel_admin', user_info),
        'user_message': su.user_greeting(user_info),
        'site_message': None,
        'wiki_categories': wiki_cats
    }
    return context

@app.get('/logout')
def logout():
    su = page_init()
    su.remove_auth_cookie(request)
    return index()

@app.post('/login')
def login_post():
    su = page_init()
    login_form = request.forms
    assert isinstance(login_form, FormsDict)
    user = login_form.username
    passwd = login_form.password
    login_token = su.do_login(user, passwd)

    if login_token is not None:
        response.set_cookie('ncms_auth', login_token)
        redirect('/')
    else:
        return index(message="Login failed, invalid username or password.")


if __name__ == "__main__":
    run(app, host='localhost', port=8080, debug=True, reloader=True)
