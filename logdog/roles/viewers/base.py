import logging

from logdog.core.base_role import BaseRole


logger = logging.getLogger(__name__)


class BaseViewer(BaseRole):

    def on_recv(self, data):
        logger.debug(data)