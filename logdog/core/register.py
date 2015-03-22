import anydbm
import pickle
import os


class Register(object):

    def __init__(self, index_file):
        self._index_file = os.path.expandvars(os.path.expanduser(index_file))
        if not os.path.exists(os.path.dirname(self._index_file)):
            os.makedirs(os.path.dirname(self._index_file))
        self._reg = anydbm.open(self._index_file, 'c')

    def set(self, key, val):
        self._reg[key] = val

    def get(self, key):
        return self._reg[key]

    def __getitem__(self, item):
        return self._reg[item]

    def get_path(self, name):
        return pickle.loads(self.get(name))

    def set_path(self, path_obj):
        self.set(path_obj.name, pickle.dumps(path_obj))