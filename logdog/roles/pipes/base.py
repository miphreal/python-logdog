import logging
from tornado import gen

from logdog.core.base_role import BaseRole


logger = logging.getLogger(__name__)


class BasePipe(BaseRole):
    defaults = BaseRole.defaults.copy_and_update(
        unique=True
    )

    def __init__(self, *args, **kwargs):
        super(BasePipe, self).__init__(*args, **kwargs)
        self.items = [self.construct_subrole(name, conf) for name, conf in self.items]
        self._link_pipe_objects()
        if self.items:
            self.items[-1].set_output(None)

    def __str__(self):
        return 'PIPE:{}'.format(self._oid)

    def _is_valid_pipe(self):
        active_pipe = self.active_items
        in_ = active_pipe[0] if active_pipe else None
        for p in active_pipe[1:]:
            if in_.output is not p:
                logger.warning('[%s] Lost connectivity in the pipe. Check the configuration. %s -x-> %s', self, in_, p)
                return False
            in_ = p
        return True

    @gen.coroutine
    def start(self):
        if not self.started and self._is_valid_pipe():
            logger.debug('[%s] Starting %s', self, ' -> '.join(map(str, self.items)))
            yield [po.start() for po in reversed(self.items)]
            yield super(BasePipe, self).start()

    @gen.coroutine
    def stop(self):
        if self.started:
            yield [po.stop() for po in self.items]
            yield super(BasePipe, self).stop()

    def _link_pipe_objects(self):
        active_pipe = self.active_items
        obj_first = active_pipe[0] if active_pipe else None
        for obj_next in active_pipe[1:]:
            obj_first.set_output(obj_next)
            obj_next.set_input(obj_first)
            obj_first = obj_next

        for obj in reversed(active_pipe):
            obj.link_methods()

    def set_input(self, obj):
        logger.debug('[%s] Pipe initialized with %s.', self, obj)
        if self.active_items:
            self.active_items[0].set_input(obj)

    def set_output(self, obj):
        if self.active_items:
            self.active_items[-1].set_output(obj)

    def _input_forwarder(self, data):
        if self.active_items:
            self._input_forwarder = self.active_items[0].send
            return self._input_forwarder(data)