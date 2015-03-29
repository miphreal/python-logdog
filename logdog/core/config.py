import copy
import logging
from tornado.util import ObjectDict, import_object
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from logdog.default_config import config as logdog_default_config


logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass

_unset = object()


def handle_as_list(conf):
    if isinstance(conf, dict):
        return conf.iteritems()
    if isinstance(conf, (list, tuple)):
        l = []
        for item in conf:
            if isinstance(item, basestring):
                l.append((item, None))
            elif isinstance(item, dict) and len(item) == 1:
                l.append(item.items()[0])
            elif isinstance(item, (list, tuple)) and item:
                l.append((item[0], item[1:] if len(item) > 2 else item[1]))
            else:
                l.append((item, None))
        return l
    return [(conf, None)]


def is_importable(key):
    return key in ('cls',)


class Config(ObjectDict):
    namespace_delimiter = ' '
    namespace_default = '*'
    subconfig_namespace_delimiter = '@'

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
        name = name.strip().lstrip(self.namespace_delimiter).rstrip(self.subconfig_namespace_delimiter)

        namespace = self.namespace_default
        if self.namespace_delimiter in name:
            namespace, tmp, name = name.partition(self.namespace_delimiter)

        extra_conf = None
        if self.subconfig_namespace_delimiter in name:
            name, tmp, extra_conf = name.rpartition(self.subconfig_namespace_delimiter)
            extra_conf_relative = '{}.{}{}'.format(name, self.subconfig_namespace_delimiter, extra_conf)
            extra_conf = self.walk_conf(extra_conf_relative, default=None)

        try:
            target = self.walk_conf(name)
        except KeyError:
            if fallback:
                return self.find_conf(name=fallback)
            else:
                raise

        if isinstance(target, (list, tuple)):
            target = handle_as_list(target)

        elif extra_conf and isinstance(target, dict) and isinstance(extra_conf, dict):
            target.update(extra_conf)

        return target, name, namespace.split(',')

    def find_class(self, name, fallback=None):
        initial_name = name
        _cache = self._classes_cache.get(initial_name)
        if _cache is not None:
            return copy.deepcopy(_cache)

        conf, name, namespaces = self.find_conf(name, fallback=None)
        if isinstance(conf, basestring):
            conf = {'cls': conf}
        elif isinstance(conf, (list, tuple)):
            conf = {'*': conf}

        try:
            cls = conf.pop('cls')
        except KeyError:
            if name != 'default':
                fallback = fallback if fallback else ''.join(name.rpartition('.')[:-1] + ('default',))
                cls, f_name, f_conf, f_ns = self.find_class(name=fallback)
                f_conf.update(conf)
                conf = f_conf
                namespaces = list(set(namespaces).union(f_ns))
            else:
                raise

        # sanitize conf
        for k in conf.keys():
            if k.startswith(self.subconfig_namespace_delimiter):
                conf.pop(k)

        if isinstance(cls, basestring):
            try:
                cls = import_object(cls)
            except ImportError:
                logger.warning('Could not import "%s".', cls)

        if 'namespaces' in conf:
            if tuple(namespaces) == (self.namespace_default,):
                namespaces = tuple(conf['namespaces'])
            else:
                namespaces = tuple(set(namespaces).union(conf['namespaces']))

        self._classes_cache[initial_name] = cls, name, conf, tuple(namespaces)
        return cls, name, copy.deepcopy(conf), tuple(namespaces)

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


class ConfigLoader(object):

    def __init__(self, path):
        self._path = path

    def _load_user_config(self):
        with open(self._path, 'r') as f:
            return load(f, Loader=Loader)

    def _merge_configs(self, config, updater):
        if isinstance(config, dict):
            if isinstance(updater, dict):
                missing_keys = set(updater).difference(config)
                existing_keys = set(updater).intersection(config)

                cfg = config.copy()
                for k in missing_keys:
                    cfg[k] = updater[k]

                for k in existing_keys:
                    cfg[k] = self._merge_configs(cfg[k], updater[k])

                return cfg

        return updater

    def load_config(self, default_only=False):
        user_config = self._load_user_config() if not default_only else Config()
        default_config = copy.deepcopy(logdog_default_config)

        def walk(cfg, key=None):
            if isinstance(cfg, dict):
                return Config((k, walk(v, key=k)) for k, v in cfg.iteritems())
            if isinstance(cfg, (tuple, list)):
                return map(walk, cfg)
            if isinstance(cfg, (str, unicode)):
                ret = cfg.format(default=default_config)
                if is_importable(key):
                    try:
                        ret = import_object(ret)
                    except ImportError:
                        pass
                return ret
            return cfg

        default_config = walk(default_config)
        user_config = walk(user_config)

        conf = self._merge_configs(default_config, user_config)
        conf.sources = handle_as_list(conf.sources)

        return conf