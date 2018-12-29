"""Templates for rules, a la Make pattern rules."""

import functools
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

def pattern() -> t.Callable[[Recipe], t.Callable[..., Target]]:
    """Turn a recipe function into a target constructor.

    The constructor's parameters are the prerequisites, which will be passed,
    evaluated, to the recipe.

    Example
    -------

    .. code-block:: python

        import picard

        @picard.pattern()
        async def object_file(target, context, source):
            await picard.sh('gcc', '-c', source, '-o', target.name)

        hello_o = object_file('hello.o', 'hello.c')
        example_o = object_file('example.o', source='example.c')

    """
    def decorator(recipe):
        @_wraps(recipe)
        def constructor(name, *args, **kwargs):
            return PatternTarget(name, recipe, *args, **kwargs)
        return constructor
    return decorator

def _wraps(wrapped):
    """Like :func:`functools.wraps`, but do not set ``__wrapped__``.

    Because we change the type of the function, we do not want to set the
    ``__wrapped__`` attribute, which would give Sphinx autodoc the wrong
    impression.
    """
    def decorator(wrapper):
        for attr in functools.WRAPPER_ASSIGNMENTS:
            setattr(wrapper, attr, getattr(wrapped, attr))
        return wrapper
    return decorator
