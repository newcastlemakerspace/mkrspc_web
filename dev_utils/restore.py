import base64
import redis

states = (
    'expect_begin',
    'expect_record_count',
    'expect_delimiter',
    'expect_key_length',
    'expect_key',
    'expect_type_length',
    'expect_type',
    'expect_string_value_length',
    'expect_string_value',
    'expect_list_length',
    'expect_list_value_length',
    'expect_list_value',
)


class StringRecord(object):

    def __init__(self, key, value):
        self.key = key
        self.value = value
        assert isinstance(self.key, basestring)
        assert isinstance(self.value, basestring)

    def write(self, redis_conn):
        assert isinstance(self.key, basestring)
        assert isinstance(self.value, basestring)
        redis_conn.set(self.key, self.value)


class ListRecord(object):

    def __init__(self, key):
        self.key = key
        self.values = []
        assert isinstance(self.key, basestring)

    def add_list_value(self, value):
        assert isinstance(value, basestring)
        self.values.append(value)

    def write(self, redis_conn):
        assert isinstance(self.key, basestring)
        for list_val in self.values:
            redis_conn.rpush(self.key, list_val)


class WebBackupRestore(object):

    def __init__(self, input_file):
        self.input_file = input_file
        self.string_records = []
        self.list_records = []
        self.list_records_by_key = {}
        self.keys = set()

    def write_records(self, db_number):
        print "Restore to DB #%d" % db_number
        r = redis.Redis(db=db_number)
        assert isinstance(r, redis.Redis)
        if r.dbsize() != 0:
            print "ABORTED! DB #%d is not empty." % db_number
        assert r.dbsize() == 0

        for sr in self.string_records:
            sr.write(r)

        for lr in self.list_records:
            lr.write(r)

        redis_key_count = r.dbsize()

        print "Redis DB key count = %d" % redis_key_count
        print "Backup key count = %d" % len(self.keys)

        assert redis_key_count == len(self.keys)
        print "Restore complete for DB #%d" % db_number

    def add_string_record(self, key, value):
        r = StringRecord(key, value)
        assert key not in self.keys
        self.keys.add(key)
        self.string_records.append(r)

    def add_list_record(self, key):
        r = ListRecord(key)
        assert key not in self.keys
        self.keys.add(key)
        self.list_records.append(r)
        self.list_records_by_key[key] = r

    def add_list_entry(self, key, value):
        assert key in self.list_records_by_key
        r = self.list_records_by_key[key]
        assert isinstance(r, ListRecord)
        r.add_list_value(value)

    def show_stats(self):
        print "-------------------------------"
        print "Keys      : %d" % len(self.keys)
        print "Strings   : %d" % len(self.string_records)
        print "Lists     : %d" % len(self.list_records)
        print "-------------------------------"

    def load(self):

        f = open(self.input_file, 'rt')

        state = 'expect_begin'
        line_num = 0
        record_count = 0
        records_loaded = 0
        key_length = 0
        key = None
        value_type_length = 0
        string_value_length = 0
        list_length = 0
        list_value_length = 0
        list_values_loaded = 0

        for line in f:

            # lose the CR/LF
            line = line.strip()

            #print '.....................................................................'
            #print line_num
            #print line
            #print state
            assert state in states

            if state == 'expect_begin':
                assert line == '====BEGIN===='
                print "begin restore operation", record_count
                state = 'expect_record_count'

            elif state == 'expect_record_count':
                record_count = int(line)
                print "record count is", record_count
                state = 'expect_delimiter'

            elif state == 'expect_delimiter':
                if record_count == records_loaded:
                    assert line == '====END===='
                else:
                    assert line == '--------------------------------'

                # Reset record details.
                key_length = 0
                key = None
                value_type_length = 0
                string_value_length = 0
                list_length = 0
                list_value_length = 0
                list_values_loaded = 0

                state = 'expect_key_length'

            elif state == 'expect_key_length':
                key_length = int(line)
                #print "key length is", key_length
                state = 'expect_key'

            elif state == 'expect_key':
                key = line
                #print "key is", key
                assert len(key) == key_length
                state = 'expect_type_length'

            elif state == 'expect_type_length':
                value_type_length = int(line)
                #print "type length is", value_type_length
                state = 'expect_type'

            elif state == 'expect_type':
                value_type = line
                #print 'type is %s' % value_type
                assert len(value_type) == value_type_length
                if value_type == 'string':
                    state = 'expect_string_value_length'
                elif value_type == 'list':
                    state = 'expect_list_length'

            elif state == 'expect_string_value_length':
                string_value_length = int(line)
                #print "string value length is", string_value_length
                state = 'expect_string_value'

            elif state == 'expect_string_value':
                assert len(line) == string_value_length
                string_value = base64.b64decode(line)
                #print "string value is", string_value
                #print "Key  : %s" % key
                #print "Value: %s" % string_value[:73]
                self.add_string_record(key, string_value)
                records_loaded += 1
                state = 'expect_delimiter'

            elif state == 'expect_list_length':
                list_length = int(line)
                print "list length is", list_length
                self.add_list_record(key)
                state = 'expect_list_value_length'

            elif state == 'expect_list_value_length':
                list_value_length = int(line)
                #print "list value length is", list_value_length
                state = 'expect_list_value'

            elif state == 'expect_list_value':
                list_value_b64 = line
                assert len(list_value_b64) == list_value_length
                list_value = base64.b64decode(line)
                print " - list value is", list_value
                self.add_list_entry(key, list_value)
                list_values_loaded += 1
                if list_length == list_values_loaded:
                    records_loaded += 1
                    state = 'expect_delimiter'
                else:
                    state = 'expect_list_value_length'

            else:
                raise Exception('Unhandled state: %s' % state)

            line_num += 1


if __name__ == '__main__':

    db = 3
    #input_file = '/dkpw_1TB/development/felix/makerspace/mkrspc_web/static/backups/mkrspc_web_backup_2014-10-23T14:23:49.354552.txt'
    #input_file = '/dkpw_1TB/development/felix/makerspace/mkrspc_web/static/backups/mkrspc_web_backup_2014-10-23T21-34-01.495315 (1).txt'
    input_file = '/dkpw_1TB/development/felix/makerspace/mkrspc_web/dev_utils/mkrspc_web_backup_2014-11-13T09 20 26.824244.txt'
    restorer = WebBackupRestore(input_file)
    restorer.load()
    restorer.show_stats()
    restorer.write_records(db)



