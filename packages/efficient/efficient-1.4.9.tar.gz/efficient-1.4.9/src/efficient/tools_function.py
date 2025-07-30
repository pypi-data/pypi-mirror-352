from time import time_ns


def call_timer(func):
    def wrapper(*args, **kwargs):
        t = time_ns()
        r = func(*args, **kwargs)
        print(func.__name__, '执行用时', (time_ns() - t) / 1000000000, f"{func.__code__.co_filename}, line {func.__code__.co_firstlineno + 1}")
        return r

    return wrapper
