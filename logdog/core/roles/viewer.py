import logging

from .base import BaseRole


logger = logging.getLogger(__name__)


class BaseViewer(BaseRole):

    def on_recv(self, data):
        logger.debug(data)