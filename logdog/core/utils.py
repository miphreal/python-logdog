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