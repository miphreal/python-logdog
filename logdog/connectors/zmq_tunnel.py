from tornado import gen
from tornado.concurrent import is_future
import zmq
import zmq.eventloop.ioloop
from zmq.eventloop.zmqstream import ZMQStream
from logdog.core.msg import Msg
from logdog.core.roles.connector import BaseConnector


zmq.eventloop.ioloop.install()


class ZMQTunnel(BaseConnector):
    _sockets = {}  # TODO. shared sockets OR singleton

    def __init__(self, *args, **kwargs):
        super(ZMQTunnel, self).__init__(*args, **kwargs)
        self.ctx = None
        self.socket = None
        self.stream = None
        if 'bind' in self.config and not isinstance(self.config.bind, (list, tuple)):
            self.config.bind = [self.config.bind]
        if 'connect' in self.config and not isinstance(self.config.connect, (list, tuple)):
            self.config.connect = [self.config.connect]

    def _pre_start(self):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(getattr(zmq, self.config.socket))

        if 'bind' in self.config:
            for addr in self.config.bind:
                self.socket.bind(addr)

        if 'connect' in self.config:
            for addr in self.config.connect:
                self.socket.connect(addr)

        self.stream = ZMQStream(self.socket)
        self.stream.on_recv(self.on_recv)

    @gen.coroutine
    def start(self):
        self._pre_start()
        self.started = True

    @gen.coroutine
    def on_recv(self, data):
        data = Msg.deserialize_json(data[0])
        ret = self._forward(data)
        if is_future(ret):
            yield ret

    @gen.coroutine
    def send(self, data):
        if self.started:
            data = data.serialize_json()
            yield gen.Task(self.stream.send, msg=data)
        else:
            yield gen.moment