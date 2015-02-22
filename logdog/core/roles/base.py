import logging
from tornado import gen

from ..config import Config
from ..utils import mark_as_coroutine


logger = logging.getLogger(__name__)


class BaseRole(object):
    defaults = Config()

    def __init__(self, app, pipe, **config):
        self.app = app
        self.pipe = pipe
        self.config = self.defaults.copy_and_update(config)
        self.started = False
        self.input = self.output = self.send = None
        self.link_methods()

    def __str__(self):
        return '{}:{}'.format(self.__class__.__name__, self.pipe)

    def link_methods(self, **kwargs):
        if getattr(self, 'send', None) is None:
            # TODO. add adjusting to async funcs
            self.send = getattr(self, 'on_recv', self._output_forwarder)

    def _output_forwarder(self, data):
        self.output.send(data)

    def set_input(self, obj):
        self.input = obj

    def set_output(self, obj):
        self.output = obj

    def _pre_start(self):
        pass

    def _post_stop(self):
        pass

    @mark_as_coroutine
    @gen.coroutine
    def start(self):
        yield gen.maybe_future(self._pre_start())
        self.started = True

    @mark_as_coroutine
    @gen.coroutine
    def stop(self):
        self.started = False
        yield gen.maybe_future(self._post_stop())
