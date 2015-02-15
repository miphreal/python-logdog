import copy
from tornado.util import ObjectDict
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from logdog.default_config import config as logdog_default_config


class Config(ObjectDict):
    pass


class ConfigLoader(object):

    def __init__(self, path):
        self._path = path

    def _load_user_config(self):
        with open(self._path, 'r') as f:
            return load(f, Loader=Loader)

    def load_config(self, default_only=False):
        user_config = self._load_user_config() if not default_only else Config()
        default_config = copy.deepcopy(logdog_default_config)

        def walk(cfg):
            if isinstance(cfg, dict):
                return Config((k, walk(v)) for k, v in cfg.iteritems())
            if isinstance(cfg, (tuple, list)):
                return map(walk, cfg)

            if isinstance(cfg, (str, unicode)):
                return cfg.format(default=default_config)
            return cfg

        default_config = walk(default_config)
        user_config = walk(user_config)

        if 'watcher' in user_config:
            default_config.watcher.update(user_config.watcher)
        if 'forwarder' in user_config:
            default_config.forwarder.update(user_config.forwarder)
        if 'webui' in user_config:
            default_config.webui.update(user_config.webui)

        return default_config