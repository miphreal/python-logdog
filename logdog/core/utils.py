def mark_as_coroutine(func):
    func.is_coroutine = True
    return func


def is_coroutine(func):
    return hasattr(func, 'is_coroutine')
