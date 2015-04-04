from logdog.core.utils.six import *


__all__ = ['import_object', 'text_type']


# tornado import_object
from tornado.util import import_object as _import_object
if PY2:
    import_object = lambda name: _import_object(str(name))
if PY3:
    import_object = _import_object
