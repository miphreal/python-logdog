from collections import deque
import os
import logging

from tornado import gen

from logdog.core.mixins import IntervalSleepPolicyMixin


logger = logging.getLogger(__name__)


class FileWatcher(IntervalSleepPolicyMixin):

    def __init__(self, path, offset, last_stat, app):
        self.poll_interval = app.config.watcher.poll_interval
        self.max_poll_interval = app.config.watcher.max_poll_interval
        self.poll_interval_count = app.config.watcher.poll_interval_count
        self.buffer_size = app.config.watcher.buffer_size
        self.consume_buffer_size = self.buffer_size

        self.app = app
        self.path = path
        self._offset = offset
        self._prev_stat = self._stat = last_stat
        self._f = None

        self._last_read_line = None

        self._buffer = deque(maxlen=self.buffer_size)
        self._wait_for_writable_buf = None

        self._started = False

        logger.debug('[FILE:%s] Created file watcher.', self.path)
        logger.debug('[FILE:%s] Watcher: offset=%s poll-interval=%s', self.path, self._offset, self.poll_interval)

    def _check_buffer_renew_write_policy(self):
        write_available = len(self._buffer) <= self.buffer_size / 2
        if write_available and self._wait_for_writable_buf and not self._wait_for_writable_buf.done():
            self._wait_for_writable_buf.set_result(None)

    def _check_buffer_write_policy(self):
        return len(self._buffer) < self.buffer_size

    def _wait_for_buffer_write_availability(self):
        self._wait_for_writable_buf = gen.Future()
        return self._wait_for_writable_buf

    def consume_buffer(self, n=None):
        """Note. this is NOT a coroutine"""
        if n is None:
            n = self.consume_buffer_size
        while n:
            n -= 1
            try:
                yield self._buffer.popleft()
                self._check_buffer_renew_write_policy()
            except IndexError:
                return

    def _open(self):
        self._f = open(self.path, 'r')
        self._f.seek(self._offset)
        self._stat = os.stat(self.path)

    def _reopen(self):
        self._f.close()
        self._open()

    def _check_stat(self):
        """Is called if we have nothing to read"""
        self._prev_stat = self._stat
        self._stat = os.stat(self.path)

        if not self._is_same_file(self._prev_stat, self._stat):
            logger.debug('[FILE:%s] New file detected by this path. Re-opening...', self.path)
            self._offset = 0
            self._reopen()

        elif self._is_file_truncated(self._prev_stat, self._stat):
            logger.debug('[FILE:%s] Seems, file was truncated. Re-opening...', self.path)
            self._offset = 0
            self._reopen()

    def _is_same_file(self, prev_stat, cur_stat):
        return prev_stat.st_ino == cur_stat.st_ino and prev_stat.st_dev and cur_stat.st_dev

    def _is_file_truncated(self, prev_stat, cur_stat):
        return prev_stat.st_size > cur_stat.st_size

    def _read_line(self):
        self._last_read_line = (self._offset, self._f.readline())
        self._offset = self._f.tell()
        return self._last_read_line[1]

    @gen.coroutine
    def start(self):
        logger.info('[FILE:%s] Starting watching...', self.path)
        self._started = True
        self._open()

        self.base_sleep_interval = self.poll_interval
        self.sleep_repeat_count = self.poll_interval_count
        self.max_sleep_interval = self.max_poll_interval

        while self._started:
            data = None
            try:
                data = self._read_line()
            except Exception as e:
                logger.exception(self.path)

            if data:
                yield self.handle_chunk(data)
                self.reset_sleep_interval()
            else:
                self._check_stat()
                logger.debug('[FILE:%s] Sleep on watching %ss.', self.path, self.sleep_interval)
                yield gen.sleep(self.sleep_interval)
                self.next_sleep_interval()

    @gen.coroutine
    def stop(self):
        logger.info('[FILE:%s] Stopping watching...', self.path)
        self._started = False
        self._f.close()

    @gen.coroutine
    def handle_chunk(self, chunk):
        # preprocessing chunk of data
        chunk = chunk.strip()

        logger.debug('[FILE:%s] Log: %s', self.path, chunk)
        if not self._check_buffer_write_policy():
            logger.info('[FILE:%s] Buffer is full. Stopping watching until buffer available...', self.path)
            yield self._wait_for_buffer_write_availability()
        self._buffer.append(chunk)
