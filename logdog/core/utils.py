import logging
from string import ascii_letters
import time
import functools


logger = logging.getLogger(__name__)


def mark_as_coroutine(func):
    func.is_coroutine = True
    return func


def mark_as_proxy_method(func):
    func.is_proxy_method = True
    return func


def is_coroutine(func):
    return getattr(func, 'is_coroutine', False)


def is_proxy(func):
    return getattr(func, 'is_proxy_method', False)


def simple_oid():
    oid = []
    x = int(time.time() * 10000) % 10 ** 8
    n = len(ascii_letters)
    while x:
        oid.insert(0, ascii_letters[x % n])
        x /= n
    return ''.join(oid)


def debug_deco(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
    return wrapper