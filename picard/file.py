"""Make-style file (and directory) targets."""

import os
from pathlib import Path
import typing as t

from picard.context import Context
from picard.rule import Recipe
from picard.typing import Target

FileLike = t.Union[str, os.PathLike]
FileTargetLike = t.Union[Target, FileLike]

def is_file_like(value):
    # For now, ``isinstance`` does not play well with ``typing.Union``.
    # https://stackoverflow.com/a/45959000/618906
    return isinstance(value, (str, os.PathLike))

class FileRecipePostConditionError(Exception):
    """Raised when a file recipe fails to update its target."""

class FileTarget(Target):
    """A file that must be newer than its prerequisite files."""

    def __init__(
            self, path: Path, recipe: Recipe, *prereqs: FileTargetLike,
    ) -> None:
        self.path = path
        self.prereqs = [file_target(p) for p in prereqs]
        self._recipe = recipe

    @property
    def name(self) -> str: # type: ignore
        return str(self.path)

    async def recipe(self, context: Context) -> Path:
        """Conditionally rebuild this file.

        The conditions are (1) if this file does not exist or (2) if its
        prerequisites have changed since it was last touched.
        """
        # TODO: Memoize value.
        # There is no way around evaluating all of the prerequisites. Either
        # (1) some have changed but we must feed them all to the recipe or (2)
        # we must check all of them to make sure none have changed.
        from picard.api import sync # pylint: disable=cyclic-import
        prereqs = await sync(self.prereqs)
        if not await self._is_up_to_date(context, prereqs):
            context.log.info(f'start: {self.name}')
            value = await self._recipe(self, context, *prereqs)
            if value is not None and value != self.path:
                context.log.warning(
                    f'discarding value returned by {self._recipe}: {value}')
            if not await self._is_up_to_date(context, prereqs):
                raise FileRecipePostConditionError(self.name)
            context.log.info(f'finish: {self.name}')
        return self.path

    async def _is_up_to_date(
            self, context: Context, prereqs: t.Iterable[t.Any]
    ) -> bool:
        try:
            mtime = os.stat(self.name).st_mtime
        except FileNotFoundError:
            return False

        for prereq in prereqs:
            if not is_file_like(prereq):
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
    if is_file_like(value):
        # Treat ``value`` as a filename.
        return file(value)()
    raise Exception(f'not a target: {value}')

async def _touch(target: Target, context: Context, *prereqs) -> None:
    # pylint: disable=unused-argument
    filename = target.name
    open(filename, 'a').close()
    os.utime(filename)

def file(target: FileLike, *prereqs: FileTargetLike):
    """A file that is newer than its prerequisite files."""
    # pylint: disable=unused-argument
    # We need the default to be touch so that the timestamp is updated.
    def decorator(recipe: Recipe = _touch):
        return FileTarget(Path(target), recipe, *prereqs)
    return decorator
