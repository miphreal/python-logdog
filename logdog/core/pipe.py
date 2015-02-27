import logging
from tornado import gen
from logdog.core.path import Path


logger = logging.getLogger(__name__)


class Pipe(object):
    def __init__(self, *pipe_elements, **kwargs):
        self.app = kwargs.pop('app')
        self._pipe = [self._construct_pipe_element(name, conf, kwargs) for name, conf in pipe_elements]
        self._link_pipe_objects()
        self._meta_name = ''

    def _construct_pipe_element(self, name, *confs):
        cls, defaults, ns = self.app.config.find_class(name=name)
        for conf in filter(bool, confs):
            defaults.update(conf)
        defaults['app'] = self.app
        defaults['pipe'] = self
        return cls(**defaults)

    @gen.coroutine
    def start(self):
        yield [po.start() for po in reversed(self._pipe)]

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
        if self._pipe:
            self._pipe[0].set_input(data)

        if isinstance(data, Path):
            self._meta_name = data.name

    def __str__(self):
        return 'PIPE:{}'.format(self._meta_name)