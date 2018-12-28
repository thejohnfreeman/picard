"""Tests for file targets."""

import os

import pytest # type: ignore

import picard

async def _touch(
        target: picard.Target,
        context: picard.Context,
) -> None:
    # pylint: disable=unused-argument
    filename = target.name
    open(filename, 'a').close()
    os.utime(filename)

@pytest.mark.asyncio
async def test_file_returns_path(tmp_path):
    """File targets return their file's path."""
    path = tmp_path / 'output.txt'
    output = picard.file(path)(_touch)
    assert await picard.sync(output) == path

@pytest.mark.asyncio
async def test_raises_error_when_file_not_created(tmp_path):
    """File targets must update their file."""
    path = tmp_path / 'output.txt'
    @picard.file(path)
    async def output(self, context): # pylint: disable=unused-argument
        """This rule does not touch its target."""
    with pytest.raises(picard.FileRecipePostConditionError):
        await picard.sync(output)

@pytest.mark.asyncio
async def test_file_default_recipe_touches_output(tmp_path):
    """File targets have the post-condition that their file exists."""
    path = tmp_path / 'output.txt'
    output = picard.file(path)(_touch)
    await picard.sync(output)
    assert path.is_file()
