"""Construct a Target from a TargetLike."""

from picard.file import file
from picard.typing import Target, TargetLike

def target(value: TargetLike) -> Target:
    """Canonicalize a value to a :class:`Target`.

    If the value is already a :class:`Target`, it is returned as-is.
    If it is a :class:`str`, it is turned into a :class:`FileTarget`.

    Parameters
    ----------
    value :
        A value convertible to :class:`Target`.

    Returns
    -------
    Target
        A target.

    Raises
    ------
    Exception
        If :param:`value` is not a target.
    """
    if isinstance(value, Target):
        return value
    if isinstance(value, str):
        # Treat ``value`` as a filename.
        return file(value)()
    raise Exception(f'not a target: {value}')
