import logging
from tornado import gen


logger = logging.getLogger(__name__)


class DefaultSleepPolicy(object):
    BASE_SLEEP_INTERVAL = 0.5
    MAX_SLEEP_INTERVAL = 5 * 60.
    SLEEP_REPEAT_COUNT = 10

    def __init__(self, sleep_interval=BASE_SLEEP_INTERVAL,
                 max_sleep_interval=MAX_SLEEP_INTERVAL,
                 sleep_repeat_count=SLEEP_REPEAT_COUNT):

        self._base_sleep_interval = self._sleep_interval = sleep_interval
        self._max_sleep_interval = max_sleep_interval
        self._sleep_repeat_count = self._base_sleep_repeat_count = sleep_repeat_count

    def _next_sleep_interval(self):
        if not self._sleep_repeat_count:
            self._sleep_repeat_count = self._base_sleep_repeat_count
            self._sleep_interval *= 2
            if self._sleep_interval > self._max_sleep_interval:
                self._sleep_interval = self._max_sleep_interval
            return
        self._sleep_repeat_count -= 1

    def sleep(self):
        f = gen.sleep(self._sleep_interval)
        f.add_done_callback(lambda _: self._next_sleep_interval())
        return f

    @property
    def cur_interval(self):
        return self._sleep_interval

    def reset(self):
        self._sleep_interval = self._base_sleep_interval
        self._sleep_repeat_count = self._base_sleep_repeat_count
