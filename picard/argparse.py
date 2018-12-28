"""A Pythonic command line parser."""

import re
import sys
import typing as t

def parse_args(argv: t.Iterable[str] = None):
    """Parse a command line into positional and keyword arguments.

    Parameters
    ----------
    argv :
        A command line, like :obj:`sys.argv`.

    Returns
    -------
    (tuple, dict)
        A tuple of positional and keyword arguments.

    Examples
    --------

    >>> parse_args([])
    ((), {})
    >>> parse_args(['a'])
    (('a',), {})
    >>> parse_args(['a', 'b'])
    (('a', 'b'), {})
    >>> parse_args(['--name', 'value'])
    ((), {'name': 'value'})
    >>> parse_args(['name=value'])
    ((), {'name': 'value'})
    >>> parse_args(['a', 'b', '--name', 'value'])
    (('a', 'b'), {'name': 'value'})
    >>> parse_args(['a', '--name', 'value', 'b'])
    (('a', 'b'), {'name': 'value'})
    >>> parse_args(['--name', 'value', 'a', 'b'])
    (('a', 'b'), {'name': 'value'})
    """
    if argv is None:
        argv = sys.argv[1:]

    args: t.List[str] = []
    kwargs: t.MutableMapping[str, t.Any] = {}

    key = None
    for arg in argv:
        if arg.startswith('--'):
            if arg == '--help':
                print(USAGE)
                raise SystemExit
            if key is not None:
                kwargs[key] = True
            key = arg[2:]
            continue

        match = re.match('^(\\w+)=(.*)$', arg)
        if match:
            if key is not None:
                kwargs[key] = True
                key = None
            kwargs[match.group(1)] = match.group(2)
            continue

        if key is not None:
            kwargs[key] = arg
            key = None
            continue

        args.append(arg)

    if key is not None:
        kwargs[key] = True

    return (tuple(args), kwargs)

USAGE = f'{sys.argv[0]} [options] [targets]'
