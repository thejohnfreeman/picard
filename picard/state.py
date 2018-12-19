"""Construct a State from a StateLike."""

from picard.file import file
from picard.typing import State, StateLike

def state(arg: StateLike) -> State:
    """Canonicalize a value to a :class:`State`.

    If the value is already a :class:`State`, it is returned as-is.
    If it is a :class:`str`, it is turned into a :class:`FileState`.
    """
    if isinstance(arg, State):
        return arg
    if isinstance(arg, str):
        # Treat ``arg`` as a filename.
        return file(arg)()
    raise Exception(f'not a state: {arg}')
