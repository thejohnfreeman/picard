"""An abstract base target class."""

import abc
import typing as t

from picard.context import Context
from picard.typing import Target, TargetLike

class AbstractTarget(abc.ABC, Target):
    """An abstract target."""

    def __init__(
            self, name: str, prereqs: t.Collection[TargetLike] = tuple()):
        from picard.target import target # pylint: disable=cyclic-import
        self.name = name
        self.prereqs = [target(p) for p in prereqs]

    async def recipe(self, context: Context):
        """Build the target from its prerequisites."""
        # This implementation logs its entry and exit and memoizes its result.
        # TODO: Memoize result.
        context.log.info(f'start: {self.name}')
        value = await self._recipe(context)
        context.log.info(f'finish: {self.name}')
        return value

    @abc.abstractmethod
    async def _recipe(self, context: Context):
        # pylint: disable=unused-argument,pointless-statement
        ...
