"""Tests for file states."""

import asyncio

import picard

@picard.file('output.txt')
async def output(context, self, inputs):
    # pylint: disable=unused-argument
    pass


def test_file_returns_filename():
    assert asyncio.run(picard.sync(output)) == 'output.txt'
