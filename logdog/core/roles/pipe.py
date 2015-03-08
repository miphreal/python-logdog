import logging
from tornado import gen

from .base import BaseRole


logger = logging.getLogger(__name__)


class Pipe(BaseRole):

    def __init__(self, *args, **kwargs):
        super(Pipe, self).__init__(*args, **kwargs)

        self._pipe = [self._construct_pipe_element(name, conf, kwargs) for name, conf in self.items]
        self._link_pipe_objects()
        self._active_pipe = [po for po in self._pipe
                             if set(po.namespaces).intersection(self.app.active_namespaces)]
        if self._active_pipe:
            self._active_pipe[-1].set_output(None)

    def __str__(self):
        return 'PIPE:{}'.format(self._oid)

    def _construct_pipe_element(self, name, *confs):
        conf = {}
        for c in filter(bool, confs):
            conf.update(c)
        conf['app'] = self.app
        conf['parent'] = self

        return self.app.config.find_and_construct_class(name=name, **conf)

    def _is_valid_pipe(self):
        in_ = self._active_pipe[0] if self._active_pipe else None
        for p in self._active_pipe[1:]:
            if in_.output is not p:
                logger.warning('[%s] Lost connectivity in the pipe. Check the configuration. %s -x-> %s', self, in_, p)
                return False
            in_ = p
        return True

    @gen.coroutine
    def start(self):
        if self._is_valid_pipe():
            logger.debug('[%s] Starting %s', self, ' -> '.join(map(str, self._active_pipe)))
            yield [po.start() for po in reversed(self._active_pipe)]

    @gen.coroutine
    def stop(self):
        yield [po.stop() for po in self._active_pipe]

    def _link_pipe_objects(self):
        obj_first = self._pipe[0] if self._pipe else None
        for obj_next in self._pipe[1:]:
            obj_first.set_output(obj_next)
            obj_next.set_input(obj_first)
            obj_first = obj_next

        for obj in reversed(self._pipe):
            obj.link_methods()

    def set_input(self, data):
        logger.debug('[%s] Pipe initialized with %s.', self, data)
        if self._active_pipe:
            self._active_pipe[0].set_input(data)