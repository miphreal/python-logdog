import glob
from itertools import chain
import logging
import os
from tornado import gen

from logdog.core.config import Config, handle_as_list
from logdog.core.path import Path
from logdog.core.register import Register


logger = logging.getLogger(__name__)


class Application(object):

    def __init__(self, active_namespaces, config, io_loop=None,
                 force_handler=None, force_sources=None, reset_indices=False):
        from tornado.ioloop import IOLoop
        self.io_loop = io_loop or IOLoop.current()
        self.config = config
        self.force_handler = force_handler
        self.force_sources = force_sources
        self.namespaces = (Config.namespace_default,)
        self.active_namespaces = active_namespaces or [Config.namespace_default]
        self._pipes = {}
        self._sources = {}
        self.register = Register(index_file=config.options.sources.index_file, reset=reset_indices)

        logger.debug('[%s] Active namespaces: %s', self, ', '.join(self.active_namespaces))

    def __str__(self):
        return u'APP'

    @gen.coroutine
    def load_sources(self):
        flat_files = set()
        flat_patterns = set()

        sources = self.config.sources
        if self.force_sources:
            self.force_sources = self.force_sources.split(':')
            sources = handle_as_list(self.force_sources)

        for source, conf in sources:
            if not isinstance(source, (list, tuple)):
                source = [source]
            else:
                source = list(source)

            if isinstance(conf, basestring):
                conf = Config(handler=conf)
            elif not conf:
                conf = Config(handler=self.config.options.sources.default_handler)
            elif isinstance(conf, dict):
                conf.setdefault('handler', self.config.options.sources.default_handler)
            else:
                logger.warning('[APP] Weird config for "%s" (will be skipped).', ', '.join(source))
                continue

            if self.force_handler:
                conf['handler'] = self.force_handler

            intersection_patterns = flat_patterns.intersection(source)
            if intersection_patterns:
                logger.warning('[APP] Duplicate source patterns: %s (will be skipped).',
                               ', '.join(intersection_patterns))
                source = list(set(source).difference(intersection_patterns))

            source.sort()
            source = tuple(source)

            files = chain(*map(glob.glob, source))
            files = set(filter(os.path.isfile, files))

            intersection_files = flat_files.intersection(files)
            if intersection_files:
                logger.warning('[APP] Your source patterns have intersections.'
                               'The following files appeared in several groups: %s',
                               ', '.join(intersection_files))

                # remove from wider pattern
                for source_, (_, files_) in self._sources.iteritems():
                    intersection_ = files_.intersection(files)
                    if intersection_ and len(files_) > len(files):
                        files_.difference_update(intersection_)
                        logger.warning('[APP] "%s" will not be a part of "%s" group.',
                                       ', '.join(intersection_), ', '.join(source_))
                    elif intersection_:
                        files.difference_update(intersection_)
                        logger.warning('[APP] "%s" will not be a part of "%s" group.',
                                       ', '.join(intersection_), ', '.join(source))

            flat_files.update(files)
            flat_patterns.update(source)
            self._sources[source] = (conf, files)

    @gen.coroutine
    def construct_pipes(self):
        default_watcher = self.config.options.sources.default_watcher
        for conf, files in self._sources.itervalues():
            conf['app'] = self
            conf['parent'] = self

            for f in files:
                watcher = self.config.find_and_construct_class(
                    name=conf.get('watcher', default_watcher), kwargs=conf)
                pipe = self.config.find_and_construct_class(name=conf['handler'], kwargs=conf)

                try:
                    path = self.register.get_path(f)
                except KeyError:
                    path = Path(f, 0, None)

                watcher.set_input(path)
                watcher.set_output(pipe)
                pipe.link_methods()
                watcher.link_methods()

                self._pipes[f] = watcher, pipe

    @gen.coroutine
    def _init(self):
        yield self.load_sources()
        yield self.construct_pipes()

        pipes = [p for _, p in self._pipes.itervalues()]
        watchers = [w for w, _ in self._pipes.itervalues()]
        yield [i.start() for i in chain(pipes, watchers)]

    def run(self):
        self.io_loop.add_callback(self._init)
        self.io_loop.start()
