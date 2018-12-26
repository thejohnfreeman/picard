"""Recursive synchronous fmap for Python."""

import itertools
import typing as t
import typing_extensions as tex

@tex.runtime
class Functor(tex.Protocol):
    """A user-defined functor with a synchronous fmap."""
    def _fmap_(self, function) -> 'Functor':
        # pylint: disable=no-self-use,unused-argument,pointless-statement
        ...


def _fmap_str(function, string):
    return ''.join(map(function, string))

def _fmap_generator(function, xs):
    for x in xs:
        yield fmap(function, x)

def _fmap_iterable(function, iterable):
    return type(iterable)(fmap(function, x) for x in iterable)

def _fmap_mapping(function, mapping):
    values = _fmap_generator(function, mapping.values())
    kvs = itertools.zip_longest(mapping.keys(), values)
    return type(mapping)(kvs)

# Only ``str`` and ``range`` need to be here because they do not fit nicely
# into the protocol branches, but we include the rest of the built-in types
# here anyways as an optimization (because known types are checked first).
_IMPLEMENTATIONS = {
    bytes: _fmap_iterable,
    dict: _fmap_mapping,
    frozenset: _fmap_iterable,
    list: _fmap_iterable,
    range: _fmap_generator,
    set: _fmap_iterable,
    str: _fmap_str,
    tuple: _fmap_iterable,
}

_NO_ARGUMENT = object()

def fmap(function: t.Callable, functor=_NO_ARGUMENT):
    """Recursively apply a function within a functor.

    By "recursive", we mean if a functor is nested, even with different types,
    e.g. a list of dicts, then :func:`fmap` will recurse into each level and
    apply :param:`function` at the "leaf" values.

    Parameters
    ----------
    function :
        A function to apply to the values within :param:`functor`. It must be
        able to handle any type found within :param:`functor`.
    functor :
        A functor. Known functors include lists, dicts, and other collections.
        User-defined functors with an ``_fmap_`` method will be recognized.

    Returns
    -------
    Functor
        A copy of :param:`functor` with the results of applying
        :param:`function` to all of its leaf values.
    """
    # pylint: disable=too-many-return-statements
    # Currying:
    if functor is _NO_ARGUMENT:
        return lambda functor: fmap(function, functor)
    # 1. If the functor is a known type:
    impl = _IMPLEMENTATIONS.get(type(functor), None)
    if impl is not None:
        return impl(function, functor)
    # 2. If it is a Functor:
    if isinstance(functor, Functor):
        return functor._fmap_(function) # pylint: disable=protected-access
    # 3. If it is a Mapping:
    if isinstance(functor, t.Mapping):
        return _fmap_mapping(function, functor)
    # 4. If it is an Iterator:
    if isinstance(functor, t.Iterator):
        return _fmap_generator(function, functor)
    # 5. If it is an Iterable:
    if isinstance(functor, t.Iterable):
        return _fmap_iterable(function, functor)
    # Assume it is the identity functor.
    return function(functor)
