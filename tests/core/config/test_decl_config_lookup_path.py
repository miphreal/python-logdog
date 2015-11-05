# coding=utf-8
from hamcrest import *

from logdog.core.config.decl import ConfigLookupPath


class TestConfigLookupPath(object):

    def test_path_parsing_simple_name(self):
        assert_that(
            ConfigLookupPath('path'),
            has_properties({
                'origin_path': 'path',
                'path': 'path',
                'namespaces': contains('*'),
                'variation': None,
                'variation_path': None}))

    def test_path_parsing_with_namespace(self):
        assert_that(
            ConfigLookupPath('ns path'),
            has_properties({
                'origin_path': 'ns path',
                'path': 'path',
                'namespaces': contains('ns'),
                'variation': None,
                'variation_path': None}))

    def test_path_parsing_with_namespaces(self):
        assert_that(
            ConfigLookupPath('ns1,ns2 path'),
            has_properties({
                'origin_path': 'ns1,ns2 path',
                'path': 'path',
                'namespaces': contains('ns1', 'ns2'),
                'variation': None,
                'variation_path': None}))

    def test_path_parsing_with_variation(self):
        assert_that(
            ConfigLookupPath('ns1,ns2 path.obj@variation'),
            has_properties({
                'origin_path': 'ns1,ns2 path.obj@variation',
                'path': 'path.obj',
                'namespaces': contains('ns1', 'ns2'),
                'variation': '@variation',
                'variation_path': 'path.obj.@variation'}))

    def test_path_parsing_with_variation__simple(self):
        assert_that(
            ConfigLookupPath('path.obj@variation'),
            has_properties({
                'origin_path': 'path.obj@variation',
                'path': 'path.obj',
                'namespaces': contains('*'),
                'variation': '@variation',
                'variation_path': 'path.obj.@variation'}))

    def test_path_parsing_names_with_dashes_and_underscores_and_dots(self):
        assert_that(
            ConfigLookupPath(
                'ns-1,ns_2 path.sub-path.sub_path@variation-x_y'
            ),
            has_properties({
                'origin_path':
                    'ns-1,ns_2 path.sub-path.sub_path@variation-x_y',
                'path': 'path.sub-path.sub_path',
                'namespaces': contains('ns-1', 'ns_2'),
                'variation': '@variation-x_y',
                'variation_path': 'path.sub-path.sub_path.@variation-x_y'}))

    def test_incorrect_name(self):
        assert_that(
            ConfigLookupPath('ns.1 path:sub@variation,x'),
            has_properties({  # nothing parsed
                'origin_path': 'ns.1 path:sub@variation,x',
                'path': 'ns.1 path:sub@variation,x',
                'namespaces': contains('*'),
                'variation': None,
                'variation_path': None}))
