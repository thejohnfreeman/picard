"""Make-style file states."""

import os
import typing as t

from picard.context import Context
from picard.rule import RuleState, RuleFunction
from picard.typing import State

class FileState(RuleState):
    """A file that must be newer than its input files."""

    async def sync(self, context: Context) -> str:
        """Conditionally re-generate this file.

        The conditions are (1) if this file does not exist or (2) if its
        inputs have changed since it was last touched.
        """
        # There is no way around evaluating all of the inputs. Either (1) we
        # must compute the output from the evaluated inputs or (2) we
        # must check all inputs to make sure none have changed since the
        # target was last touched.
        from picard.api import sync # pylint: disable=cyclic-import
        inputs = await sync(self.dependencies)
        if not await self._is_up_to_date(context, inputs):
            context.log.info(f'start: {self.name}')
            value = await self.function(context, self, inputs)
            if value is not None:
                context.log.warning(
                    f'discarding value returned by {self.function}: {value}')
            if not await self._is_up_to_date(context, inputs):
                context.log.warning(
                    f'rule failed to update target: {self.name}')
            context.log.info(f'finish: {self.name}')
        return self.name

    async def _is_up_to_date(
            self, context: Context, inputs: t.Iterable[t.Any]):
        try:
            mtime = os.stat(self.name).st_mtime
        except FileNotFoundError:
            return False

        for input_ in inputs:
            if not isinstance(input_, str):
                # Not a filename.
                context.log.warn(
                    f'skipping non-filename dependency: {input_}')
                continue
            if os.stat(input_).st_mtime > mtime:
                # Input has been modified after output.
                return False

        return True


async def _touch(
        context: Context, state: State, inputs: t.Iterable[t.Any]) -> None:
    # pylint: disable=unused-argument
    output = state.name
    open(output, 'a').close()
    os.utime(output)


def file(output: str, inputs=tuple()):
    """A file that is younger than its input files."""
    # pylint: disable=unused-argument
    # We need the default to be touch so that the timestamp is updated.
    def decorator(function: RuleFunction = _touch):
        return FileState(output, inputs, function)
    return decorator
