"""Recursive asynchronous fmap for Python."""

import asyncio
import itertools
import typing as t
import typing_extensions as tex

@tex.runtime
class AsyncFunctor(tex.Protocol):
    """A user-defined functor with an asynchronous fmap.

    The sad state of async programming in Python dictates that we have two
    implementations of everything.
    """
    async def _afmap_(self, function) -> 'AsyncFunctor':
        # pylint: disable=no-self-use,unused-argument,pointless-statement
        ...


async def _afmap_str(function, string):
    ss = await asyncio.gather(*map(function, string))
    return ''.join(ss)

async def _afmap_generator(function, xs):
    # These type specializations are awaited unconditionally in :func:`afmap`.
    # If this function itself were a generator, it could not be awaited.
    # Instead, it must return an awaitable that returns an async generator.
    # Gross.
    async def generator():
        for x in xs:
            yield await afmap(function, x)
    return generator()

async def _afmap_iterable(function, iterable):
    ys = await asyncio.gather(*(function(x) for x in iterable))
    return type(iterable)(ys)

async def _afmap_mapping(function, mapping):
    async def curried(functor):
        return await afmap(function, functor)
    values = await asyncio.gather(*map(curried, mapping.values()))
    kvs = itertools.zip_longest(mapping.keys(), values)
    return type(mapping)(kvs)

# Only ``str`` and ``range`` need to be here because they do not fit nicely
# into the protocol branches, but we include the rest of the built-in types
# here anyways as an optimization (because known types are checked first).
_IMPLEMENTATIONS = {
    bytes: _afmap_iterable,
    dict: _afmap_mapping,
    frozenset: _afmap_iterable,
    list: _afmap_iterable,
    range: _afmap_generator,
    set: _afmap_iterable,
    str: _afmap_str,
    tuple: _afmap_iterable,
}

_NO_ARGUMENT = object()

async def afmap(function: t.Callable, functor=_NO_ARGUMENT):
    """Recursively apply an asynchronous function within a functor.

    By "recursive", we mean if a functor is nested, even with different types,
    e.g. a list of dicts, then :func:`afmap` will recurse into each level and
    apply :param:`function` at the "leaf" values.

    Calls of the function will be evaluated concurrently, thus there is no
    guaranteed order of execution (you want a monad for that).

    Parameters
    ----------
    function :
        A function to apply to the values within :param:`functor`. It must be
        able to handle any type found within :param:`functor`.
    functor :
        A functor. Known functors include lists, dicts, and other collections.
        User-defined functors with an ``_afmap_`` method will be recognized.

    Returns
    -------
    AsyncFunctor
        A copy of :param:`functor` with the results of applying
        :param:`function` to all of its leaf values.
    """
    # pylint: disable=too-many-return-statements
    # Currying async functions is inconvenient and slow. We don't do it.
    # 1. If the functor is a known type:
    impl = _IMPLEMENTATIONS.get(type(functor), None)
    if impl is not None:
        return await impl(function, functor)
    # 2. If it is an AsyncFunctor:
    if isinstance(functor, AsyncFunctor):
        return await functor._afmap_(function) # pylint: disable=protected-access
    # 3. If it is a Mapping:
    if isinstance(functor, t.Mapping):
        return await _afmap_mapping(function, functor)
    # 4. If it is an Iterator:
    if isinstance(functor, t.Iterator):
        return _afmap_generator(function, functor)
    # 5. If it is an Iterable:
    if isinstance(functor, t.Iterable):
        return await _afmap_iterable(function, functor)
    # Assume it is the identity functor.
    return await function(functor)
