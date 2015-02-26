import logging
from tornado import gen
from tornado.concurrent import is_future

from logdog.core.roles.pollers import BasePoller


logger = logging.getLogger(__name__)


class FileWatcher(BasePoller):
    defaults = BasePoller.defaults.copy_and_update(
        poll_sleep_policy='utils.sleep-policies.default',
        greedy_file_reading=True,
    )

    def __init__(self, app, **config):
        super(FileWatcher, self).__init__(app, **config)
        self.poll_sleep_policy = self.app.config.find_and_construct_class(name=self.config.poll_sleep_policy)

    def __str__(self):
        return u'WATCHER:{!s}'.format(self.pipe)

    def _prepare_message(self, data):
        msg = super(FileWatcher, self)._prepare_message(data)
        msg.source = getattr(self.input, 'name', msg.source)
        return msg

    @gen.coroutine
    def poll(self):
        greedy_file_reading_enabled = self.config.greedy_file_reading
        self.input.open()

        yield gen.moment
        logger.debug('[%s] Watching...', self)

        while self.started:
            data = self.input.read_line()

            if data:
                data = self._prepare_message(data)
                try:
                    ret = self._forward(data)
                    if is_future(ret):
                        yield ret
                except Exception as e:
                    logger.exception(e)

                self.poll_sleep_policy.reset()
                if not greedy_file_reading_enabled:
                    yield gen.moment
            else:
                self.input.check_stat()
                logger.debug('[%s] Sleep on watching %ss.', self, self.poll_sleep_policy.cur_interval)
                yield self.poll_sleep_policy.sleep()