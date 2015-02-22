import logging

from tornado import gen


logger = logging.getLogger(__name__)


class BaseForwarder(object):

    def __init__(self, pipe, app, **config):
        self._app = app
        self._started = False
        self._pipe = pipe
        self._pipe_in = self._pipe_out = None

    def _init_pipe_ends(self):
        pipe = self._pipe[self]
        self._pipe_in = pipe.start
        self._pipe_out = pipe.end

    @gen.coroutine
    def start(self):
        self._init_pipe_ends()

        self._started = True

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
        self._started = False

