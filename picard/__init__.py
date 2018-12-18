"""Picard combines the idea of Ansible with the execution of Make."""

import asyncio
import typing as t
import typing_extensions as tex


T = t.TypeVar('T', covariant=True)


StateLike = t.Union['State', str]


class Context:
    """For now, this is just a placeholder."""
    # TODO: Logging.

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

    async def get(self, context: Context) -> T:
        raise NotImplementedError()


def state(arg):
    """Canonicalize a value to a :class:`State`.

    If the value is already a :class:`State`, it is returned as-is.
    If it is a :class:`str`, it is turned into a :class:`FileState`.
    """
    if isinstance(arg, State):
        return arg
    if isinstance(arg, str):
        # Treat ``arg`` as a filename.
        async def touch(context, inputs):
            # pylint: disable=unused-argument
            pass
        return file(arg)(touch)
    raise Exception(f'not a state: {arg}')


class FileState(State):
    """A file that must have a timestamp newer than its input files."""

    def __init__(self, name, inputs, f):
        self.name = name
        self.dependencies = [state(i) for i in inputs]
        self.f = f

    async def get(self, context: Context) -> str:
        inputs = await asyncio.gather(*self.dependencies)
        # TODO: Check timestamps.
        await self.f(context, inputs)
        return self.name


def file(output: str, inputs=tuple()):
    """A file that is younger than its input files."""
    # pylint: disable=unused-argument
    def decorator(f):
        return FileState(output, inputs, f)
    return decorator


def get(state):
    context = Context()
    return asyncio.run(state.get(context))


def main():
    """Parse targets from the command line."""
