"""A shortcut for subprocesses."""

import asyncio

async def sh(*args, **kwargs):
    p = await asyncio.create_subprocess_exec(*args, **kwargs)
    await p.wait()
