"""An abstract base state class."""

import abc
import functools
import typing as t

from picard.context import Context
from picard.typing import State, StateLike

T = t.TypeVar('T', covariant=True)


class AbstractState(abc.ABC, State[T]):
    """An abstract state."""

    def __init__(
            self, name: str, inputs: t.Collection[StateLike] = tuple()):
        from picard.state import state # pylint: disable=cyclic-import
        self.name = name
        self.dependencies = [state(i) for i in inputs]

    @abc.abstractmethod
    async def sync(self, context: Context) -> T:
        raise NotImplementedError()


def log_to_context():
    """Log to the context when entering and exiting a sync function."""
    def decorator(function):
        @functools.wraps(function)
        async def sync(self, context: Context, *args, **kwargs):
            context.log.info(f'start: {self.name}')
            value = await function(self, context, *args, **kwargs)
            context.log.info(f'finish: {self.name}')
            return value
        return sync
    return decorator
