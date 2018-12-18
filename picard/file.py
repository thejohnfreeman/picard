"""Make-style file states."""

import typing as t

from picard.context import Context
from picard.typing import State, StateLike

class FileState(State):
    """A file that must have a timestamp newer than its input files."""

    def __init__(self, name: str, inputs: t.Collection[StateLike], f) -> None:
        from picard.state import state # pylint: disable=cyclic-import
        self.name = name
        self.dependencies = [state(i) for i in inputs]
        self.f = f

    async def sync(self, context: Context) -> str:
        """Conditionally re-generate this file.

        The conditions are (1) if this file does not exist or (2) if its
        inputs have changed.
        """
        from picard.api import sync # pylint: disable=cyclic-import
        inputs = await sync(self.dependencies)
        # TODO: Check timestamps.
        context.log.info(f'start: {self.name}')
        await self.f(context, inputs)
        context.log.info(f'finish: {self.name}')
        return self.name


def file(output: str, inputs=tuple()):
    """A file that is younger than its input files."""
    # pylint: disable=unused-argument
    def decorator(f):
        return FileState(output, inputs, f)
    return decorator
