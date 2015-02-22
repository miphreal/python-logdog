import zmq.eventloop.ioloop
from logdog.core.roles.pollers import BasePoller


zmq.eventloop.ioloop.install()


class ZMQTunnel(BasePoller):
    def __init__(self, *args, **kwargs):
        super(ZMQTunnel, self).__init__(*args, **kwargs)
