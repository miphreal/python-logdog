from collections import deque
from itertools import chain, product
import logging
from operator import or_
from tornado import gen
from logdog.core.config import Config
from logdog.core.polling_policies import PollingSleepPolicy


logger = logging.getLogger(__name__)


# PIPE communication roles
# actively poll messages
ACTIVE_SYNC_READER = 2 ** 0     # synchronously poll messages from the input
ACTIVE_ASYNC_READER = 2 ** 1    # asynchronously poll messages from the input
# pass messages forward as soon as it gets them
ACTIVE_SYNC_WRITER = 2 ** 2     # synchronously write messages to the output
ACTIVE_ASYNC_WRITER = 2 ** 3    # asynchronously write messages to the output

# do nothing to retrieve messages
PASSIVE_SYNC_READER = 2 ** 4    # synchronously handle `send` call
PASSIVE_ASYNC_READER = 2 ** 5   # asynchronously handle `send` call
# do nothing to pass messages forward
PASSIVE_SYNC_WRITER = 2 ** 6    # collect all incoming messages in the buffer / interim storage
PASSIVE_ASYNC_WRITER = 2 ** 7   # asynchronously collect all incoming messages in the buffer / interim storage

VIABLE_PIPE_OBJ_RELATIONS = [
    # A(output) <-> B(input)
    # Note. Asynchronous operation cannot come after active synchronous one
    (ACTIVE_ASYNC_WRITER, PASSIVE_ASYNC_READER),
    (ACTIVE_ASYNC_WRITER, PASSIVE_SYNC_READER),
    (ACTIVE_SYNC_WRITER, PASSIVE_SYNC_READER),

    (PASSIVE_ASYNC_WRITER, ACTIVE_ASYNC_READER),
    (PASSIVE_SYNC_WRITER, ACTIVE_ASYNC_READER),
    (PASSIVE_ASYNC_WRITER, ACTIVE_SYNC_READER),
    (PASSIVE_SYNC_WRITER, ACTIVE_SYNC_READER),
    (PASSIVE_SYNC_WRITER, ACTIVE_SYNC_READER),

    # all other communication pairs won't work
]




class Pipe(object):

    def __init__(self, *pipe_objects):
        self._pipe = pipe_objects

        pipe_obj = pipe_objects[0] if pipe_objects else None
        for po in pipe_objects[1:]:
            self.link_pipe_objects(pipe_obj, po)

    @gen.coroutine
    def start(self):
        yield [po.start() for po in self._pipe]

    @staticmethod
    def link_pipe_objects(obj_first, obj_next):
        obj_first.set_output(obj_next)
        obj_next.set_input(obj_first)

        pairs = product(obj_first.output_roles_priority, obj_next.input_roles_priority)
        pair = next((for _pair in pairs if _pair in VIABLE_PIPE_OBJ_RELATIONS), None)

        if pair is not None:
            obj_first.add_roles(pair[0])
            obj_next.add_roles(pair[1])


class BasePipeObject(object):
    """
    All `messages` objects are iterable objects (list/tuple of messages; iterator; generator)
    """

    # expectations
    as_reader_roles_priority = [PASSIVE_ASYNC_READER, PASSIVE_SYNC_READER]
    as_writer_roles_priority = [ACTIVE_ASYNC_WRITER, ACTIVE_SYNC_WRITER]

    defaults = Config(
        default_active_roles=(PASSIVE_SYNC_READER, ACTIVE_SYNC_WRITER),
    )

    def __init__(self, app, config):
        self.app = app
        self.config = self.defaults.copy()
        self.config.update(config)

        self._started = False
        self.active_roles = 0
        self.input = self.output = None
        self.send = self.receive = self.poll = None

    @property
    def supported_roles(self):
        return reduce(or_, chain(self.as_reader_roles_priority, self.as_writer_roles_priority))

    def add_roles(self, *roles):
        self.active_roles |= reduce(or_, roles)

    def is_active_writer(self):
        return self.active_roles & ACTIVE_SYNC_WRITER or self.active_roles & ACTIVE_ASYNC_WRITER

    def is_passive_writer(self):
        return self.active_roles & PASSIVE_SYNC_WRITER or self.active_roles & PASSIVE_ASYNC_WRITER

    def is_active_reader(self):
        return self.active_roles & ACTIVE_SYNC_READER or self.active_roles & ACTIVE_ASYNC_READER

    def is_passive_reader(self):
        return self.active_roles & PASSIVE_SYNC_READER or self.active_roles & PASSIVE_ASYNC_READER

    def set_input(self, obj):
        self.input = obj

    def set_output(self, obj):
        self.output = obj

    # Communication methods
    def _sync_forward(self, messages):
        """Sends messages to the next pipe object"""
        self.output.send(messages=messages)

    @gen.coroutine
    def _async_forward(self, messages):
        """Sends messages to the next pipe object asynchronously"""
        yield gen.maybe_future(self.output.send(messages=messages))

    def _sync_put(self, messages):
        """Puts messages to the pipe object"""
        raise NotImplementedError

    @gen.coroutine
    def _async_put(self, messages):
        """Puts messages to the pipe object asynchronously"""
        raise NotImplementedError

    def _sync_receive(self, n=None):
        """Returns messages from the current pipe object"""
        raise NotImplementedError

    @gen.coroutine
    def _async_receive(self, n=None):
        """Returns messages from the current pipe object asynchronously"""
        raise NotImplementedError

    @gen.coroutine
    def poll(self):
        raise NotImplementedError

    methods_map = {
        ('send', '_async_forward'): lambda po: (
            po.input and po.input.is_active_writer()
            and po.input.active_roles & ACTIVE_ASYNC_WRITER
            and po.is_active_writer()
        ),
        ('send', '_sync_forward'): lambda po: (
            po.input and po.input.is_active_writer()
            and po.input.active_roles & ACTIVE_SYNC_WRITER
            and po.is_active_writer()
        ),
        ('send', '_async_put'): lambda po: (
            po.input and po.input.is_active_writer()
            and po.input.active_roles & ACTIVE_ASYNC_WRITER
            and po.is_passive_writer()
        ),
        ('send', '_sync_put'): lambda po: (
            po.input and po.input.is_active_writer()
            and po.input.active_roles & ACTIVE_SYNC_WRITER
            and po.is_passive_writer()
        ),
        ('receive', '_async_receive'): lambda po: (
            po.output and po.is_passive_writer()
            and po.output.active_roles & ACTIVE_ASYNC_READER
        ),
        ('receive', '_sync_receive'): lambda po: (
            po.output and po.is_passive_writer()
            and po.output.active_roles & ACTIVE_SYNC_READER
        ),
    }

    def _pre_start(self):
        pass

    def _post_stop(self):
        pass

    # Running/Stopping pipe object
    @gen.coroutine
    def start(self):
        logger.info('[%s] Starting...', self)

        for (interface_name, method_name), condition in self.methods_map.iteritems():
            if condition(self):
                method = getattr(self, method_name, None)
                if callable(method):
                    setattr(self, interface_name, method)

        yield gen.maybe_future(self._pre_start())
        self._started = True

        if self.is_active_reader():
            yield gen.maybe_future(self.poll())

    @gen.coroutine
    def stop(self):
        logger.info('[%s] Stopping...', self)
        self._started = False
        yield gen.maybe_future(self._post_stop())


class BaseBufferedPipeObject(BasePipeObject):

    as_reader_roles_priority = BasePipeObject.as_reader_roles_priority
    as_writer_roles_priority = [PASSIVE_ASYNC_WRITER, PASSIVE_SYNC_WRITER] + BasePipeObject.as_writer_roles_priority

    defaults = BasePipeObject.defaults.inherit(
        default_active_roles=(PASSIVE_SYNC_READER, PASSIVE_ASYNC_WRITER),
        buffer_size=1024,
    )
    _async_receive = None

    def __init__(self, app, config):
        super(BaseBufferedPipeObject, self).__init__(app=app, config=config)

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

    def _sync_put(self, messages):
        """Puts messages to the pipe object"""
        if not self._check_buffer_write_policy():
            logger.warning('[%s] Buffer is full. Configure "%s" to work in async way.', self, self.input)
        self._buffer.append(messages)

    @gen.coroutine
    def _async_put(self, messages):
        """Puts messages to the pipe object asynchronously"""
        if not self._check_buffer_write_policy():
            logger.info('[%s] Buffer is full. Waiting until buffer is available...', self)
            yield self._wait_for_buffer_writability()
        self._buffer.append(messages)

    def _sync_receive(self, n=None):
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