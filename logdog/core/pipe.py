import logging
from tornado import gen

from logdog.core.config import Config
from .utils import simple_oid


logger = logging.getLogger(__name__)


class Pipe(object):
    def __init__(self, *pipe_elements, **kwargs):
        self.app = kwargs.pop('app')
        self.namespaces = kwargs.get('namespaces', (Config.namespace_default,))
        self._oid = simple_oid()
        self._pipe = [self._construct_pipe_element(name, conf, kwargs) for name, conf in pipe_elements]
        self._link_pipe_objects()

    def __str__(self):
        return 'PIPE:{}'.format(self._oid)

    def _construct_pipe_element(self, name, *confs):
        cls, defaults, ns = self.app.config.find_class(name=name)
        for conf in filter(bool, confs):
            defaults.update(conf)
        defaults['app'] = self.app
        defaults['pipe'] = self
        defaults['namespaces'] = (self.namespaces + (ns,)) if ns not in self.namespaces else self.namespaces
        if hasattr(cls, 'factory'):
            cls = cls.factory
        return cls(**defaults)

    @gen.coroutine
    def start(self):
        logger.debug('[%s] Starting %s', self, ' -> '.join(map(str, self._pipe)))
        yield [po.start() for po in reversed(self._pipe)
               if set(po.namespaces).intersection(self.app.active_namespaces)]

    @gen.coroutine
    def stop(self):
        yield [po.stop() for po in self._pipe]

    def _link_pipe_objects(self):
        obj_first = self._pipe[0] if self._pipe else None
        for obj_next in self._pipe[1:]:
            obj_first.set_output(obj_next)
            obj_next.set_input(obj_first)
            obj_first = obj_next

        for obj in self._pipe:
            obj.relink_methods()

    def set_input(self, data):
        logger.debug('[%s] Pipe initialized with %s.', self, data)
        if self._pipe:
            self._pipe[0].set_input(data)