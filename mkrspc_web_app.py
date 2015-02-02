from __future__ import print_function
import os

from bottle import request, response, run, Bottle, view, abort, redirect
from bottle import static_file
from bottle import FormsDict

from site_config import static_files_root
from site_utils import SiteUtils
from mkrspc_web_app_wiki_pages import wiki_app
from models.site_message import SiteMessage, SM_ERROR, SM_VALIDATION_FAIL, SM_SUCCESS

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
    if message is not None:
        assert isinstance(message, SiteMessage)
    su = page_init()  # su = a SiteUtils instance
    #su.check_db_version()
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


@app.route('/admin')
@view('templates/admin')
def admin(message=None):
    if message is not None:
        assert isinstance(message, SiteMessage)
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
        'site_message': message,
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
        return index(message=SiteMessage("!Login failed, invalid username or password."))


@app.get('/user_profile')
@view('templates/user_profile')
def user_page(site_message=None):

    if site_message is not None:
        assert isinstance(site_message, SiteMessage)

    su = page_init()

    user_info = su.check_auth_cookie(request)
    if user_info is None:
        abort(403, "Forbidden")

    context = {
        'title': "User profile - Newcastle Makerspace",
        'menu': su.menu(None, user_info),
        'site_message': site_message,
        'user_message': su.user_greeting(user_info),
        'wiki_edits_log': [],
        'user_name': user_info[0]
    }

    return context


@app.post('/change_password')
def change_password():
    su = page_init()

    user_info = su.check_auth_cookie(request)
    if user_info is None:
        abort(403, "Forbidden")

    user_name = user_info[0]

    paswd_form = request.forms
    assert isinstance(paswd_form, FormsDict)

    old_pass = paswd_form.old_password
    new_pass = paswd_form.new_password
    confirm_pass = paswd_form.confirm_new_password

    if new_pass != confirm_pass:
        print(new_pass, confirm_pass)
        return user_page(site_message=SiteMessage("?Passwords do not match."))

    if len(new_pass) < 7:
        print(new_pass, confirm_pass)
        return user_page(site_message=SiteMessage("?Password must be at least 6 charaacters."))

    if not su.compare_password(user_name, old_pass):
        return user_page(site_message=SiteMessage("?Password incorrect."))

    su.change_user_password(user_name, old_pass, new_pass)

    if not su.compare_password(user_name, new_pass):
        return user_page(
            site_message=SiteMessage("!Password change failed for an unknown reason. Please contact an administrator.")
        )

    return user_page(site_message=SiteMessage("*Password change was successful."))


@app.post('/admin_add_user')
def admin_add_user():
    su = page_init()

    user_info = su.check_auth_cookie(request)
    if user_info is None:
        abort(403, "Forbidden")
    if user_info[1] is False:  # superuser?
        abort(403, "Forbidden")

    new_user_form = request.forms
    assert isinstance(new_user_form, FormsDict)
    user = new_user_form.newusername
    passwd = new_user_form.newpassword
    confirm = new_user_form.confirmpassword

    # make sure user does not exist already.
    if su.user_exists(user):
        return admin(message=SiteMessage("User already exists, try another username.", SM_VALIDATION_FAIL))

    # password was typed correctly?
    if passwd != confirm:
        return admin(message=SiteMessage("Passwords do not match.", SM_VALIDATION_FAIL))

    try:
        su.make_user(user, passwd)
    except Exception as e:
        return admin(message=SiteMessage("An error occurred: %s" % e.message, SM_ERROR))
    else:
        return admin(message=SiteMessage("User created successfully.", SM_SUCCESS))


@app.get('/admin_do_backup')
def admin_do_backup():
    su = page_init()

    user_info = su.check_auth_cookie(request)
    if user_info is None:
        abort(403, "Forbidden")
    if user_info[1] is False:  # superuser?
        abort(403, "Forbidden")

    #backup_filename = su.take_backup()
    #assert backup_filename is not None

    try:
        backup_filename = su.take_backup()
        msg = 'Backup successful. <a href="%s">%s</a>' % ('/static/backups/' + backup_filename, backup_filename)
        return admin(message=SiteMessage(msg, SM_SUCCESS))
    except Exception as e:
        return admin(message=SiteMessage("Backup failed. [%s]" % e.message, SM_ERROR))


@app.post('/image_upload')
def do_upload():
    caption = request.forms.get('caption')
    upload = request.files.get('upload')

    name, ext = os.path.splitext(upload.filename)
    if ext not in ('.png', '.jpg', '.jpeg'):
        return user_page(
            site_message=SiteMessage("File extension not allowed. [Use .png, .jpg or .jpeg]", SM_VALIDATION_FAIL)
        )

    try:
        save_path = os.path.join(static_files_root, "upload", "images")
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_path = os.path.join(save_path, upload.filename)
        upload.save(file_path)

    except Exception as e:
        return user_page(site_message=SiteMessage("Upload failed: " + e.message, SM_ERROR))

    return user_page(site_message=SiteMessage("Image upload was successful.", SM_SUCCESS))


@app.get('/dev_test')
@view('templates/dev_test')
def dev_test_page(site_message=None):

    if site_message is not None:
        assert isinstance(site_message, SiteMessage)

    su = page_init()

    user_info = su.check_auth_cookie(request)
    if user_info is None:
        abort(403, "Forbidden")

    context = {
        'title': "User profile - Newcastle Makerspace",
        'menu': su.menu(None, user_info),
        'site_message': site_message,
        'user_message': su.user_greeting(user_info),
        'wiki_edits_log': [],
        'user_name': user_info[0]
    }

    return context



if __name__ == "__main__":
    run(app, host='0.0.0.0', port=8088, debug=True, reloader=True)


