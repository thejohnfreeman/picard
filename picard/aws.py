"""Patterns for Amazon Web Services resources.

The patterns in this module correspond to AWS resources, e.g. an EC2 instance
or an S3 bucket. That is, their post-condition asserts that the resource
exists with the given parameters. Each target requires *at least* the
parameters necessary to create the resource. These parameters should be enough
to identify the resource in a search.

.. note:: All parameters for these patterns must be keyword arguments.
"""

import typing as t

import boto3 # type: ignore
# Types coming soon: https://github.com/python/typeshed/pull/2384
from tabulate import tabulate # type: ignore

from picard.context import Context
from picard.pattern import pattern
from picard.typing import Target

@pattern()
async def security_group(target: Target, context: Context, **kwargs):
    """An AWS security group.

    Parameters
    ----------
    Description : str
    """
    # pylint: disable=unused-argument
    name = target.name

    # Search for the security group by name.
    client = boto3.client('ec2')
    response = client.describe_security_groups(GroupNames=[name])
    groups = response['SecurityGroups']

    # More than one? Ambiguous.
    if len(groups) > 1:
        raise Exception(f'ambiguous security group name: {name}')

    # None? We must create it.
    ec2 = boto3.resource('ec2')
    if not groups:
        response = client.create_security_group(GroupName=name, **kwargs)
        return ec2.SecurityGroup(response['GroupId'])

    # Exactly one? Check for differences, then return it.
    assert len(groups) == 1
    group = groups[0]
    gid = group['GroupId']
    diffs = {
        key: (expected, actual)
        for key, expected in kwargs.items()
        for actual in (group[key],)
        if actual != expected
    }
    if diffs:
        raise DifferenceError('Security Group', gid, diffs)
    return ec2.SecurityGroup(gid)

class DifferenceError(Exception):
    """An exception for unexpected differences."""

    def __init__(
            self,
            type_: str,
            id_: str,
            diffs: t.Mapping[str, t.Tuple[t.Any, t.Any]],
    ) -> None:
        super().__init__()
        self.type = type_
        self.id = id_
        self.diffs = diffs

    def __str__(self) -> str:
        rows = [
            (key, repr(expected), repr(actual))
            for key, (expected, actual) in self.diffs.items()
        ]
        table = tabulate(rows, headers=('Value', 'Expected', 'Actual'))
        return f'{self.type} #{self.id}\n{table}'

@pattern()
async def key_pair(target: Target, context: Context):
    """An AWS key pair."""
    # pylint: disable=unused-argument
    name = target.name

    # Search for the key pair by name.
    client = boto3.client('ec2')
    response = client.describe_key_pairs(KeyNames=[name])
    key_pairs = response['KeyPairs']

    # More than one? Ambiguous.
    if len(key_pairs) > 1:
        raise Exception(f'ambiguous key pair name: {name}')

    # None? We must create it.
    ec2 = boto3.resource('ec2')
    if not key_pairs:
        response = client.create_key_pair(KeyName=name)
        return ec2.KeyPair(name)
        # Can we get the key material *after* the key has been created?

    # Exactly one? Return it.
    assert len(key_pairs) == 1
    return ec2.KeyPair(name)

@pattern()
async def instance(self, context: Context): # pylint: disable=unused-argument
    """An AWS instance."""
    # Search for instance by name (kept in a tag).
    # Careful to filter for non-terminated instance.
    # Use the tag "Name". It shows up in the dashboard on amazon.com.
    # If more than zero instances with name, count how many have the right
    # configuration. If too many, stop the excess and the non-matching
    # instances. If too few, change the non-matching to match, then stop
    # the rest if we have enough, or start more if not.
    # If zero instances with name, start them, with tags.
