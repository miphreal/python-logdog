from collections import deque
import logging
from tornado import gen

from logdog.core.base_role import BaseRole


logger = logging.getLogger(__name__)


class BaseCollector(BaseRole):
    defaults = BaseRole.defaults.inherit(
        buffer_size=1024,
    )

    def __init__(self, *args, **kwargs):
        super(BaseCollector, self).__init__(*args, **kwargs)
        self._buffer = deque(maxlen=self.config.buffer_size)
        self._wait_for_writable_buf = None

    def _check_buffer_renew_write_policy(self):
        write_available = len(self._buffer) <= self.config.buffer_size / 2
        if write_available and self._wait_for_writable_buf and not self._wait_for_writable_buf.done():
            self._wait_for_writable_buf.set_result(None)

    def _check_buffer_write_policy(self):
        return len(self._buffer) < self.config.buffer_size

    def _wait_for_buffer_writability(self):
        self._wait_for_writable_buf = gen.Future()
        return self._wait_for_writable_buf

    @gen.coroutine
    def on_recv(self, data):
        if not self._check_buffer_write_policy():
            logger.info('[%s] Buffer is full. Waiting until buffer is available...', self)
            yield self._wait_for_buffer_writability()
        self._buffer.append(data)

    def pop(self):
        try:
            data = self._buffer.popleft()
        except IndexError:
            return

        self._check_buffer_renew_write_policy()
        return data

