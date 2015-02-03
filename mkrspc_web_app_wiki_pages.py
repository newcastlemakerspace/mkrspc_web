from __future__ import print_function

import markdown
import uuid

from bottle import request, template, Bottle, abort, redirect
from bottle import FormsDict

from site_utils import SiteUtils

from models.site_message import SiteMessage, SM_ERROR, SM_VALIDATION_FAIL, SM_SUCCESS, SM_NOTIFY

wiki_app = Bottle()


def _safe_wiki_category_name(name):
    allowed_symbols = """()'"-_/"""
    bad_chars = [c for c in name if c != u' ' and not c.isalpha() and not c.isnumeric() and c not in allowed_symbols]
    if len(bad_chars) > 0:
        return bad_chars
    else:
        return None


def _safe_wiki_article_name(name):
    allowed_symbols = """()'"-_/%&"""
    bad_chars = [c for c in name if c != u' ' and not c.isalpha() and not c.isnumeric() and c not in allowed_symbols]
    if len(bad_chars) > 0:
        return bad_chars
    else:
        return None


def _safe_wiki_article_slug(name):
    allowed_symbols = """()-_"""
    bad_chars = [c for c in name if not c.isalpha() and not c.isnumeric() and c not in allowed_symbols]
    if len(bad_chars) > 0:
        return bad_chars
    else:
        return None


@wiki_app.route('/wiki/<slug>/')
@wiki_app.route('/wiki/<slug>')
def wiki(slug):

    su = SiteUtils()
    categories = su.wiki_index()
    print("Wiki page: ", categories)

    user_info = su.check_auth_cookie(request)
    editable = False
    if user_info is not None:
        editable = True

    r = su.redis_conn
    art_id = r.get('wiki_slug_' + slug)

    if art_id is None:
        site_message = "Missing article - %s" % slug
        art_slug = slug
        art_title = site_message
        html = "Please check the URL."
    else:
        md_src = r.get('wiki_article_' + art_id)
        art_title = r.get('wiki_article_title_' + art_id)
        art_slug = r.get('wiki_article_slug_' + art_id)
        md = markdown.Markdown(extensions=['wikilinks(base_url=/wiki/,html_class=wiki_internal)'])
        #html = markdown.markdown(md_src, ['wikilinks(base_url=/wiki/)'])
        html = md.convert(md_src)
        site_message = None

    context = {
        'title': u"Wiki - Newcastle Makerspace",
        'menu': su.menu('sel_wiki', user_info, nav_style='wiki'),
        'main_content': html,
        'allow_edit': editable,
        'user_message': su.user_greeting(user_info),
        'site_message': site_message,
        'wiki_index': categories,
        'slug': art_slug,
        'article_title': art_title
    }

    return template('templates/wiki', context)


@wiki_app.route('/wiki/edit/<slug>/')
@wiki_app.route('/wiki/edit/<slug>')
def wiki_edit_page(slug):

    su = SiteUtils()
    categories = su.wiki_index()
    print("Wiki page: ", categories)

    user_info = su.check_auth_cookie(request)
    editable = False
    site_message = None
    if user_info is not None:
        editable = True
    else:
        site_message = u"Sorry, you do not have permission to edit this page."

    r = su.redis_conn
    art_id = r.get('wiki_slug_' + slug)

    if art_id is None:
        #art_slug = slug
        art_title = site_message
        html = "Missing article - %s <br/>Please check the URL." % slug
        md_src = None
    else:
        md_src = r.get('wiki_article_' + art_id)
        art_title = r.get('wiki_article_title_' + art_id)
        art_slug = r.get('wiki_article_slug_' + art_id)
        #md = markdown.Markdown(extensions=['wikilinks(base_url=/wiki/,html_class=mkrspc_wiki)'])
        #html = markdown.markdown(md_src, ['wikilinks(base_url=/wiki/)'])
        html = '<h4 class="page-title">Editing article: "%s" (%s)</h4>' % (art_title, art_slug)


    if site_message is not None:
        sm = SiteMessage(site_message, SM_VALIDATION_FAIL)

    context = {
        'title': "Wiki - Newcastle Makerspace",
        'menu': su.menu('sel_wiki', user_info, nav_style='wiki'),
        'main_content': html,
        'editable': editable,
        'user_message': su.user_greeting(user_info),
        'wiki_index': categories,
        'site_message': site_message,
        'article_id': art_id,
        'article_title': art_title,
        'article_markdown': md_src
    }

    return template('templates/wiki_edit', context)


@wiki_app.route('/wiki/category/<cat_id>/')
@wiki_app.route('/wiki/category/<cat_id>')
def wiki_cat(cat_id, site_message=None):

    su = SiteUtils()
    categories = su.wiki_index()
    user_info = su.check_auth_cookie(request)
    editable = False
    if user_info is not None:
        editable = True

    cat_name = su.wu.name_for_wiki_cat_id(cat_id)

    #html = [u'<h3 class="page-title">Wiki > %s > %s</h3>' % (maincat_name, subcat_name)]
    assert isinstance(cat_name, basestring)
    html = [u'<h3 class="page-title">Wiki > %s</h3>' % cat_name]
    r = su.redis_conn
    articles = r.lrange('wiki_category_articles_' + cat_id, 0, 999)

    html += u'<p>%d articles:</p>\n<ul class="category-page-list">' % len(articles)

    for art_id in articles:
        art_slug_key = 'wiki_article_slug_%s' % art_id
        art_slug = r.get(art_slug_key)

        art_title_key = 'wiki_article_title_%s' % art_id
        art_title = r.get(art_title_key)

        html += u'<li class="category-page"><a class="wiki_internal" href="/wiki/%s">%s</a></li>' % (art_slug, art_title)

    html += u'</ul>'
    html = u"".join(html)

    context = {
        'title': "Wiki - Newcastle Makerspace",
        'menu': su.menu('sel_wiki', user_info, nav_style='wiki'),
        'main_content': html,
        'editable': editable,
        'user_message': su.user_greeting(user_info),
        'wiki_index': categories,
        'site_message': site_message,
        'category_id': cat_id,
        'category_name': cat_name
    }

    return template('templates/wiki_cat', context)


@wiki_app.post('/wiki/update_article')
def wiki_update_article():

    su = SiteUtils()
    user_info = su.check_auth_cookie(request)
    if user_info is None:
        abort(403, "Forbidden")

    # form is defined in wiki_edit.tpl
    article_form = request.forms
    assert isinstance(article_form, FormsDict)
    article_name = article_form.article_title.strip()
    article_body = article_form.article_markdown.strip()
    article_id = article_form.article_id

    r = su.redis_conn
    old_article_body = r.get('wiki_article_' + article_id)
    # save the old revision before doing anything else
    r.lpush('wiki_article_revision_%s' % article_id, old_article_body)

    # slugs never change
    art_slug = r.get('wiki_article_slug_%s' % article_id)

    r.set('wiki_article_title_%s' % article_id, article_name)
    r.set('wiki_article_%s' % article_id, article_body)

    redirect('/wiki/%s' % art_slug)

    #todo logging edit actions


@wiki_app.post('/wiki/new_article')
def wiki_new_article():

    su = SiteUtils()
    #categories = su.wiki_index()
    user_info = su.check_auth_cookie(request)
    if user_info is None:
        abort(403, "Forbidden")

    # form is defined in wiki_cat.tpl
    article_form = request.forms
    assert isinstance(article_form, FormsDict)
    article_name = article_form.article_title.strip()
    article_slug = article_form.article_slug.strip()
    cat_id = article_form.article_cat_id

    if len(article_slug) == 0:
        return wiki_cat(cat_id, site_message="No article slug given.")

    if len(article_name) == 0:
        return wiki_cat(cat_id, site_message="No article name given.")

    category_name = su.wu.name_for_wiki_cat_id(cat_id)
    if category_name is None:
        return wiki_cat(cat_id, site_message="Invalid category.")

    bad_chars = _safe_wiki_article_slug(article_slug)
    if bad_chars is not None:
        bad_slug_message = u"Sorry, these characters are not allowed in an article slug: %s" % u" ".join(bad_chars)
        return wiki_cat(cat_id, site_message=bad_slug_message)

    bad_chars = _safe_wiki_article_name(article_name)
    if bad_chars is not None:
        bad_cat_message = u"Sorry, these characters are not allowed in an article name: %s" % u" ".join(bad_chars)
        return wiki_cat(cat_id, site_message=bad_cat_message)

    #print("OK, we have a good article: %s %s" % (article_slug, article_name))

    default_text = """**%s** (New article)""" % article_name
    su.wu.create_wiki_article(cat_id, article_slug, article_name, default_text)

    return wiki(article_slug)


@wiki_app.post('/wiki/add_category')
def add_wiki_category():

    su = SiteUtils()
    wu = su.wu
    user_info = su.check_auth_cookie(request)

    if user_info is None:
        abort(403, "Forbidden")
    if user_info[1] is False:  # superuser?
        abort(403, "Forbidden")

    # form is defined in admin.tpl
    cat_form = request.forms
    assert isinstance(cat_form, FormsDict)
    cat_name = cat_form.category_name

    #print("add_category page got: ", cat_name)
    bad_cat_message = None

    cat_name = cat_name.strip()
    bad_chars = _safe_wiki_category_name(cat_name)

    if bad_chars is not None:
        bad_cat_message = u"Sorry, these characters are not allowed: %s" % u" ".join(bad_chars)

    if bad_cat_message is None:
        wiki_root_id = wu.wiki_root_category()
        wu.create_wiki_category(wiki_root_id, cat_name)
    else:
        print("Create category failed: %s" % bad_cat_message)

    context = {
        'title': u"Admin - Newcastle Makerspace",
        'menu': su.menu('sel_admin', user_info, nav_style='default'),
        'user_message': su.user_greeting(user_info),
        'site_message': bad_cat_message,
        'wiki_categories': su.wiki_index()
    }

    return template('templates/admin', context)

@wiki_app.post('/wiki/add_subcategory')
def add_wiki_subcategory():

    class SubcatCreateException(Exception):
        pass

    su = SiteUtils()
    wu = su.wu
    user_info = su.check_auth_cookie(request)

    if user_info is None:
        abort(403, "Forbidden")
    if user_info[1] is False:  # superuser?
        abort(403, "Forbidden")

    # form is defined in admin.tpl
    cat_form = request.forms
    assert isinstance(cat_form, FormsDict)
    cat_name = cat_form.category_name
    parent_cat_id = cat_form.parent

    print("add_subcategory page got: ", cat_name, parent_cat_id)
    bad_cat_message = None

    try:

        cat_name = cat_name.strip()
        try:
            parent_cat_as_uuid = uuid.UUID(parent_cat_id)
        except ValueError as e:
            fail_message = "Invalid parent category ID."
            raise SubcatCreateException(fail_message)

        parent_cat_name = wu.name_for_wiki_cat_id(parent_cat_as_uuid)

        print("PArent cat: ", parent_cat_name)
        if parent_cat_name is None:
            fail_message = u"The specified parent category does not exist."
            raise SubcatCreateException(fail_message)

        bad_chars = _safe_wiki_category_name(cat_name)
        if bad_chars is not None:
            fail_message = u"Sorry, these characters are not allowed: %s" % u" ".join(bad_chars)
            raise SubcatCreateException(fail_message)

        wiki_root_id = wu.wiki_root_category()
        wu.create_wiki_category(wiki_root_id, cat_name)
        print("Created OK")

    except SubcatCreateException as e:
        print("Failed, invalid inputs: %s" % e.message)
        bad_cat_message = e.message

    except Exception as e:
        print("Failed (general error: %s" % e.message)

    context = {
        'title': u"Admin - Newcastle Makerspace",
        'menu': su.menu('sel_admin', user_info, nav_style='default'),
        'user_message': su.user_greeting(user_info),
        'site_message': bad_cat_message,
        'wiki_categories': su.wiki_index()
    }

    return template('templates/admin', context)



#
# @wiki_app.post('/wiki/add_subcategory')
# def add_wiki_subcategory():
#
#     su = SiteUtils()
#     user_info = su.check_auth_cookie(request)
#
#     if user_info is None:
#         abort(403, "Forbidden")
#     if user_info[1] is False:  # superuser?
#         abort(403, "Forbidden")
#
#     # form is defined in admin.tpl
#     sub_cat_form = request.forms
#     assert isinstance(sub_cat_form, FormsDict)
#     main_cat_id = sub_cat_form.main_category
#     # todo Check that maincat exists
#     sub_cat_name = sub_cat_form.subcategory_name
#     sub_cat_name = sub_cat_name.strip()
#     sub_cat_id = 'wiki_subcat_%s' % str(uuid.uuid4())
#     print("new subcat: ", main_cat_id, sub_cat_id, sub_cat_name)
#     bad_chars = _safe_wiki_category_name(sub_cat_name)
#     bad_cat_message = None
#     if bad_chars is not None:
#         bad_cat_message = u"Sorry, these characters are not allowed: %s" % u" ".join(bad_chars)
#         print(bad_cat_message)
#
#     if bad_cat_message is None:
#         subcats_key = "wiki_subcats_%s" % main_cat_id
#         r = su.redis_conn
#         r.lpush(subcats_key, sub_cat_id)
#         r.set(sub_cat_id, sub_cat_name)
#
#     context = {
#         'title': u"Admin - Newcastle Makerspace",
#         'menu': su.menu('sel_admin', user_info, nav_style='default'),
#         'user_message': su.user_greeting(user_info),
#         'site_message': bad_cat_message,
#         'wiki_categories': su.wiki_index(),
#         'subcategory_id': sub_cat_id
#     }
#
#     return template('templates/admin', context)
