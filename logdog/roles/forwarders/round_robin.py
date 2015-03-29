from tornado import gen

from .base import BaseForwarder


class RoundRobin(BaseForwarder):

    def __init__(self, *args, **kwargs):
        super(RoundRobin, self).__init__(*args, **kwargs)
        self._curr_target = 0

    def __str__(self):
        return u'ROUND-ROBIN:{}'.format(self.input)

    @gen.coroutine
    def _input_forwarder(self, data):
        if self.items:
            ret = self.items[self._curr_target].send(data)
            self._curr_target = (self._curr_target + 1) % len(self.items)
            if gen.is_future(ret):
                yield gen.maybe_future(ret)