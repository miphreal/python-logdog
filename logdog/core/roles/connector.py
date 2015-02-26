import logging
from tornado import gen

from .base import BaseRole


logger = logging.getLogger(__name__)


class BaseConnector(BaseRole):
    pass