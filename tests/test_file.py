"""Tests for file states."""

import picard


@picard.file('output.txt')
async def output(context, inputs):
    # pylint: disable=unused-argument
    pass


def test_file_returns_filename():
    assert picard.get(output) == 'output.txt'
