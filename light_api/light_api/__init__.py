import functools
from .client import Light


def with_light(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with Light() as light:
            return f(light, *args, **kwargs)
    return wrapper
