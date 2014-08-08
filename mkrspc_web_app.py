import markdown
import redis
import hashlib
import uuid

from bottle import request, response, run, template, Bottle, view, abort, Request
from bottle import static_file
from bottle import FormsDict
from collections import defaultdict

from site_config import static_files_root, auth_salt_secret


app = Bottle(catchall=False)

def connect_redis():
    # TODO connection pooling
    r = redis.StrictRedis(db=3)  # 3 for testing
    return r


def _check_auth_cookie(req):
    assert isinstance(req, Request)
    req_token = req.cookies.ncms_auth
    if req_token is None:
        return None
    else:
        r = connect_redis()
        auth_token_name = r.get('User_Auth_Cookie_%s' % req_token)
        if auth_token_name is None:
            print(" - auth cookie not found in Redis")
            return None
        else:
            print(" - auth cookie found OK")
            # todo check superuser status
            return (auth_token_name, False)


def _menu(selected, show_admin=True):

    if show_admin:
        admin_menu_entry = """
        <li class="%(sel_admin)s">
            <a href="/admin"><i class="fa fa-cog fa-fw"></i>&nbsp; Admin</a>
        </li>
        """
    else:
        admin_menu_entry = ''

    menu_template = """
            <ul class='menu'>
                <li class="%(sel_home)s">
                    <a href="/"><i class="fa fa-home fa-fw"></i>&nbsp; Home</a>
                </li>
                <li class="%(sel_about)s">
                    <a href="/about"><i class="fa fa-question-circle fa-fw"></i>&nbsp; About</a>
                </li>
                <li class="%(sel_contact)s">
                    <a href="/contact"><i class="fa fa-envelope fa-fw"></i>&nbsp; Contact</a>
                </li>
                <li class="%(sel_wiki)s">
                    <a href="/wiki/Index"><i class="fa fa-pencil-square-o fa-fw"></i>&nbsp; Wiki</a>
                </li>
                %(admin)s
            </ul>

            """

    selections = defaultdict(lambda: 'sibling')
    selections[selected] = 'selected'
    selections['admin'] = admin_menu_entry % selections

    return menu_template % selections


def _user_greeting(req):
    user_info = _check_auth_cookie(req)
    if user_info is not None:
        if user_info[1]:
            return "Hi %s" % user_info[0]
        else:
            return "Greetings %s" % user_info[0]
    else:
        return ""


@app.route('/static/<filepath:path>')
def server_static(filepath):
    configured_static_filepath = static_files_root
    return static_file(filepath, root=configured_static_filepath)


@app.route('/')
@view('templates/mkrspc_front')
def index():

    context = {
        'title': "Home - Newcastle Makerspace",
        'menu': _menu('sel_home'),
        'user_message': _user_greeting(request)
    }

    with open('content/home.html', 'r') as content_file:
        context['main_content'] = content_file.read()

    return context

@app.route('/about')
@view('templates/mkrspc_front')
def about():

    context = {
        'title': "About - Newcastle Makerspace",
        'menu': _menu('sel_about'),
        'user_message': _user_greeting(request)
    }

    with open('content/about.html', 'r') as content_file:
        context['main_content'] = content_file.read()

    return context


@app.route('/contact')
@view('templates/mkrspc_front')
def about():

    context = {
        'title': "Contact - Newcastle Makerspace",
        'menu': _menu('sel_contact'),
        'user_message': _user_greeting(request)
    }

    with open('content/contact.html', 'r') as content_file:
        context['main_content'] = content_file.read()

    return context

@app.route('/admin')
@view('templates/mkrspc_front')
def admin():

    if _check_auth_cookie(request) is None:
        abort(403, "Forbidden")

    context = {
        'title': "Administration - Newcastle Makerspace",
        'menu': _menu('sel_admin'),
        'user_message': _user_greeting(request)
    }

    with open('content/admin.html', 'r') as content_file:
        context['main_content'] = content_file.read()

    return context

@app.post('/login')
def login_post():
    login_form = request.forms
    assert isinstance(login_form, FormsDict)

    # todo never print passwords (after it's debugged....)
    #print "login for [%s] with passwd [%s]" % (login_form.username, login_form.password)
    #print login_form.keys()

    user = login_form.username
    passwd = login_form.password

    # todo write auth module
    r = connect_redis()
    user_passwd_record = r.get('User_Pwd_%s' % user)
    if user_passwd_record is not None:
        hash_object = hashlib.sha256(auth_salt_secret + passwd)   # TODO: don't deploy with this salt!
        hex_dig = hash_object.hexdigest()
        #print(hex_dig)
        if hex_dig == user_passwd_record:

            # passwords match OK
            # now set a cookie
            token = str(uuid.uuid4())
            r = connect_redis()
            r.set('User_Auth_Cookie_%s' % token, user)
            response.set_cookie('ncms_auth', token)


            return "<b>Hello %s, welcome back!</b>" % request.forms.username
        else:
            return '<b>Hello "%s", not even close.</b>' % request.forms.username

    return "<b>Hello %s! Nice to meet you. Bye!</b>" % request.forms.username


@app.route('/wiki/<slug>/')
@app.route('/wiki/<slug>')
def wiki(slug):

    r = connect_redis()
    md_src = r.get('wiki_' + slug)
    md = markdown.Markdown(extensions=['wikilinks(base_url=/wiki/,html_class=myclass)'])
    #html = markdown.markdown(md_src, ['wikilinks(base_url=/wiki/)'])
    html = md.convert(md_src)

    editable = False
    if _check_auth_cookie(request) is not None:
        editable = True

    context = {
        'title': "Contact - Newcastle Makerspace",
        'menu': _menu('sel_wiki'),
        'main_content': html,
        'editable': editable,
        'user_message': _user_greeting(request)
    }

    return template('templates/mkrspc_wiki', context)

    #return template('<b>Hello {{name}}!</b>', name=username)

if __name__ == "__main__":

    run(app, host='localhost', port=8080, debug=True, reloader=True)
