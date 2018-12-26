"""Tests for general rules."""

import logging

import pytest # type: ignore

import picard

logging.basicConfig(level=logging.DEBUG)

@pytest.mark.asyncio
async def test_rule():
    """Test a basic rule."""
    # pylint: disable=unused-argument
    @picard.rule()
    async def target_1(self, context):
        return 1
    @picard.rule(target_1)
    async def target_2(self, context, one):
        return one + 1
    @picard.rule(two=target_2)
    async def target_3(self, context, *, two):
        return two + 1
    assert await picard.sync(target_3) == 3
