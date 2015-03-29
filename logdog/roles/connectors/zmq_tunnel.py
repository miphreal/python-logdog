from tornado import gen
from tornado.concurrent import is_future
import zmq
import zmq.eventloop.ioloop
from zmq.eventloop.zmqstream import ZMQStream

from logdog.core.msg import Msg
from .base import BaseConnector


zmq.eventloop.ioloop.install()


class ZMQTunnel(BaseConnector):
    defaults = BaseConnector.defaults(
        unique=True,
        connect=(),
        bind=(),
        socket=None,
    )

    def __init__(self, *args, **kwargs):
        if not isinstance(kwargs.get('bind', ()), (list, tuple)):
            kwargs['bind'] = (kwargs['bind'],)
        if not isinstance(kwargs.get('connect', ()), (list, tuple)):
            kwargs['connect'] = (kwargs['connect'],)

        self.stream = self.socket = None
        self.ctx = zmq.Context()

        super(ZMQTunnel, self).__init__(*args, **kwargs)

    def __str__(self):
        return u'ZMQ-TUNNEL:{}:{}'.format(self.config.socket,
                                          ','.join(self.config.bind) or
                                          ','.join(self.config.connect) or 'None')

    @classmethod
    def __singleton_key__(cls, passed_args, passed_kwargs):
        key = super(ZMQTunnel, cls).__singleton_key__(passed_args, passed_kwargs)
        connect = passed_kwargs.get('connect', cls.defaults.connect) or ()
        if not isinstance(connect, (list, tuple)):
            connect = [connect]
        bind = passed_kwargs.get('bind', cls.defaults.bind) or ()
        if not isinstance(bind, (list, tuple)):
            bind = [bind]
        return u'{key}::socket-type={socket_type}::bind={bind}::connect={connect}'.format(
            key=key,
            socket_type=passed_kwargs.get('socket', cls.defaults.socket),
            connect=','.join(sorted(connect)) or 'None',
            bind=','.join(sorted(bind)) or 'None',
        )

    def _pre_start(self):
        self.socket = self.ctx.socket(getattr(zmq, self.config.socket))

        if 'bind' in self.config:
            for addr in self.config.bind:
                self.socket.bind(addr)

        if 'connect' in self.config:
            for addr in self.config.connect:
                self.socket.connect(addr)

        self.stream = ZMQStream(self.socket, io_loop=self.app.io_loop)
        self.stream.on_recv(self.on_recv)

    @gen.coroutine
    def on_recv(self, data):
        data = Msg.deserialize_jsonb(data[0])
        ret = self._forward(data)
        if is_future(ret):
            yield ret

    def send(self, data):
        if self.started:
            data = data.serialize_jsonb()
            return self.stream.send(msg=data)