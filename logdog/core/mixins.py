import logging


logger = logging.getLogger(__name__)


class IntervalSleepPolicyMixin(object):
    base_sleep_interval = 0.5
    max_sleep_interval = 5 * 60.
    sleep_repeat_count = 10

    _sleep_interval = base_sleep_interval
    _sleep_repeat_count = sleep_repeat_count

    @property
    def sleep_interval(self):
        return self._sleep_interval

    def reset_sleep_interval(self):
        self._sleep_interval = self.base_sleep_interval
        self._sleep_repeat_count = self.sleep_repeat_count

    def next_sleep_interval(self):
        if not self._sleep_repeat_count:
            self._sleep_repeat_count = self.sleep_repeat_count
            self._sleep_interval *= 2
            if self._sleep_interval > self.max_sleep_interval:
                self._sleep_interval = self.max_sleep_interval
        self._sleep_repeat_count -= 1
