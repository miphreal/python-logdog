import zmq.eventloop.ioloop
from logdog.core.roles.connector import BaseConnector


zmq.eventloop.ioloop.install()


class ZMQTunnel(BaseConnector):
    def __init__(self, *args, **kwargs):
        super(ZMQTunnel, self).__init__(*args, **kwargs)
