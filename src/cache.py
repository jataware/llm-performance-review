# from .path import Path, p, here
import atexit
from typing import Callable, TypeVar, ParamSpec, overload
import inspect
import platform
import json

from pathlib import Path

import pdb

def caller_here():
    # Get the frame of the caller of the function
    frame = inspect.currentframe()
    if frame is None:
        raise Exception('inspect.currentframe() returned None')
    # Move one frame back in the stack to get to the caller
    caller_frame = frame.f_back
    if caller_frame is None:
        raise Exception('frame.f_back returned None')
    # Retrieve the filename of the caller's frame
    caller_filename = caller_frame.f_globals['__file__']
    # Return the directory containing the file
    return Path(caller_filename).parent


def p(*args):
    return Path(*args)


R = TypeVar("R", covariant=True)
P = ParamSpec("P")


def freeze(obj):
    # if the object is hashable, return it as is
    try:
        hash(obj)
        return obj
    except TypeError:
        pass
    
    # convert known unhashable types to hashable types
    if isinstance(obj, dict):
        return tuple((freeze(k), freeze(v)) for k, v in sorted(obj.items()))
    elif isinstance(obj, (list, tuple)):
        return tuple(freeze(i) for i in obj)
    elif isinstance(obj, set):
        return frozenset(freeze(i) for i in obj)
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj  # already hashable
    else:
        raise TypeError(f"Unhashable and unfreezable type: ({type(obj)}): {obj}")



Serializable = dict | list | str | int | float | bool | None

identity = lambda x: x  # type: ignore

# TODO: diskcache should hash the function body and save it in the cache file, so it knows to invalidate the cache if the hash doesn't match
# TODO: also ideally diskcache could be more automatic about serialization e.g. it can probably figure it out in a lot of cases
@overload
def diskcache(func: Callable[P, R], /) -> Callable[P, R]: ...
@overload
def diskcache(
    *,
    serializer: Callable[[R], Serializable] = identity,
    deserializer: Callable[[Serializable], R] = identity,
    cache_path: Path | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...
def diskcache(func=None, /, *, serializer=identity, deserializer=identity, cache_path: Path|None = None):
    """
    decorator that acts like @cache, but stores the cache in a file on disk

    Saves the cache to a file on disk in the directory specified by cache_dir.

    Args:
        serializer (function): function that takes a value and returns a serializable object
        deserializer (function): function that takes a serializable object and returns the original value
        cache_path (Path): path to cache file. If not provided, path will be generated based on function name and signature

    Returns:
        function: the decorated function
    """
    # allow for decorator as @diskcache or @diskcache(options...)
    if func is not None:
        return diskcache(serializer=serializer, deserializer=deserializer, cache_path=cache_path)(func)

    def decorator(f: Callable[P, R]):
        nonlocal cache_path
        if cache_path is None:
            cache_path = caller_here() / make_filesafe_signature(f)

        # load the cache from the file
        cache: dict[P, R]
        try:
            lines = cache_path.read_text().splitlines()
            cache = {freeze((tuple(args), tuple(map(tuple, kwargs)))): deserializer(value)
                     for (args, kwargs), value in map(json.loads, lines)}
        except FileNotFoundError:
            # create an empty cache file
            cache_path.touch()
            cache = {}

        # open the cache file for appending, and ensure it closes on exit
        cache_file = open(cache_path, 'a')
        atexit.register(cache_file.close)

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = freeze((tuple(args), tuple(kwargs.items())))
            if key in cache:
                return cache[key]

            value = f(*args, **kwargs)
            cache[key] = value
            cache_file.write(json.dumps((key, serializer(value))) + '\n')

            return value

        return wrapper
    return decorator


def make_filesafe_signature(f:Callable[P, R]) -> str:
    """Generate a file-safe signature string for the function. More flexible on linux"""
    # determine if the OS is flexible with file names
    os = platform.system().lower()
    flexible_os = {'linux'}

    f_sig = str(inspect.signature(f))
    
    if os in flexible_os:
        # linux is pretty flexible with file names, so we can use mostly the original signature
        f_sig = f_sig.replace("/", "\\")
    
    else:
        # fallback to the safe signature generation for non-Linux systems
        f_sig = f_sig \
            .replace(' ', '')    \
            .replace(':', '.')   \
            .replace('->', '--') \
            .replace(',', '_')   \
            .replace('=', '-')

    return f'{p(f.__code__.co_filename).name}.cache.({f.__name__}{f_sig})'


if __name__ == '__main__':
    # silly example of using the diskcache decorator
    @diskcache
    def fib(n: int) -> int:
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)

    print(f'{fib(10)=}')
    print(f'{fib(12)=}')
    print(f'{fib(20)=}')
    print(f'{fib(30)=}')
    print(f'{fib(20)=}')
    print(f'{fib(30)=}')
