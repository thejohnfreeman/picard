"""The rest of the public API."""

import asyncio
import inspect
import logging
import os
import typing as t

from picard.afunctor import afmap
from picard.argparse import parse_args
from picard.context import Context
from picard.typing import Target

# Targets = Traversable[Target]
Targets = t.Any

async def sync(target: Targets, context: Context = None):
    """Swiss-army function to synchronize one or more targets.

    Parameters
    ----------
    targets :
        One or more targets. This function will recurse into functors like
        sequences and mappings. (Remember that mappings are functors over
        their values, not their keys.)
    context :
        An optional context. If ``None`` is passed (the default), one will be
        created for you.

    Returns
    -------
    The value(s) of the targets.
    """
    if context is None:
        context = Context()
    async def _sync(value):
        if isinstance(value, Target):
            return await value.recipe(context)
        return value
    return await afmap(_sync, target)

def make(
        target: Targets,
        config: t.Mapping[str, t.Any] = None,
        rules: t.Mapping[str, Target] = None,
):
    """Parse targets from the command line."""
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    if rules is None:
        stack = inspect.stack()
        module = inspect.getmodule(stack[0].frame)
        if module is None:
            raise NotImplementedError(
                'cannot get module of caller; '
                'you must pass the "rules" argument')
        rules = vars(module)

    targets, overrides = parse_args()

    targets_ = (
        [target]
        if not targets else
        [rules[t] for t in targets]
    )

    config = {} if config is None else dict(config)
    config.update(os.environ)
    config.update(overrides)
    context = Context(config=config)

    return _run(sync(targets_, context))

def _run(awaitable):
    """A shim for :func:`asyncio.run` from 3.7+."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)
