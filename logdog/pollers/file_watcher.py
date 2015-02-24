import logging
from tornado import gen

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
        self.input.open()
        yield gen.moment

        logger.debug('[%s] Watching...', self)

        while self.started:
            data = self.input.read_line()

            if data:
                try:
                    self.send(self._prepare_message(data))
                except Exception as e:
                    pass
                self.poll_sleep_policy.reset()
                if not self.config.greedy_file_reading:
                    yield gen.moment
            else:
                self.input.check_stat()
                logger.debug('[%s] Sleep on watching %ss.', self, self.poll_sleep_policy.cur_interval)
                yield self.poll_sleep_policy.sleep()