# coding=utf-8
from __future__ import unicode_literals
from hamcrest import *

from logdog.core.msg import Msg


class TestMsg(object):

    def test_init(self):
        m = Msg(message='log entry', source='/tmp/x')
        assert_that(m.message, equal_to('log entry'))

    def test_init_unicode(self):
        m = Msg(message='сообщение лога', source='/tmp/x')
        assert_that(m.message, equal_to('сообщение лога'))

    def test_update_message(self):
        m = Msg(message='log entry', source='/tmp/x')
        m.update_message('new msg')
        assert_that(m.message, equal_to('new msg'))

    def test_updated_meta(self):
        m = Msg(message='log entry', source='/tmp/x')
        m.update_meta({'tags': ('syslog', 'auth')})
        assert_that(m.meta, has_entry('tags', contains('syslog', 'auth')))

    def test_serialize(self):
        m = Msg(message='log entry', source='/tmp/x', meta={'tags': ['syslog']})
        assert_that(m.serialize(), all_of(
            instance_of(dict),
            has_entries({
                'msg': 'log entry',
                'src': '/tmp/x',
                'meta': {'tags': ['syslog']},
                '_v': 1,
            })
        ))

    def test_deserialize(self):
        m = Msg.deserialize({
            'msg': 'log entry',
            'src': '/tmp/x',
            'meta': {'tags': ['syslog']},
            '_v': 1,
        })
        assert_that(m, has_properties(
            message='log entry',
            source='/tmp/x',
            meta={'tags': ['syslog']},
            version=1
        ))

    def test_serialize_json(self):
        m = Msg(message='log entry', source='/tmp/x', meta={'tags': ['syslog']})
        assert_that(m.serialize_json(), contains_string('log entry'))
        m = Msg(message='сообщение', source='/tmp/x', meta={'tags': ['syslog']})
        m.serialize_json()

    def test_deserialize_json(self):
        assert_that(Msg.deserialize_json('{"msg": "log entry"}'),
                    has_property('message', equal_to('log entry')))
        assert_that(Msg.deserialize_json('{"msg": "log entry","src":"/tmp/x","meta":null,"_v":1}'),
                    has_properties(
                        message=equal_to('log entry'), source=equal_to('/tmp/x'),
                        meta=None, version=1))
        assert_that(Msg.deserialize_json('{"msg":"сообщение","src":"/tmp/файл","meta":null,"_v":1}'),
                    has_properties(
                        message=equal_to('сообщение'), source=equal_to('/tmp/файл'),
                        meta=None, version=1))

    def test_serialize_jsonb(self):
        m = Msg(message='log entry', source='/tmp/x', meta={'tags': ['syslog']})
        m.serialize_jsonb()
        m = Msg(message='сообщение', source='/tmp/файл', meta={'tags': ['syslog']})
        m.serialize_jsonb()

    def test_deserialize_jsonb(self):
        m0 = Msg(message='log entry', source='/tmp/x', meta={'tags': ['syslog']})
        serialized_message = m0.serialize_jsonb()
        m1 = Msg.deserialize_jsonb(serialized_message)

        assert_that(m1, has_properties(
            message=equal_to(m0.message),
            source=equal_to(m0.source),
            meta=equal_to(m0.meta),
            version=equal_to(m0.version)
        ))