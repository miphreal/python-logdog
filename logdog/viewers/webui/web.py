import logging

from tornado import gen
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler


logger = logging.getLogger(__name__)


class IndexHandler(RequestHandler):

    def get(self):
        self.render('index.html')


class LogWebSocket(WebSocketHandler):

    @gen.coroutine
    def open(self):
        logger.info('Client connected.')
        self.application.ws.append(self)

    def on_close(self):
        logger.debug('Connection closed.')
        self.application.ws.remove(self)