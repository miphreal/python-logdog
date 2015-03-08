from tornado import gen

from logdog.core.roles.forwarder import BaseForwarder


class Broadcast(BaseForwarder):
    def __str__(self):
        return u'BROADCAST:{}'.format(self.input)

    @gen.coroutine
    def _input_forwarder(self, data):
        return [gen.maybe_future(i.send(data)) for i in self.items]