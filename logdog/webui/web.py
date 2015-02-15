import logging
from tornado.ioloop import IOLoop
from logdog.webui.app import init_app


logger = logging.getLogger(__name__)


def main(config):
    app = init_app(config)
    app.listen(address=config.webui.address,
               port=config.webui.port)
    logger.info('Starting logdog.webui: %s:%s...',
                config.webui.address or '*', config.webui.port)
    IOLoop.current().start()


if __name__ == '__main__':
    main()