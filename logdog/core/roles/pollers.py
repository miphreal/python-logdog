import logging
from tornado import gen

from ..utils import mark_as_proxy_method
from .base import BaseRole


logger = logging.getLogger(__name__)


class BasePoller(BaseRole):
    def poll(self):
        # Straightforward implementation
        while self.started:
            self.send(self.input.pop())

    @mark_as_proxy_method
    def on_recv(self, data):
        return self.output.send(data)

    @gen.coroutine
    def start(self):
        yield gen.maybe_future(self._pre_start())
        self.started = True
        yield gen.maybe_future(self.poll())
