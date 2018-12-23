"""Tests for general rules."""

import pytest # type: ignore

import picard

@pytest.mark.asyncio
async def test_rule():
    @picard.rule()
    async def target_1(self, context, prereqs):
        return 1
    @picard.rule((target_1,))
    async def target_2(self, context, prereqs):
        one, = prereqs
        return one + 1
    assert await picard.sync(target_2) == 2
