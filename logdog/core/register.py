from __future__ import absolute_import, unicode_literals

import anydbm
import json
import logging
import os
from logdog.core.path import Path


logger = logging.getLogger(__name__)


class Register(object):

    def __init__(self, index_file, reset=False):
        self._index_file = os.path.expandvars(os.path.expanduser(index_file))
        if not os.path.exists(os.path.dirname(self._index_file)):
            os.makedirs(os.path.dirname(self._index_file))
        self._reg = anydbm.open(self._index_file, 'c')
        if reset:
            self._reg.clear()

    def set(self, key, val):
        self._reg[str(key)] = str(val)

    def get(self, key):
        return self._reg[key]

    def __getitem__(self, item):
        return self._reg[item]

    def get_path(self, name):
        path = Path(name, 0, None)
        try:
            path.__setstate__(json.loads(self.get(name)))
        except ValueError as e:
            logger.warning('[REGISTER] Cannot load stats for %s. Reason: "%s"', name, e)
        return path

    def set_path(self, path_obj):
        logger.debug('[REGISTER] Save state for path: %s', path_obj)
        self.set(path_obj.name, json.dumps(path_obj.__getstate__()))
        self._reg.sync()
