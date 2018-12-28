"""The rest of the public API."""

import argparse
import asyncio
import inspect
import logging
import typing as t

from picard.afunctor import afmap
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

def main(default: Targets, rules: t.Mapping[str, Target] = None):
    """Parse targets from the command line."""
    if rules is None:
        stack = inspect.stack()
        module = inspect.getmodule(stack[0].frame)
        if module is None:
            raise NotImplementedError(
                'cannot get module of caller; '
                'you must pass the "rules" argument')
        rules = vars(module)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('targets', nargs='*')
    args = parser.parse_args()

    targets = (
        [default]
        if args.targets == [] else
        [rules[t] for t in args.targets]
    )

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    # TODO: Build configuration.
    context = Context()
    return _run(sync(targets, context))

def _run(awaitable):
    """A shim for :func:`asyncio.run` from 3.7+."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)
