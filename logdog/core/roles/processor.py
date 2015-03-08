import logging

from .base import BaseRole


logger = logging.getLogger(__name__)


class BaseProcessor(BaseRole):
    defaults = BaseRole.defaults(unique=True)

    def on_recv(self, data):
        self.output.send(data)