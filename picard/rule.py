"""Turn a named function into a state."""

import typing as t

from picard.context import Context
from picard.typing import State, StateLike

class RuleState(State):
    """A state built from a named function.

    A state is a combination of a name, a set of dependencies, and an (async)
    function. Because every async function in Python has a name, we just need
    to add a set of dependencies to an async function to build a state, which
    is much easier than defininig a class. :func:`rule` is a function
    decorator to do just that, and it constructs an instance of this class.
    """

    def __init__(self, name: str, inputs: t.Collection[StateLike], f) -> None:
        from picard.state import state # pylint: disable=cyclic-import
        self.name = name
        self.dependencies = [state(i) for i in inputs]
        self.f = f

    async def sync(self, context: Context):
        from picard.api import sync # pylint: disable=cyclic-import
        inputs = await sync(self.dependencies)
        context.log.info(f'start: {self.name}')
        value = await self.f(context, self.name, inputs)
        context.log.info(f'finish: {self.name}')
        return value


def rule(inputs=tuple()):
    """Turn a named function into a state.

    The basic principle of every rule is that it establishes a post-condition
    by the time it exits. It should return the same value whether it needs to
    "do work" or not, and such work should be performed conditionally on
    whether the post-condition was met before the rule was entered.

    Example
    -------
        from pathlib import Path

        @rule()
        async def gitdir():
            path = Path('.git')
            if not path.is_dir():
                picard.sh('git', 'init', '.')
            return path
    """
    def decorator(f: t.Callable[[Context, str, t.Iterable[t.Any]], t.Any]):
        return RuleState(f.__name__, inputs, f)
    return decorator