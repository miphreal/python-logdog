import logging

from tornado import gen
import zmq
from zmq.eventloop import zmqstream

from logdog.core.mixins import IntervalSleepPolicyMixin


logger = logging.getLogger(__name__)


class Forwarder(IntervalSleepPolicyMixin):

    def __init__(self, watcher, app, meta=None):
        self.consume_interval = app.config.forwarder.consume_interval

        self._app = app
        self._watcher = watcher
        self._path = watcher.path
        self._meta = meta
        self._started = False

        ctx = zmq.Context()
        s = ctx.socket(zmq.PUSH)
        for upstream in app.config.forwarder.upstream:
            s.connect(upstream)
        self.upstream = zmqstream.ZMQStream(s)

    def _forward_message(self, message):
        return gen.Task(self.upstream.send, message)

    @gen.coroutine
    def start(self):
        logger.info('[FWDR:%s] Starting message forwarder.', self._path)
        self._started = True

        self.base_sleep_interval = self.consume_interval
        path = self._path

        while self._started:
            message = None
            for message in self._watcher.consume_buffer():
                logger.debug('[FWDR:%s] Forwarding message: %s.', path, message)
                try:
                    yield self._forward_message(message)
                except Exception as e:
                    logger.exception('[FWDR:%s] Error: %s.', path, e)

            sleep_interval = self.sleep_interval
            logger.debug('[FWDR:%s] Sleeping on consuming messages %ss.', path, sleep_interval)
            yield gen.sleep(sleep_interval)

            if message is None:
                self.next_sleep_interval()
            else:
                self.reset_sleep_interval()

    @gen.coroutine
    def stop(self):
        logger.info('[FWDR:%s] Stopping message forwarder.', self._path)
        self._started = False
