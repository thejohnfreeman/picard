"""Tests for file targets."""

import pytest # type: ignore

import picard

@pytest.mark.asyncio
async def test_file_returns_path(tmp_path):
    """File targets return their file's path."""
    path = tmp_path / 'output.txt'
    output = picard.file(path)()
    assert await picard.sync(output) == path

@pytest.mark.asyncio
async def test_raises_error_when_file_not_created(tmp_path):
    """File targets must update their file."""
    path = tmp_path / 'output.txt'
    @picard.file(path)
    async def output(self, context, prereqs): # pylint: disable=unused-argument
        """This rule does not touch its target."""
    with pytest.raises(picard.FileRecipePostConditionError):
        await picard.sync(output)

@pytest.mark.asyncio
async def test_file_default_recipe_touches_output(tmp_path):
    """File targets have the post-condition that their file exists."""
    path = tmp_path / 'output.txt'
    output = picard.file(path)()
    await picard.sync(output)
    assert path.is_file()
