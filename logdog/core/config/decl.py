from __future__ import absolute_import, unicode_literals

import copy
import logging
import re

from tornado.util import ObjectDict
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from logdog.compat import import_object
from .exceptions import ConfigError
from .utils import handle_as_list


logger = logging.getLogger(__name__)
_unset = object()
DEFAULT_NAMESPACE = '*'
VARIATION_STARTS_WITH = '@'


class ConfigLookupPath(object):
    path_format_re = re.compile(r'(?P<namespaces>[\w-]+(,[\w-])*)?'
                                r'\s(?P<path>[\w-]+(\.[\w-]+)*)'
                                r'(?P<variation>{}[\w-]+)?'.format(VARIATION_STARTS_WITH))

    def __init__(self, path):
        path = path or ''
        self.origin_path = path
        _match = self.path_format_re.match(path)
        if _match:
            kw = _match.groupdict()
            self.namespaces = kw.get('namespaces') or (DEFAULT_NAMESPACE,)
            self.path = kw.get('path') or ''
            self.variation = kw.get('variation') or None
        else:
            self.namespaces = (DEFAULT_NAMESPACE,)
            self.path = path
            self.variation = None

    @property
    def variation_path(self):
        if self.variation and self.path:
            return '{}.@{}'.format(self.path, self.variation)
        return None


class Config(ObjectDict):
    namespace_default = DEFAULT_NAMESPACE
    _classes_cache = {}
    _conf_path_cache = {}

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
            except (KeyError, IndexError):
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
                return self.find_conf(name=fallback)
            else:
                raise

        if isinstance(target, (list, tuple)):
            target = handle_as_list(target)

        elif extra_conf and isinstance(target, dict) and isinstance(extra_conf, dict):
            target.update(extra_conf)

        return target, lookup_path

    def find_class(self, name, fallback=None):
        initial_name = name
        _cache = self._classes_cache.get(initial_name)
        if _cache is not None:
            return copy.deepcopy(_cache)

        conf, lookup_path = self.find_conf(name, fallback=None)
        namespaces = lookup_path.namespaces

        if isinstance(conf, basestring):
            conf = {'cls': conf}
        elif isinstance(conf, (list, tuple)):
            conf = {'*': conf}

        try:
            cls = conf.pop('cls')
        except KeyError:
            if lookup_path.path != 'default':
                fallback = fallback if fallback else ''.join(lookup_path.path.rpartition('.')[:-1] + ('default',))
                cls, f_name, f_conf, f_ns = self.find_class(name=fallback)
                f_conf.update(conf)
                conf = f_conf
                namespaces = list(set(lookup_path.namespaces).union(f_ns))
            else:
                raise

        # sanitize conf
        for k in conf.keys():
            if k.startswith(VARIATION_STARTS_WITH):
                conf.pop(k)

        if isinstance(cls, basestring):
            try:
                cls = import_object(cls)
            except ImportError:
                logger.warning('Could not import "%s".', cls)

        if 'namespaces' in conf:
            conf_ns = conf.pop('namespaces')
            if tuple(lookup_path.namespaces) == (DEFAULT_NAMESPACE,):
                namespaces = conf_ns
            else:
                namespaces = set(lookup_path.namespaces).union(conf_ns)

        namespaces = set(namespaces)
        if len(namespaces) > 1 and DEFAULT_NAMESPACE in namespaces:
            namespaces.remove(DEFAULT_NAMESPACE)

        self._classes_cache[initial_name] = cls, lookup_path.path, conf, tuple(namespaces)
        return cls, lookup_path.path, copy.deepcopy(conf), tuple(namespaces)

    def find_and_construct_class(self, name, fallback=None, args=(), kwargs=None):
        found_cls, name, defaults, ns = self.find_class(name=name, fallback=fallback)

        if kwargs:
            defaults.update(kwargs)

        kw = defaults
        kw.update(kw.pop('**', {}))
        kw['namespaces'] = set(kw.get('namespaces', ())).union(ns)
        kw['config_name'] = name

        args = kw.pop('*', args)

        if hasattr(found_cls, 'factory'):
            found_cls = found_cls.factory

        args = handle_as_list(args)

        if callable(found_cls):
            return found_cls(*args, **kw)
        raise ConfigError('{} is not a class. Cannot be imported or called.'.format(found_cls))
