import asyncio
import functools
import time
from contextlib import contextmanager


def fmt_arg(arg) -> str:
    t = type(arg)
    if t is list or t is tuple or t is set:
        arg = list(arg)
        if len(arg) == 0:
            return f"[]"
        elif len(arg) > 2:
            return f"[{arg[0]} ... {arg[-1]}]#{len(arg)}"
        else:
            return f"[{', '.join([a for a in arg])}"
    else:
        return str(arg)


def fmt_args(args, kwargs):
    s = []
    if len(args) > 0:
        s.append(', '.join([fmt_arg(arg) for arg in args]))
    if kwargs:
        s.append(', '.join(f"{k}={v}" for k, v in kwargs.items()))
    return ', '.join(s)


def duration(func):
    @contextmanager
    def wrapping_logic(*args, **kwargs):
        print('{}({}) started...'.format(func.__name__, fmt_args(args, kwargs)))
        start_ts = time.time()
        yield
        dur = time.time() - start_ts
        print('{}({}) took {} seconds'.format(func.__name__, fmt_args(args, kwargs), dur))

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            with wrapping_logic(*args, **kwargs):
                return func(*args, **kwargs)
        else:
            async def tmp():
                with wrapping_logic(*args, **kwargs):
                    return await func(*args, **kwargs)

            return tmp()

    return wrapper
