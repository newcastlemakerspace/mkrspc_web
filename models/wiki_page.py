PG_STATUS_LIVE, PG_STATUS_DRAFT, PG_STATUS_DELETED = 'PG_STATUS_LIVE', 'PG_STATUS_DRAFT', 'PG_STATUS_DELETED'

class WikiPage(object):

    def __init__(self, title='', body='', slug=''):

        self.title = title
        self.body = body
        self.slug = slug

    def load(self, redis_conn, article_id):

        r = redis_conn

        art_key = 'wiki_article_%s' % article_id
        art_title_key = 'wiki_article_title_%s' % article_id
        art_slug_key = 'wiki_article_slug_%s' % article_id

        self.body = r.get(art_key)
        self.title = r.get(art_title_key)
        self.slug = r.get(art_slug_key)







