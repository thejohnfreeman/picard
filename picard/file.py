"""Make-style file targets."""

import os
import typing as t

from picard.context import Context
from picard.rule import Recipe
from picard.typing import Target

FileTargetLike = t.Union[Target, str]

class FileTarget(Target):
    """A file that must be newer than its prerequisite files."""

    def __init__(
            self,
            name: str,
            prereqs: t.Collection[FileTargetLike],
            recipe: Recipe) -> None:
        self.name = name
        self.prereqs = [file_target(p) for p in prereqs]
        self._recipe = recipe

    async def recipe(self, context: Context) -> str:
        """Conditionally rebuild this file.

        The conditions are (1) if this file does not exist or (2) if its
        prerequisites have changed since it was last touched.
        """
        # There is no way around evaluating all of the prerequisites. Either
        # (1) some have changed but we must feed them all to the recipe or (2)
        # we must check all of them to make sure none have changed.
        from picard.api import sync # pylint: disable=cyclic-import
        prereqs = await sync(self.prereqs)
        if not await self._is_up_to_date(context, prereqs):
            context.log.info(f'start: {self.name}')
            value = await self._recipe(context, self, prereqs)
            if value is not None:
                context.log.warning(
                    f'discarding value returned by {self._recipe}: {value}')
            if not await self._is_up_to_date(context, prereqs):
                context.log.warning(
                    f'rule failed to update target: {self.name}')
            context.log.info(f'finish: {self.name}')
        return self.name

    async def _is_up_to_date(
            self, context: Context, prereqs: t.Iterable[t.Any]):
        try:
            mtime = os.stat(self.name).st_mtime
        except FileNotFoundError:
            return False

        for prereq in prereqs:
            if not isinstance(prereq, str):
                # Not a filename.
                context.log.warn(
                    f'skipping non-filename dependency: {prereq}')
                continue
            if os.stat(prereq).st_mtime > mtime:
                # Prerequisite has been modified after target.
                return False

        return True

def file_target(value: FileTargetLike) -> Target:
    """Canonicalize a value to a :class:`Target`.

    If the value is already a :class:`Target`, it is returned as-is.
    If it is a :class:`str`, it is returned as a :class:`FileTarget`.

    Parameters
    ----------
    value :
        A value convertible to :class:`Target`.

    Returns
    -------
    Target
        A target.

    Raises
    ------
    Exception
        If :param:`value` is not convertible to a target.
    """
    if isinstance(value, Target):
        return value
    if isinstance(value, str):
        # Treat ``value`` as a filename.
        return file(value)()
    raise Exception(f'not a target: {value}')

async def _touch(
        context: Context, target: Target, prereqs: t.Iterable[t.Any]) -> None:
    # pylint: disable=unused-argument
    filename = target.name
    open(filename, 'a').close()
    os.utime(filename)

def file(target: str, prereqs: t.Collection[FileTargetLike] = tuple()):
    """A file that is newer than its prerequisite files."""
    # pylint: disable=unused-argument
    # We need the default to be touch so that the timestamp is updated.
    def decorator(recipe: Recipe = _touch):
        return FileTarget(target, prereqs, recipe)
    return decorator
