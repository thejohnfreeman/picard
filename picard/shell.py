"""A shortcut for subprocesses."""

import asyncio

async def sh(*args, **kwargs):
    """Echo and execute a command.

    Parameters
    ----------
    *args :
        Command line arguments. ``None``s will be removed and the rest
        passed through ``str`` before execution.
    """
    args = tuple(str(a) for a in args if a is not None)
    print(' '.join(args))
    p = await asyncio.create_subprocess_exec(*args, **kwargs)
    await p.wait()
