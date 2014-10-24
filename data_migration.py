import redis
import datetime
from site_config import REDIS_DB


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


if __name__ == '__main__':

    print "Ruinning migrations for DB #%d" % REDIS_DB
    r = redis.Redis(db=REDIS_DB)
    assert isinstance(r, redis.Redis)

    migration_201410241041(r)






