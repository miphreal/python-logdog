import logging
from tornado import gen
from tornado.concurrent import Future

from ..config import Config
from ..msg import Msg
from ..utils import mark_as_coroutine, mark_as_proxy_method, is_proxy


logger = logging.getLogger(__name__)


class BaseRole(object):
    defaults = Config(
        singleton_behavior=False,
        start_delay=0,
    )
    _singleton_cache = {}

    @classmethod
    def factory(cls, *args, **kwargs):
        singleton_behavior = cls.defaults.singleton_behavior or kwargs.get('singleton_behavior', False)
        if singleton_behavior:
            key = cls.__singleton_key__(args, kwargs)
            if key in cls._singleton_cache:
                return cls._singleton_cache[key]
            new_obj = cls(*args, **kwargs)
            cls._singleton_cache[key] = new_obj
            return new_obj

        return cls(*args, **kwargs)

    @classmethod
    def __singleton_key__(cls, passed_args, passed_kwargs):
        return u'{!r}'.format(cls)

    def __init__(self, app, pipe, namespaces, **config):
        self.app = app
        self.pipe = pipe
        self.namespaces = namespaces
        self.config = self.defaults.copy_and_update(config)
        self._started = self._singleton_was_started = False
        self._started_futures = []
        self._stopped_futures = []
        self.input = self.output = None
        self.send = getattr(self, 'send', None)
        self._forward = getattr(self, '_forward', None)

        if self.config.singleton_behavior:
            logger.info('[%s] Created in a shared mode.', self)

    def __str__(self):
        return u'{}:{}'.format(self.pipe, self.__class__.__name__)

    @property
    def started(self):
        return self._started

    @started.setter
    def started(self, value):
        self._started = bool(value)
        futures = self._started_futures if self.started else self._stopped_futures
        for future in futures:
            future.set_result(self._started)

    def wait_for_start(self):
        f = Future()
        if not self.started:
            self._started_futures.append(f)
        else:
            f.set_result(True)
        return f

    def wait_for_stop(self):
        f = Future()
        if not self.started:
            self._stopped_futures.append(f)
        else:
            f.set_result(False)
        return f

    def link_methods(self):
        if getattr(self, 'send', None) is None:
            self.send = self.get_send_method()

        if getattr(self, '_forward', None) is None:
            self._forward = self.get_forward_method()

    @mark_as_proxy_method
    def _input_forwarder(self, data):
        return self.output.send(data)

    def get_send_method(self):
        return getattr(self, 'on_recv', self._input_forwarder)

    def get_forward_method(self):
        method = self._input_forwarder
        obj = self.output

        while is_proxy(method):
            if obj:
                method = obj.send
                obj = obj.output
            else:
                break

        return method

    def set_input(self, obj):
        self.input = obj

    def set_output(self, obj):
        self.output = obj

    def _prepare_message_meta(self, **extra):
        extra.setdefault('host', None)
        return extra

    def _prepare_message(self, data):
        return Msg(
            message=data,
            source=None,
            meta=self._prepare_message_meta()
        )

    def _pre_start(self):
        pass

    def _post_stop(self):
        pass

    @gen.coroutine
    def start(self):
        need_to_skip_start = self.started
        if not need_to_skip_start and self.config.singleton_behavior and self._singleton_was_started:
            need_to_skip_start = True

        if not need_to_skip_start:
            if self.config.start_delay:
                yield gen.sleep(self.config.start_delay)

            self._singleton_was_started = True
            logger.debug('[%s] Starting...', self)
            if hasattr(self.output, 'wait_for_start'):
                yield self.output.wait_for_start()
            yield gen.maybe_future(self._pre_start())
            self.started = True


    @gen.coroutine
    def stop(self):
        if self.started:
            if hasattr(self.input, 'wait_for_stop'):
                yield self.stop.wait_for_stop()
            self.started = False
            yield gen.maybe_future(self._post_stop())
