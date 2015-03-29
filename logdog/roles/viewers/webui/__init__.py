import logging
import os
from tornado import gen
from tornado.web import Application, url

from ..base import BaseViewer


logger = logging.getLogger(__name__)


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
    defaults = BaseViewer.defaults(
        unique=True,
        port=8888,
        address='',
        autoreload=False,
        debug=False,
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        template_path=os.path.join(os.path.dirname(__file__), 'assets/html'),
    )

    def __init__(self, *args, **kwargs):
        super(WebUI, self).__init__(*args, **kwargs)
        self._web_app = WebApp(**self.config)

    def __str__(self):
        return u'WEBUI:http://{}:{}'.format(self.config.address or '0.0.0.0', self.config.port)

    @classmethod
    def __singleton_key__(cls, passed_args, passed_kwargs):
        key = super(WebUI, cls).__singleton_key__(passed_args, passed_kwargs)
        return u'{key}:address={address}:port={port}'.format(
            key=key,
            address=passed_kwargs.get('address', cls.defaults.address),
            port=passed_kwargs.get('port', cls.defaults.port)
        )

    @gen.coroutine
    def _pre_start(self):
        logger.info('[%s] Starting %s:%s...', self, self.config.address or '0.0.0.0', self.config.port)
        try:
            self._web_app.listen(address=self.config.address, port=self.config.port)
        except Exception as e:
            logger.exception(e)

    def on_recv(self, data):
        if self.started:
            for ws in self._web_app.ws:
                ws.write_message(data.serialize_json())
