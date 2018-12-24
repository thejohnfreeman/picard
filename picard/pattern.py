"""Templates for rules, a la Make pattern rules.

A **pattern** is defined by supplying a recipe, and then it is instantiated to
make rules. Remember that each rule defines exactly one named target with
a recipe for building that target that only needs a :class:`picard.Context`.

The recipe given to a pattern definition may expect more than
a :class:`picard.Context`, however:

1. Its first parameter will be the :class:`Target` itself. A pattern does not
   yet define a target, so the recipe cannot know it until it is called.
2. Its second parameter will be the :class:`Context`.
3. The rest of its ``args`` and ``kwargs`` will be whatever was passed to the
   constructor, which may contain a mix of values and targets. By the time the
   recipe is called, all targets will be evaluated for it, so the recipe will
   only see values, not targets.

Once you have a pattern, you can use it to stamp out rules (a.k.a
:class:`Target`s). The constructor for these rules expects slightly different
parameters than the recipe you supplied for the pattern:

1. Its first parameter is the name of the target.
2. The rest of its ``args`` and ``kwargs`` can be whatever you want to pass
   through to the recipe. It can contain a mix of constant values and other
   targets, which will be evaluated before the recipe you supplied is called.

.. code-block:: python

    import picard

    @picard.pattern()
    async def object_file(target, context, source):
        context.log.info(f'compiling {source}...')
        await picard.sh('gcc', '-c', source, '-o', target.name)

    hello_o = object_file('hello.o', 'hello.c')
    example_o = object_file('example.o', source='example.c')
"""

import abc
import typing as t

from picard.context import Context
from picard.typing import Target

class AbstractPatternTarget(abc.ABC, Target):
    """An abstract pattern.

    Every pattern is a subclass of this class, which is only missing
    a :meth:`_recipe` method.
    """

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.prereqs = (args, kwargs)

    async def recipe(self, context: Context) -> t.Any:
        # TODO: Memoize value.
        from picard.api import sync # pylint: disable=cyclic-import
        args, kwargs = await sync(self.prereqs)
        context.log.info(f'start: {self.name}')
        value = await self._recipe(context, *args, **kwargs)
        context.log.info(f'finish: {self.name}')
        return value

    @abc.abstractmethod
    async def _recipe(self, context: Context, *args, **kwargs) -> t.Any:
        # pylint: disable=pointless-statement
        ...

_DEFAULT_DOCSTRING = """A template for rules, a.k.a. :class:`Target`s."""

def pattern():
    """Turn a recipe function into a pattern."""
    def decorator(recipe):
        class PatternTarget(AbstractPatternTarget):
            __doc__ = recipe.__doc__ or _DEFAULT_DOCSTRING
            _recipe = recipe
        return PatternTarget
    return decorator
