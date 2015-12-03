# coding=utf-8
from hamcrest import *
from mock import patch

from logdog.core.config.decl import Config, ConfigLookupPath


class TestConfigDeclaration(object):

    def test_copy(self):
        c = Config({'a': 1, 'b': {'c': 2}})
        c_copy = c.copy()
        assert_that(c_copy, not_(same_instance(c)))
        assert_that(c_copy.b, same_instance(c.b))

    def test_deepcopy(self):
        c = Config({'a': 1, 'b': {'c': 2}})
        c_deepcopy = c.deepcopy()
        assert_that(c_deepcopy, not_(same_instance(c)))
        assert_that(c_deepcopy.b, not_(same_instance(c.b)))

    def test_copy_and_update(self):
        c = Config({'a': 1, 'b': {'c': 2}})
        c_upd = c.copy_and_update({'x': 3}, y=4)
        assert_that(c_upd, not_(same_instance(c)))
        assert_that(c_upd.b, not_(same_instance(c.b)))
        assert_that(c_upd, has_entries({'x': 3, 'y': 4}))

    def test_copy_and_update__via_call(self):
        c = Config({'a': 1, 'b': {'c': 2}})
        c_upd = c({'x': 3}, y=4)
        assert_that(c_upd, not_(same_instance(c)))
        assert_that(c_upd.b, not_(same_instance(c.b)))
        assert_that(c_upd, has_entries({'x': 3, 'y': 4}))

    def test_walk_conf(self):
        c = Config({'a': 1, 'b': {'c': 2}})
        assert_that(c.walk_conf('a'), equal_to(1))
        assert_that(c.walk_conf('b.c'), equal_to(2))
        assert_that(c.walk_conf('b.c.d', default=3), equal_to(3))

    def test_walk_conf_returns_copy(self):
        c = Config({'a': 1, 'b': {'c': 2}})
        assert_that(c.walk_conf('b'), not_(same_instance(c.b)))

    def test_walk_conf_caches_lookups(self):
        # acceptable behaviour,
        # since config is normally used in read-only mode
        c = Config({'a': 1, 'b': {'c': {'d': 2}}})
        val = c.walk_conf('b.c.d')
        c['b']['c']['d'] = 3
        assert_that(c.walk_conf('b.c.d'), equal_to(val))

    def test_find_conf(self):
        c = Config({'x-conf': {'host': 'h', 'connection': {'type': 'unix'}}})

        ret = c.find_conf('x-conf.connection')
        assert_that(ret, all_of(
            has_length(2),
            contains(
                has_entries({'type': 'unix'}),
                instance_of(ConfigLookupPath))))

    def test_find_conf_with_variation(self):
        c = Config({'x-conf': {
            'connection': {
                'type': 'unix', 'log': '/tmp/conn.log',
                '@debug': {'type': 'http', 'debug': True}}}})

        ret = c.find_conf('x-conf.connection@debug')
        assert_that(ret, all_of(
            has_length(2),
            contains(
                has_entries({'log': '/tmp/conn.log',
                             'type': 'http',
                             'debug': True}),
                instance_of(ConfigLookupPath))))

    def test_find_conf_with_fallback(self):
        c = Config({'x-conf': {
            'default': {'type': 'udp', 'log': '/tmp/udp.log', 'debug': False},
            # let's say there's a typo -- 'conection' instead of 'connection'
            'conection': {'type': 'unix', 'log': '/tmp/conn.log'},
            '@debug': {'type': 'http', 'debug': True}}})

        ret = c.find_conf('x-conf.connection@debug',
                          fallback='x-conf.default')
        assert_that(ret, all_of(
            has_length(2),
            contains(
                has_entries({'log': '/tmp/udp.log',
                             'type': 'udp',
                             'debug': False}),
                instance_of(ConfigLookupPath))))

    def test_find_class__simple_definition(self):
        import logging

        c = Config({
            'path': {'nested': {'sys-logger': {'cls': 'logging.Logger'}}}
        })

        cls, conf, lookup = c.find_class('path.nested.sys-logger')

        assert_that(cls, same_instance(logging.Logger))
        assert_that(conf, has_entries({'cls': 'logging.Logger'}))
        assert_that(lookup.path, equal_to('path.nested.sys-logger'))

    def test_find_class__simple_definition_without_cls(self):
        import logging

        c = Config({
            'path': {'nested': {'sys-logger': 'logging.Logger'}}
        })

        cls, conf, lookup = c.find_class('path.nested.sys-logger')

        assert_that(cls, same_instance(logging.Logger))
        assert_that(conf, has_entries({'cls': 'logging.Logger'}))
        assert_that(lookup.path, equal_to('path.nested.sys-logger'))

    def test_find_class__with_fallback(self):
        import logging

        c = Config({
            'path': {'nested': {'sys-logger': 'xx.Logger',
                                'fallback': 'logging.Logger'}}
        })

        cls, conf, lookup = c.find_class('path.nested.sys-logger',
                                         fallback='path.nested.fallback')

        assert_that(cls, same_instance(logging.Logger))
        assert_that(conf, has_entries({'cls': 'logging.Logger'}))
        assert_that(lookup.path, equal_to('path.nested.fallback'))

    def test_find_class__try_default(self):
        import logging

        c = Config({
            'path': {'nested': {'sys-logger': 'xx.Logger',
                                'default': 'logging.Logger'}}
        })

        cls, conf, lookup = c.find_class('path.nested.sys-logger')

        assert_that(cls, same_instance(logging.Logger))
        assert_that(conf, has_entries({'cls': 'logging.Logger'}))
        assert_that(lookup.path, equal_to('path.nested.default'))

    def test_find_class__try_default_hierarchy(self):
        import logging

        c = Config({
            'path': {'nested': {'sys-logger': 'xx.Logger'}},
            'default': 'logging.Logger',
        })

        cls, conf, lookup = c.find_class('path.nested.sys-logger')

        assert_that(cls, same_instance(logging.Logger))
        assert_that(conf, has_entries({'cls': 'logging.Logger'}))
        assert_that(lookup.path, equal_to('default'))

    def test_find_and_construct_class__simple(self):
        c = Config({
            'path': {'nested': {'sys-conf': {
                'cls': 'logdog.core.config.Config'
            }}},
        })

        obj = c.find_and_construct_class('path.nested.sys-conf')

        assert_that(obj, instance_of(Config))

    def test_find_and_construct_class__params(self):
        c = Config({
            'path': {'nested': {'sys-conf': {
                'cls': 'collections.OrderedDict',
                'cls*': [{'a': 1}],
                'cls**': {'b': 2, 'c': 3}
            }}},
        })

        obj = c.find_and_construct_class('path.nested.sys-conf')
        assert_that(obj, has_entries({'a': 1, 'b': 2, 'c': 3}))

    def test_find_and_construct_class__params_and_meta(self):
        c = Config({
            'path': {'nested': {'sys-conf': {
                'cls': 'collections.OrderedDict',
                'cls*': [{'a': 1}],
                'cls**': {'b': 2, 'c': 3}
            }}},
        })

        obj = c.find_and_construct_class('path.nested.sys-conf')
        assert_that(obj, has_entries({
            'a': 1, 'b': 2, 'c': 3,
            'namespaces': contains('*'),
            'config_name': 'path.nested.sys-conf',
            'config_variation': None}))

        obj = c.find_and_construct_class('path.nested.sys-conf',
                                         pass_meta=False)
        assert_that(obj, not_(has_entries({
            'namespaces': contains('*'),
            'config_name': 'path.nested.sys-conf',
            'config_variation': None})))

    def test_find_and_construct_class__factory(self):
        c = Config({
            'path': {'nested': {'sys-conf': {
                'cls': 'collections.OrderedDict',
            }}},
        })

        class ClassWithFactory(object):
            @classmethod
            def factory(cls, *args, **kwargs):
                return 'obj'

        ret = (
            ClassWithFactory,
            {},
            ConfigLookupPath('path.nested.sys-conf'),
        )
        with patch.object(Config, 'find_class', return_value=ret):
            obj = c.find_and_construct_class('path.nested.sys-conf')

        assert_that(obj, equal_to('obj'))

    def test_find_and_construct_class__invalid_factory(self):
        c = Config({
            'path': {'nested': {'sys-conf': {
                'cls': 'collections.OrderedDict',
            }}},
        })

        class ClassWithoutFactory(object):
            factory = None

            def __init__(self, *args, **kwargs):
                pass

        ret = (
            ClassWithoutFactory,
            {},
            ConfigLookupPath('path.nested.sys-conf'),
        )
        with patch.object(Config, 'find_class', return_value=ret):
            obj = c.find_and_construct_class('path.nested.sys-conf')

        assert_that(obj, instance_of(ClassWithoutFactory))
