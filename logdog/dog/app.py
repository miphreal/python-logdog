from tornado.util import import_object
import zmq.eventloop.ioloop

from logdog.dog.forwarders import Forwarder
from logdog.dog.watchers import FileWatcher


class Application(object):
    def __init__(self, config, loop=None):
        from tornado.ioloop import IOLoop
        self.loop = loop or IOLoop.current()
        self.loop.spawn_callback(self.init)
        self.config = config
        self.state = None
        self.watchers = []
        self.forwarders = []

    def init(self):
        default_watcher_class = import_object(self.config.watcher.default_cls)
        default_forwarder_class = import_object(self.config.forwarder.default_cls)

        for conf in self.config.watcher.targets:
            paths = conf['paths']
            meta = conf.get('meta')
            if not isinstance(paths, list):
                paths = [paths]

            watcher_class = import_object(conf['watcher_cls']) if 'watcher_cls' in conf else None
            forwarder_class = import_object(conf['forwarder_cls']) if 'watcher_cls' in conf else None

            for p in paths:
                # TODO. load last state
                watcher = (watcher_class or default_watcher_class)(path=p, offset=0, last_stat=None, app=self)
                forwarder = (forwarder_class or default_forwarder_class)(watcher, meta=meta, app=self)
                watcher.start()
                forwarder.start()

    def run(self):
        self.loop.start()


def main(config):
    zmq.eventloop.ioloop.install()
    Application(config=config).run()


if __name__ == '__main__':
    main()