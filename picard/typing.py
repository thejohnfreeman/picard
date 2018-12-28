"""Types for mypy."""

import typing as t
import typing_extensions as tex

from picard.context import Context

# mypy does not yet support nested types, so we must use :class:`t.Any`.
# Prerequisites = t.Union['Target', t.Iterable['Prerequisites']]
Prerequisites = t.Any
"""An arbitrary traversable structure for target prerequisites.

The structure can be a single target, a (possibly empty) collection of
targets, or arbitrarily nested collections of targets. We just need a way to
walk the structure and pull out the targets buried within, which we have with
:func:`picard.functor.fmap`.
"""

@tex.runtime
class Target(tex.Protocol):
    """A protocol_ (i.e. structural type) for targets.

    .. protocol_: https://www.python.org/dev/peps/pep-0544/
    """
    name: str
    prereqs: Prerequisites
    async def recipe(self, context: Context) -> t.Any:
        # pylint: disable=unused-argument,pointless-statement
        ...
