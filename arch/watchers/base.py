from collections import deque
import logging

from tornado import gen

from ..core.config import Config
from ..core.pipe import BasePipeObject
from ..core.polling_policies import PollingSleepPolicy


logger = logging.getLogger(__name__)


class BaseWatcher(BasePipeObject):
    defaults = Config(
        buffer_size=1024,
        consume_buffer_size=1024,
        poll_interval=0.5,
        max_poll_interval=5 * 60,
        poll_interval_count=120,
        poll_sleep_policy=PollingSleepPolicy,
    )

    def __init__(self, path_obj, app, **config):
        self.config = self.defaults.copy()
        self.config.update(config)

        self.poll_sleep_policy = self.config.poll_sleep_policy_class(
            sleep_interval=self.config.poll_interval,
            max_sleep_interval=self.config.max_poll_interval,
            sleep_repeat_count=self.config.poll_interval_count
        )

        self.app = app
        self.f = path_obj
        self.path = path_obj.name

        self._buffer = deque(maxlen=self.config.buffer_size)
        self._wait_for_writable_buf = None

        self._started = False

        logger.debug('[%s] Created file watcher.', self)
        logger.debug('[%s] Watcher: offset=%s poll-interval=%s', self, self.f.offset, self.config.poll_interval)

    def _check_buffer_renew_write_policy(self):
        write_available = len(self._buffer) <= self.config.buffer_size / 2
        if write_available and self._wait_for_writable_buf and not self._wait_for_writable_buf.done():
            self._wait_for_writable_buf.set_result(None)

    def _check_buffer_write_policy(self):
        return len(self._buffer) < self.config.buffer_size

    def _wait_for_buffer_writability(self):
        self._wait_for_writable_buf = gen.Future()
        return self._wait_for_writable_buf

    def receive(self, n=None):
        """Note. this is NOT a coroutine"""
        if n is None:
            n = len(self._buffer)
        while n:
            n -= 1
            try:
                yield self._buffer.popleft()
                self._check_buffer_renew_write_policy()
            except IndexError:
                return

    def _read_input(self):
        return gen.maybe_future(self.f.read_line())


    @gen.coroutine
    def start(self):
        logger.info('[%s] Starting watching...', self)

        self._started = True
        self.f.open()

        while self._started:
            data = yield self._read_input()
            self.poll_sleep_policy.reset()

            if data:
                yield self._write_output(data)
            else:
                self.f.check_stat()
                logger.debug('[%s] Sleep on watching %ss.', self, self.poll_sleep_policy.cur_interval)
                yield self.poll_sleep_policy.sleep()

    @gen.coroutine
    def stop(self):
        logger.info('[%s] Stopping watching...', self)
        self._started = False
        self.f.close()

    def __str__(self):
        return u'WATCHER:{}'.format(self.path)
