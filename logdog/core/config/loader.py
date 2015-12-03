from __future__ import absolute_import, unicode_literals

import copy
import logging
import os

from tornado.util import ObjectDict
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from logdog.default_config import config as logdog_default_config
from logdog.compat import text_type, import_object
from .decl import Config
from .exceptions import ConfigError
from .utils import handle_as_list, is_importable


logger = logging.getLogger(__name__)


class ConfigLoader(object):

    def __init__(self, path):
        self._path = path

    def _load_user_config(self):
        if not os.path.exists(self._path):
            raise ConfigError(
                '[{}] Config file does not exist.'.format(self._path))
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
        user_config = self._load_user_config() if not default_only else {}
        default_config = copy.deepcopy(logdog_default_config)

        if not isinstance(user_config, dict):
            raise ConfigError(
                '[{}] Invalid config file: must have '
                '\"key: value\" format.'.format(self._path))

        def walk(cfg, key=None):
            if isinstance(cfg, dict):
                return ObjectDict((k, walk(v, key=k)) for k, v in cfg.items())
            if isinstance(cfg, (tuple, list)):
                return map(walk, cfg)
            if isinstance(cfg, (str, text_type)):
                ret = cfg.format(default=default_config)
                if is_importable(key):
                    try:
                        ret = import_object(ret)
                    except ImportError:
                        logger.debug(
                            '[%s] Faced non-importable path: '
                            '\"%s: %s\".', self._path, key, ret)
                return ret
            return cfg

        default_config = walk(default_config)
        user_config = walk(user_config)

        conf = self._merge_configs(default_config, user_config)
        conf['sources'] = handle_as_list(conf['sources'])

        return Config(conf)
