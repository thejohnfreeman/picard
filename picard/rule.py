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
        async def gitdir(self, context, prereqs):
            path = Path('.git')
            if not path.is_dir():
                picard.sh('git', 'init', '.')
            return path
    """
    # pylint: disable=unused-argument
    def decorator(recipe: Recipe):
        return PatternTarget(recipe.__name__, recipe, *args, **kwargs)
    return decorator
