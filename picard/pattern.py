"""Templates for rules, a la Make pattern rules."""

import typing as t

from picard.context import Context
from picard.typing import Target

Recipe = t.Any

class PatternTarget(Target):
    """A template for rules, a.k.a. :class:`Target`s."""

    def __init__(self, name: str, recipe: Recipe, *args, **kwargs) -> None:
        self.name = name
        self.prereqs = (args, kwargs)
        self._recipe = recipe
        if recipe.__doc__:
            self.__doc__ = recipe.__doc__

    async def recipe(self, context: Context) -> t.Any:
        # TODO: Memoize value.
        from picard.api import sync # pylint: disable=cyclic-import
        args, kwargs = await sync(self.prereqs)
        context.log.info(f'start: {self.name}')
        value = await self._recipe(self, context, *args, **kwargs)
        context.log.info(f'finish: {self.name}')
        return value

def pattern():
    """Turn a recipe function into a pattern."""
    def decorator(recipe):
        def constructor(*args, **kwargs):
            return PatternTarget(recipe.__name__, recipe, *args, **kwargs)
        return constructor
    return decorator
