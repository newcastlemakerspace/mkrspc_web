from __future__ import print_function

import markdown
import redis
import hashlib
import uuid

from bottle import request, response, run, template, Bottle, view, abort, Request, redirect
from bottle import static_file
from bottle import FormsDict
from collections import defaultdict
from site_config import static_files_root

from site_utils import check_auth_cookie, connect_redis, menu, user_greeting, wiki_index

wiki_app = Bottle()

def _safe_wiki_category_name(name):
    allowed_symbols = """()'"-_/"""
    bad_chars = [c for c in name if c != u' ' and not c.isalpha() and not c.isnumeric() and not c in allowed_symbols]
    if len(bad_chars) > 0:
        return bad_chars
    else:
        return None

def _safe_wiki_article_name(name):
    allowed_symbols = """()'"-_/%&"""
    bad_chars = [c for c in name if c != u' ' and not c.isalpha() and not c.isnumeric() and not c in allowed_symbols]
    if len(bad_chars) > 0:
        return bad_chars
    else:
        return None

def _safe_wiki_article_slug(name):

    bad_chars = [c for c in name if not c.isalpha() and not c.isnumeric()]
    if len(bad_chars) > 0:
        return bad_chars
    else:
        return None

#
# def _wiki_index():
#     r = connect_redis()
#     cat_keys = r.lrange("wiki_cats", 0, 99)
#     cats = []
#     for cat_key in cat_keys :
#         cat = r.get(cat_key)
#         print(cat_key, cat)
#         cats.append(cat)
#     return cats


@wiki_app.route('/wiki/<slug>/')
@wiki_app.route('/wiki/<slug>')
def wiki(slug):

    categories = wiki_index()
    print("Wiki page: ", categories)

    user_info = check_auth_cookie(request)
    editable = False
    if user_info is not None:
        editable = True

    r = connect_redis()
    art_id = r.get('wiki_slug_' + slug)

    if art_id is None:
        site_message = "Missing article - %s" % slug
        html = "Please check the URL."
    else:
        md_src = r.get('wiki_article_' + art_id)
        art_title = r.get('wiki_article_title_' + art_id)
        art_slug = r.get('wiki_article_slug_' + art_id)
        md = markdown.Markdown(extensions=['wikilinks(base_url=/wiki/,html_class=myclass)'])
        #html = markdown.markdown(md_src, ['wikilinks(base_url=/wiki/)'])
        html = md.convert(md_src)
        site_message = None

    context = {
        'title': u"Wiki - Newcastle Makerspace",
        'menu': menu('sel_wiki', user_info, nav_style='wiki'),
        'main_content': html,
        'allow_edit': editable,
        'user_message': user_greeting(user_info),
        'site_message': site_message,
        'wiki_index': categories,
        'slug': slug
    }

    return template('templates/wiki', context)

@wiki_app.route('/wiki/edit/<slug>/')
@wiki_app.route('/wiki/edit/<slug>')
def wiki_edit_page(slug):

    categories = wiki_index()
    print("Wiki page: ", categories)

    user_info = check_auth_cookie(request)
    editable = False
    site_message = None
    if user_info is not None:
        editable = True
    else:
        site_message = u"Sorry, you do not have permission to edit this page."

    r = connect_redis()
    art_id = r.get('wiki_slug_' + slug)

    if art_id is None:
        html = "Missing article - %s" % slug
    else:
        md_src = r.get('wiki_article_' + art_id)
        art_title = r.get('wiki_article_title_' + art_id)
        art_slug = r.get('wiki_article_slug_' + art_id)
        md = markdown.Markdown(extensions=['wikilinks(base_url=/wiki/,html_class=myclass)'])
        #html = markdown.markdown(md_src, ['wikilinks(base_url=/wiki/)'])
        html = '<h4 class="page-title">Editing article: "%s" (%s)</h4>' % (art_title, art_slug)

    context = {
        'title': "Wiki - Newcastle Makerspace",
        'menu': menu('sel_wiki', user_info, nav_style='wiki'),
        'main_content': html,
        'editable': editable,
        'user_message': user_greeting(user_info),
        'wiki_index': categories,
        'site_message': site_message,
        'article_id': art_id,
        'article_title': art_title,
        'article_markdown': md_src
    }

    return template('templates/wiki_edit', context)

@wiki_app.route('/wiki/subcat/<subcat_id>/')
@wiki_app.route('/wiki/subcat/<subcat_id>')
def wiki_subcat(subcat_id, site_message=None):
    categories = wiki_index()
    user_info = check_auth_cookie(request)
    editable = False
    if user_info is not None:
        editable = True

    subcat_name = None
    maincat_name = None

    for c in categories:
        for sc in c[2]:
            if sc[0] == subcat_id:
                subcat_name = sc[1]
                maincat_name = c[1]

    print("looking for articles:")

    html = [u'<h3 class="page-title">Wiki > %s > %s</h3>' % (maincat_name, subcat_name)]
    html += u'<p>'
    r = connect_redis()
    articles = r.lrange('wiki_subcat_articles_' + subcat_id, 0, 999)
    html += u"%d articles<br/>" % len(articles)
    for art_id in articles:
        print(art_id)
        art_key = 'wiki_article_%s' % art_id
        art_body_markdown = r.get(art_key)

        art_slug_key = 'wiki_article_slug_%s' % art_id
        art_slug = r.get(art_slug_key)

        art_title_key = 'wiki_article_title_%s' % art_id
        art_title = r.get(art_title_key)

        html += u"Wiki article %s<br/>" % art_key
        #html += u"Title: [%s]" % art_title
        html += u'<a href="/wiki/%s">/wiki/%s</a><br/>' % (art_slug, art_title)
        #html += u" characters: [%d] <br/>" % len(art_body_markdown)
    html += u'</p>'
    html = u"".join(html)

    context = {
        'title': "Wiki - Newcastle Makerspace",
        'menu': menu('sel_wiki', user_info, nav_style='wiki'),
        'main_content': html,
        'editable': editable,
        'user_message': user_greeting(user_info),
        'wiki_index': categories,
        'site_message': site_message,
        'subcategory_id': subcat_id
    }

    return template('templates/wiki_subcat', context)


@wiki_app.post('/wiki/update_article')
def wiki_update_article():
    # form is defined in wiki_edit.tpl
    article_form = request.forms
    assert isinstance(article_form, FormsDict)
    article_name = article_form.article_title.strip()
    article_body = article_form.article_markdown.strip()
    article_id = article_form.article_id

    r = connect_redis()
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

    categories = wiki_index()
    user_info = check_auth_cookie(request)

    # form is defined in wiki_subcat.tpl
    article_form = request.forms
    assert isinstance(article_form, FormsDict)
    article_name = article_form.article_title.strip()
    article_slug = article_form.article_slug.strip()
    subcat_id = article_form.article_subcat_id

    if len(article_slug) == 0:
        return wiki_subcat(subcat_id, site_message="No article slug given.")

    if len(article_name) == 0:
        return wiki_subcat(subcat_id, site_message="No article name given.")

    bad_chars = _safe_wiki_article_slug(article_slug)
    bad_cat_message = None
    if bad_chars is not None:
        bad_slug_message = u"Sorry, these characters are not allowed in an article slug: %s" % u" ".join(bad_chars)
        return wiki_subcat(subcat_id, site_message=bad_slug_message)

    bad_chars = _safe_wiki_article_name(article_name)
    bad_name_message = None
    if bad_chars is not None:
        bad_cat_message = u"Sorry, these characters are not allowed in an article name: %s" % u" ".join(bad_chars)
        return wiki_subcat(subcat_id, site_message=bad_name_message)

    print("OK, we have a good article: %s %s" % (article_slug, article_name))

    default_text = """**%s** (New article)""" % article_name
    r = connect_redis()
    article_id = str(uuid.uuid4())
    art_key = 'wiki_article_%s' % article_id
    r.set(art_key, default_text)
    r.set('wiki_slug_%s' % article_slug, article_id)
    r.set('wiki_article_slug_%s' % article_id, article_slug)
    r.set('wiki_article_title_%s' % article_id, article_name)
    r.lpush("wiki_subcat_articles_%s" % subcat_id, article_id)

    # on error
    #return wiki_subcat(subcat_id, user_message=bad_cat_message)

    return wiki(article_slug)


@wiki_app.post('/wiki/add_category')
def add_wiki_category():

    user_info = check_auth_cookie(request)

    if user_info is None:
        abort(403, "Forbidden")
    if user_info[1] is False:  # superuser?
        abort(403, "Forbidden")

    # form is defined in admin.tpl
    cat_form = request.forms
    assert isinstance(cat_form, FormsDict)
    cat_name = cat_form.category_name
    cat_name = cat_name.strip()
    print(cat_name)
    bad_chars = _safe_wiki_category_name(cat_name)
    bad_cat_message = None
    if bad_chars is not None:
        bad_cat_message = u"Sorry, these characters are not allowed: %s" % u" ".join(bad_chars)
        print(bad_cat_message)

    if bad_cat_message is None:
        cat_key = "wiki_cat_%s" % str(uuid.uuid4())
        r = connect_redis()
        r.set(cat_key, cat_name)
        r.lpush("wiki_cats", cat_key)

    context = {
        'title': u"Admin - Newcastle Makerspace",
        'menu': menu('sel_admin', user_info, nav_style='default'),
        'user_message': user_greeting(user_info),
        'site_message': bad_cat_message,
        'wiki_categories': wiki_index()
    }

    return template('templates/admin', context)



@wiki_app.post('/wiki/add_subcategory')
def add_wiki_subcategory():

    user_info = check_auth_cookie(request)

    if user_info is None:
        abort(403, "Forbidden")
    if user_info[1] is False:  # superuser?
        abort(403, "Forbidden")

    # form is defined in admin.tpl
    sub_cat_form = request.forms
    assert isinstance(sub_cat_form, FormsDict)
    main_cat_id = sub_cat_form.main_category
    # todo Check that maincat exists
    sub_cat_name = sub_cat_form.subcategory_name
    sub_cat_name = sub_cat_name.strip()
    sub_cat_id = 'wiki_subcat_%s' % str(uuid.uuid4())
    print("new subcat: ", main_cat_id, sub_cat_id, sub_cat_name)
    bad_chars = _safe_wiki_category_name(sub_cat_name)
    bad_cat_message = None
    if bad_chars is not None:
        bad_cat_message = u"Sorry, these characters are not allowed: %s" % u" ".join(bad_chars)
        print(bad_cat_message)

    if bad_cat_message is None:
        subcats_key = "wiki_subcats_%s" % main_cat_id
        r = connect_redis()
        r.lpush(subcats_key, sub_cat_id)
        r.set(sub_cat_id, sub_cat_name)

    context = {
        'title': u"Admin - Newcastle Makerspace",
        'menu': menu('sel_admin', user_info, nav_style='default'),
        'user_message': user_greeting(user_info),
        'site_message': bad_cat_message,
        'wiki_categories': wiki_index(),
        'subcategory_id': sub_cat_id
    }

    return template('templates/admin', context)