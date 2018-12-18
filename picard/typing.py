"""Types for mypy."""

import typing as t
import typing_extensions as tex

from picard.context import Context


T = t.TypeVar('T', covariant=True)


@tex.runtime
class State(t.Generic[T], tex.Protocol):
    """A protocol for states.

    A state has:

    - A human-readable name for debugging.
    - A (possibly empty) set of dependency states. Capturing them gives us
      a representation of the graph that we can use for debugging.
    - A value (output) that is computed as a function of the dependencies
      (inputs).
    """
    name: str

    dependencies: t.Collection['State[t.Any]']

    async def sync(self, context: Context) -> T:
        raise NotImplementedError()


StateLike = t.Union[State, str]
