import logging
from tornado import gen

from logdog.core.roles.pollers import BasePoller


logger = logging.getLogger(__name__)


class FileWatcher(BasePoller):
    defaults = BasePoller.defaults.copy_and_update(
        poll_sleep_policy='utils.sleep-policies.default'
    )

    def __init__(self, app, **config):
        super(FileWatcher, self).__init__(app, **config)
        self.poll_sleep_policy = self.app.config.find_and_construct_class(name=self.config.poll_sleep_policy)

    def __str__(self):
        return u'WATCHER:{!s}'.format(self.pipe)

    @gen.coroutine
    def poll(self):
        self.input.open()
        yield gen.moment

        logger.debug('[%s] Watching...', self)

        while self.started:
            data = self.input.read_line()

            if data:
                try:
                    self.send(data)
                except Exception as e:
                    pass
                self.poll_sleep_policy.reset()
                yield gen.moment
            else:
                self.input.check_stat()
                logger.debug('[%s] Sleep on watching %ss.', self, self.poll_sleep_policy.cur_interval)
                yield self.poll_sleep_policy.sleep()