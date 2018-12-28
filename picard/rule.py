"""Turn a named function into a :class:`Target`."""

import typing as t

from picard.context import Context
from picard.pattern import PatternTarget
from picard.typing import Target

Recipe = t.Callable[[Target, Context, t.Any], t.Any]

def rule(*args, **kwargs):
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
        async def gitdir(context):
            path = Path('.git')
            if not path.is_dir():
                picard.sh('git', 'init', '.')
            return path
    """
    # pylint: disable=unused-argument
    def decorator(recipe: Recipe):
        async def selfless_recipe(self, context, *args, **kwargs):
            return await recipe(context, *args, **kwargs)
        return PatternTarget(recipe.__name__, selfless_recipe, *args, **kwargs)
    return decorator
