from __future__ import absolute_import, unicode_literals

import copy
import logging
import re

from tornado.util import ObjectDict
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from logdog.compat import import_object, string_types
from .exceptions import ConfigError


logger = logging.getLogger(__name__)
_unset = object()
DEFAULT_NAMESPACE = '*'
VARIATION_STARTS_WITH = '@'


class ConfigLookupPath(object):
    _path_format_re = re.compile(r'^((?P<namespaces>[\w-]+(,[\w-]+)*)\s+)?'
                                 r'(?P<path>[\w-]+(\.[\w-]+)*)'
                                 r'(?P<variation>{}[\w-]+)?$'
                                 .format(VARIATION_STARTS_WITH))

    def __init__(self, path):
        path = path or ''
        self.origin_path = path
        _match = self._path_format_re.match(path)
        if _match:
            kw = _match.groupdict()
            self.namespaces = (kw.get('namespaces') or
                               DEFAULT_NAMESPACE).split(',')
            self.path = kw.get('path') or ''
            self.variation = kw.get('variation') or None
        else:
            logger.warning(
                '[CONFIG-PATH] Could not parse passed path "%s".', path)
            self.namespaces = (DEFAULT_NAMESPACE,)
            self.path = path
            self.variation = None

    @property
    def variation_path(self):
        if self.variation and self.path:
            return '{}.{}'.format(self.path, self.variation)
        return None


class Config(ObjectDict):
    namespace_default = DEFAULT_NAMESPACE

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self._classes_cache = {}
        self._conf_path_cache = {}

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)

    def copy_and_update(self, *args, **config):
        conf = self.deepcopy()
        for a in args:
            if isinstance(a, dict):
                conf.update(a)
        conf.update(config)
        return conf

    __call__ = copy_and_update

    def walk_conf(self, path, default=_unset):
        _cache = self._conf_path_cache.get(path)
        if _cache is not None:
            return copy.deepcopy(_cache)

        target = self
        for part in path.split('.'):
            try:
                target = target[part]
            except (KeyError, IndexError, TypeError):
                if default is not _unset:
                    return default
                raise

        self._conf_path_cache[path] = target
        return copy.deepcopy(target)

    def find_conf(self, name, fallback=None):
        lookup_path = ConfigLookupPath(name)

        extra_conf = None
        variation_path = lookup_path.variation_path
        if variation_path:
            extra_conf = self.walk_conf(variation_path, default=None)

        try:
            target = self.walk_conf(lookup_path.path)
        except KeyError:
            if fallback:
                logger.warning('[CONFIG] Have not found "%s". '
                               'Trying to use fallback "%s"...',
                               lookup_path.path, fallback)
                return self.find_conf(name=fallback)
            else:
                logger.warning('[CONFIG] Could not find "%s".',
                               lookup_path.path)
                raise

        if extra_conf and \
                isinstance(target, dict) and isinstance(extra_conf, dict):
            target.update(extra_conf)

        return target, lookup_path

    def find_class(self, name, fallback=None):
        """
        Config can contain class definitions which can be constructed.

        Examples:
            # without init params
            {'cls': 'importable.path.to.Class'}
            or just a string, e.g.
            {'conf1': {'conf2': 'importable.path.to.Class'}...
            which is requested by `find_class('conf1.conf2')`

            # with position args
            {'cls': 'importable.path.to.Class',
             '*': ['arg1', 'arg2', 'argN']}

            # with keyword args
            {'cls': 'importable.path.to.Class',
             '**': {'kw1': 1, 'kw2': 2}}

            # or any combination
            {'cls': 'importable.path.to.Class',
             '*': ['arg1', 'arg2', 'argN'],
             '**': {'kw1': 1, 'kw2': 2}}
        """
        initial_name = name
        _cache = self._classes_cache.get(initial_name)
        if _cache is not None:
            return copy.deepcopy(_cache)

        conf, lookup_path = self.find_conf(name, fallback=fallback)

        if isinstance(conf, string_types):
            conf = {'cls': conf}

        try:
            cls = conf['cls']
            if isinstance(cls, string_types):
                cls = import_object(cls)
        except (KeyError, ImportError) as e:
            logger.warning('[CONFIG] Inappropriate config for '
                           'extracting class "%s". Faced an error: "%s".',
                           conf, e)

            if fallback:
                # use passed `fallback` path
                return self.find_class(name=fallback)
            else:
                # lookup for default configuration `down-to-up`
                parent_path = lookup_path.path
                while parent_path:
                    parent_path = parent_path.rpartition('.')[0]
                    default_path = 'default'
                    if parent_path:
                        default_path = '.'.join((parent_path, default_path))

                    try:
                        return self.find_class(name=default_path)
                    except KeyError as e:
                        logger.warning(
                            '[CONFIG] Tried extracting path "%s". '
                            'Faced an error: "%s".', default_path, e)

            raise

        self._classes_cache[initial_name] = cls, conf, lookup_path
        return cls, copy.deepcopy(conf), lookup_path

    def find_and_construct_class(self, name, fallback=None,
                                 args=None, kwargs=None, pass_meta=True):
        found_cls, conf, path = self.find_class(name=name, fallback=fallback)

        args = args or conf.pop('*', None) or ()
        kw = kwargs or conf.pop('**', None) or {}

        if pass_meta:
            namespaces = set(kw.pop('namespaces', ())).union(path.namespaces)
            if len(namespaces) > 1 and DEFAULT_NAMESPACE in namespaces:
                namespaces.remove(DEFAULT_NAMESPACE)

            kw['namespaces'] = tuple(namespaces)
            kw['config_name'] = path.path
            kw['config_variation'] = path.variation

        constructor = found_cls
        if hasattr(constructor, 'factory'):
            constructor = found_cls.factory

        if callable(constructor):
            return constructor(*args, **kw)

        elif callable(found_cls):
            return found_cls(*args, **kw)

        raise ConfigError('{} is not a class. Cannot be imported or called.'
                          .format(found_cls))
