import logging
from tornado import gen

from tornado.web import Application, url

from logdog.core.roles.viewer import BaseViewer


logger = logging.getLogger(__name__)


_web_apps = {}


class WebApp(Application):
    def __init__(self, *args, **kwargs):
        from .web import IndexHandler, LogWebSocket
        handlers = [
            url(r'/', IndexHandler, name='logdog.index'),
            url(r'/ws/logs', LogWebSocket, name='logdog.logs-ws'),
        ]
        self.ws = []
        kwargs['handlers'] = handlers
        super(WebApp, self).__init__(*args, **kwargs)


class WebUI(BaseViewer):

    def __str__(self):
        return u'WEBUI:{!s}'.format(self.pipe)

    @gen.coroutine
    def _pre_start(self):

        global _web_apps
        _web_app = _web_apps.get((self.config.address or '*', self.config.port))
        self._web_app = _web_app
        if _web_app:
            logger.info('[%s] Joining %s:%s...', self,
                        self.config.address or '*', self.config.port)
            return

        logger.debug('[%s] Loading webui app...', self)
        _web_app = WebApp(**self.config)
        _web_app.listen(address=self.config.address, port=self.config.port)
        logger.info('[%s] Starting %s:%s...', self,
                    self.config.address or '*', self.config.port)

        self._web_app = _web_app
        _web_apps[(self.config.address or '*', self.config.port)] = _web_app

    def on_recv(self, data):
        if self.started:
            for ws in self._web_app.ws:
                ws.write_message(data)
