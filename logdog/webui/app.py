import logging

from tornado import gen
from tornado.web import RequestHandler, Application, url
from tornado.websocket import WebSocketHandler

import zmq
from zmq.eventloop import ioloop, zmqstream


logger = logging.getLogger(__name__)


ws = []


class IndexHandler(RequestHandler):

    def get(self):
        self.render('index.html')


class LogWebSocket(WebSocketHandler):

    @gen.coroutine
    def open(self):
        logger.debug('WebSocket opened.')
        ws.append(self)

    def on_message(self, message):
        pass

    def on_close(self):
        logger.debug('WebSocket closed.')
        ws.remove(self)


def init_app(config):
    logger.debug('Loading webui app...')
    ioloop.install()

    ctx = zmq.Context()
    s = ctx.socket(zmq.PULL)
    for a in config.webui.collector:
        s.bind(a)
    stream = zmqstream.ZMQStream(s)

    def broadcast(msg):
        for s in ws:
            for m in msg:
                s.write_message(m)

    stream.on_recv(broadcast)

    app = Application(
        handlers=[
            url(r'/', IndexHandler, name='logdog.index'),
            url(r'/ws/logs', LogWebSocket, name='logdog.logs-ws'),
        ], **config.webui)
    app.config = config

    return app