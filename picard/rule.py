"""Turn a named function into a :class:`Target`.

A target is a combination of a name, a set of prerequisites, and an (async)
recipe function. Because every async function in Python has a name, we just
need to add a set of prerequisites to make a rule, which we can do with
a decorator much easier than defininig a class. :func:`rule` is a function
decorator to do just that, and it constructs an instance of
:class:`RuleTarget`.
"""

import typing as t

from picard.context import Context
from picard.typing import Target

Recipe = t.Callable[[Context, Target, t.Iterable[t.Any]], t.Any]

class RuleTarget(Target):
    """A target built from a recipe function."""

    def __init__(
            self,
            name: str,
            prereqs: t.Collection[Target],
            recipe: Recipe) -> None:
        self.name = name
        self.prereqs = prereqs
        self._recipe = recipe

    async def recipe(self, context: Context):
        # TODO: Memoize value.
        from picard.api import sync # pylint: disable=cyclic-import
        prereqs = await sync(self.prereqs)
        context.log.info(f'start: {self.name}')
        value = await self._recipe(context, self, prereqs)
        context.log.info(f'finish:  {self.name}')
        return value

def rule(prereqs: t.Collection[Target] = tuple(), target=None):
    """Turn a recipe function into a rule.

    We call this decorator ``rule`` because it lets us build targets from
    recipe functions with a syntax that mimics Make.

    Parameters
    ----------
    prereqs :
        A set of prerequisite targets.
    target :
        A name for the target of this recipe. If ``None`` (the default), the
        name of the recipe function will be used.

    Example
    -------
        from pathlib import Path

        @rule()
        async def gitdir(context, self, prereqs):
            path = Path('.git')
            if not path.is_dir():
                picard.sh('git', 'init', '.')
            return path
    """
    # pylint: disable=unused-argument
    def decorator(function: Recipe):
        nonlocal target
        if target is None:
            target = function.__name__
        return RuleTarget(target, prereqs, function)
    return decorator
