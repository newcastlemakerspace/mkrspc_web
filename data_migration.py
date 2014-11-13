import redis
import datetime
from site_config import REDIS_DB
import site_utils
import uuid


def _was_migration_applied(redis_conn, seq):

    value = redis_conn.get('migration_%d' % seq)
    if value is not None:
        print "migration_%d - exists" % seq
        return True

    print "migration_%d - executing" % seq
    return False


def _flag_migration_applied(redis_conn, seq):
    print "migration_%d - done" % seq
    #      migration_201410241041
    d = datetime.datetime
    redis_conn.set('migration_%d' % seq, d.now().isoformat())


def migration_201410241041(redis_conn):

    seq = 201410241041
    if _was_migration_applied(redis_conn, seq):
        return

    print " - clear old auth cookies"
    key_prefix_search = 'User_Auth_Cookie_*'
    keys = redis_conn.keys(key_prefix_search)
    for k in keys:
        redis_conn.delete(k)

    _flag_migration_applied(redis_conn, seq)


def migration_201411130948(redis_conn):

    # wiki categories
    seq = 201411130948
    if _was_migration_applied(redis_conn, seq):
        return

    print " - re-init wiki"
    su = site_utils.SiteUtils(redis_conn)
    su.wu.create_wiki_root_category()
    root_cat_id = su.wu.wiki_root_category()
    misc_cat_id = su.wu.create_wiki_category(root_cat_id, "Misc.")

    article_keys = redis_conn.keys('wiki_article_*')
    for k in article_keys:
        print k, len(k)
        print k[13:]
        if len(k) == 49:
            uuid_sstr = k[13:]
            art_id = uuid.UUID(uuid_sstr)
            assert isinstance(art_id, uuid.UUID)
            print " article: ", misc_cat_id, art_id
            cat_articles_key = "wiki_category_articles_%s" % misc_cat_id
            r.rpush(cat_articles_key, str(art_id))
        else:
            print " (not an article)"
        print '-----------------------------'



    _flag_migration_applied(redis_conn, seq)


if __name__ == '__main__':

    print "Ruinning migrations for DB #%d" % REDIS_DB
    r = redis.Redis(db=REDIS_DB)
    assert isinstance(r, redis.Redis)

    migration_201410241041(r)
    migration_201411130948(r)






