import copy
from tornado.util import ObjectDict, import_object
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from logdog.default_config import config as logdog_default_config


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
                l.append((item[0], item[1:]))
            else:
                l.append((item, None))
        return l
    return [(conf, None)]


def is_importable(key):
    return key in ('cls',)


class Config(ObjectDict):
    namespace_delimiter = '::'
    namespace_default = '*'

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

    def find_conf(self, name, fallback=None):
        namespace = self.namespace_default
        if self.namespace_delimiter in name:
            namespace, tmp, name = name.partition(self.namespace_delimiter)

        _cache = self._conf_path_cache.get(name)
        if _cache is not None:
            return copy.deepcopy(_cache)

        try:
            target = self
            for part in name.split('.'):
                target = target[part]
        except KeyError:
            if fallback:
                return self.find_conf(name=fallback)
            else:
                raise

        if isinstance(target, (list, tuple)):
            target = handle_as_list(target)

        self._conf_path_cache[name] = target, name, namespace
        return copy.deepcopy(target), name, namespace

    def find_class(self, name, fallback=None):
        _cache = self._classes_cache.get(name)
        if _cache is not None:
            return _cache

        try:
            conf, name, namespace = self.find_conf(name, fallback=None)
            cls = conf.pop('cls')
        except KeyError:
            if fallback:
                return self.find_class(name=fallback)
            else:
                raise

        self._classes_cache[name] = cls, conf, namespace
        return cls, conf, namespace

    def find_and_construct_class(self, name, fallback=None, **kwargs):
        cls, defaults, ns = self.find_class(name=name, fallback=fallback)

        if isinstance(defaults, dict):
            defaults.update(kwargs)
            return cls(**defaults)

        elif isinstance(defaults, (list, tuple)):
            return cls(*defaults, **kwargs)

        return cls(**kwargs)


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
                    ret = import_object(ret)
                return ret
            return cfg

        default_config = walk(default_config)
        user_config = walk(user_config)

        conf = self._merge_configs(default_config, user_config)
        conf.sources = handle_as_list(conf.sources)

        return conf