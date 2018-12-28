"""Turn a named function into a :class:`Target`."""

import typing as t

from picard.context import Context
from picard.pattern import PatternTarget
from picard.typing import Target

# Need a way to type *args and **kwargs without ignoring the known parameters.
Recipe = t.Callable[[Context, t.Any], t.Awaitable[t.Any]]

def rule(*args, **kwargs) -> t.Callable[[Recipe], Target]:
    """Turn a recipe function into a target.

    The parameters are the prerequisites, which will be passed, evaluated, to
    the recipe.

    Example
    -------

    .. code-block:: python

        from pathlib import Path
        import picard

        @picard.rule()
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
