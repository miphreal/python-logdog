import anydbm
import json
import os
from logdog.core.path import Path


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
        path = Path('', 0, None)
        path.__setstate__(json.loads(self.get(name)))
        return path

    def set_path(self, path_obj):
        self.set(path_obj.name, json.dumps(path_obj.__getstate__()))