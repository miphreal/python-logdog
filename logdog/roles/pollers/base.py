import logging
from tornado import gen

from logdog.core.utils import mark_as_proxy_method
from logdog.core.base_role import BaseRole


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
        yield super(BasePoller, self).start()
        if self.started:
            yield self.poll()
