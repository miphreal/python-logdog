import logging
import os
import sys

from .base import BaseViewer


logger = logging.getLogger(__name__)


class Console(BaseViewer):
    defaults = BaseViewer.defaults.copy_and_update(
        redirect_to='stdout'
    )

    def __init__(self, *args, **kwargs):
        super(Console, self).__init__(*args, **kwargs)
        self._output = getattr(sys, self.config.redirect_to)

    def _input_forwarder(self, data):
        sys.stdout.write(data.message)
        if not data.message.endswith(os.linesep):
            sys.stdout.write(os.linesep)

    on_recv = _input_forwarder