import glob
from itertools import chain
import logging
from tornado import gen

from logdog.core.config import ConfigLoader, Config
from logdog.core.path import Path
from logdog.core.pipe import Pipe


logger = logging.getLogger(__name__)


class Application(object):

    def __init__(self, active_parts=None, config_path=None, loop=None):
        from tornado.ioloop import IOLoop
        self.loop = loop or IOLoop.current()
        self._config_path = config_path
        self.config = None
        self._active_parts = active_parts
        self._pipes = {}
        self._register = {}
    @gen.coroutine
    def load_config(self):
        loader = ConfigLoader(path=self._config_path)
        self.config = loader.load_config(default_only=not self._config_path)

    @gen.coroutine
    def load_sources(self):
        flat_files = set()
        flat_patterns = set()
        for source, conf in self.config.sources:
            if not isinstance(source, (list, tuple)):
                source = [source]

            if isinstance(conf, basestring):
                conf = Config(pipe=conf)
            elif not conf:
                conf = Config(pipe=self.config.default_pipe)
            elif isinstance(conf, dict):
                if 'pipe' not in conf:
                    conf['pipe'] = self.config.default_pipea
            else:
                logger.warning('[APP] Weird config for "%s" (will be skipped).', ', '.join(source))
                continue

            intersection_patterns = flat_patterns.intersection(source)
            if intersection_patterns:
                logger.warning('[APP] Duplicate source patterns: %s (will be skipped).',
                               ', '.join(intersection_patterns))
                source = list(set(source).difference(intersection_patterns))

            source.sort()
            source = tuple(source)

            files = set(chain(*map(glob.glob, source)))

            intersection_files = flat_files.intersection(files)
            if intersection_files:
                logger.warning('[APP] Your source patterns have intersections.'
                               'The following files appeared in several groups: %s',
                               ', '.join(intersection_files))

                # remove from wider pattern
                for source_, (_, files_) in self._register.iteritems():
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
            self._register[source] = (conf, files)

    @gen.coroutine
    def construct_pipes(self):
        for conf, files in self._register.itervalues():
            for f in files:
                self._pipes[f] = pipe = self.construct_pipe(**conf)
                pipe.set_input(Path(f, 0, None))

    def construct_pipe(self, pipe, **kwargs):
        pipe_cls = Pipe
        defaults, name, ns = self.config.find_conf(pipe, fallback=self.config.default_pipe)
        kwargs['app'] = self

        if isinstance(defaults, dict):
            defaults.update(kwargs)
            return pipe_cls(**defaults)
        elif isinstance(defaults, (list, tuple)):
            return pipe_cls(*defaults, **kwargs)
        else:
            return pipe_cls(**kwargs)

    @gen.coroutine
    def _init(self):
        yield self.load_config()
        yield self.load_sources()
        yield self.construct_pipes()

        yield [p.start() for p in self._pipes.itervalues()]

    def run(self):
        self.loop.add_callback(self._init)
        self.loop.start()
