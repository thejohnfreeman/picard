"""The rest of the public API."""

import argparse
import asyncio
import inspect
import logging
import typing as t

from picard.context import Context
from picard.target import target
from picard.typing import TargetLike

async def sync(
        targets: t.Union[TargetLike, t.Iterable[TargetLike]],
        context: t.Union[Context, None] = None):
    """Swiss-army function to synchronize one or more targets.

    Parameters
    ----------
    targets :
        One or more targets.
    context :
        An optional context. If ``None`` is passed (the default), one will be
        created for you.

    Returns
    -------
    The value(s) of the targets.
    """
    if context is None:
        context = Context()
    if isinstance(targets, t.Iterable):
        return await asyncio.gather(
            *(target(t).recipe(context) for t in targets))
    return await target(targets).recipe(context)


def main(default, rules=None):
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
    asyncio.run(sync(targets, context))
