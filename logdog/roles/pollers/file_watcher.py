import logging
from tornado import gen
from tornado.concurrent import is_future

from .base import BasePoller


logger = logging.getLogger(__name__)


class FileWatcher(BasePoller):
    defaults = BasePoller.defaults.copy_and_update(
        poll_sleep_policy='utils.policies.growing-sleep',
        greedy_policy='utils.policies.mostly-greedy',
        greedy_file_reading=True,
        start_delay=2.5,
    )

    def __init__(self, *args, **kwargs):
        super(FileWatcher, self).__init__(*args, **kwargs)
        self.poll_sleep_policy = self.app.config.find_and_construct_class(name=self.config.poll_sleep_policy)
        self.greedy_policy = self.app.config.find_and_construct_class(name=self.config.greedy_policy)

    def __str__(self):
        return u'WATCHER:{!s}'.format(self.input)

    def _prepare_message(self, data):
        msg = super(FileWatcher, self)._prepare_message(data)
        msg.source = getattr(self.input, 'name', msg.source)
        return msg

    @gen.coroutine
    def poll(self):
        greedy_file_reading_enabled = self.config.greedy_file_reading

        try:
            self.input.open()
            logger.info('[%s] Opened %s.', self, self.input)
        except IOError as e:
            logger.error('[%s] Stopping watching because of errors (%s)...', self, e)
            self.started = False
            yield self.stop()
            return

        while self.started:
            try:
                data = self.input.read_line()

                if data:
                    data = self._prepare_message(data)
                    ret = self._forward(data)
                    if is_future(ret):
                        yield ret

                    self.poll_sleep_policy.reset()

                    if greedy_file_reading_enabled and self.greedy_policy.need_to_wait():
                        yield self.greedy_policy.wait()

                else:
                    self.input.check_stat()
                    self.app.register.set_path(self.input)
                    logger.debug('[%s] Sleep on watching %ss.', self, self.poll_sleep_policy.cur_interval)
                    yield self.poll_sleep_policy.sleep()
            except Exception as e:
                raise