import logging
from tornado import gen

from logdog.core.base_role import BaseRole


logger = logging.getLogger(__name__)


class BaseForwarder(BaseRole):

    def __init__(self, *args, **kwargs):
        super(BaseForwarder, self).__init__(*args, **kwargs)
        self.items = [self.construct_subrole(name, conf) for name, conf in self.items]
        self.link_methods()
        for i in self.items:
            i.link_methods()

    def __str__(self):
        return 'FORWARDER:{}'.format(self._oid)

    @gen.coroutine
    def start(self):
        if not self.started:
            yield [i.start() for i in self.items]
            yield super(BaseForwarder, self).start()

    @gen.coroutine
    def stop(self):
        if self.started:
            yield [i.stop() for i in self.items]
            yield super(BaseForwarder, self).stop()

