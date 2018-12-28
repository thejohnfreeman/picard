"""Patterns for Amazon Web Services resources.

The patterns in this module correspond to AWS resources, e.g. an EC2 instance
or an S3 bucket. That is, their post-condition asserts that the resource
exists with the given parameters. Each target requires *at least* the
parameters necessary to create the resource. These parameters should be enough
to identify the resource in a search.
"""

import boto3 # type: ignore

from picard.context import Context
from picard.pattern import pattern

@pattern()
async def security_group(self, context: Context, description: str = ''):
    """An AWS security group."""
    name = self.name

    # Search for the security group by name.
    client = boto3.client('ec2')
    response = client.describe_security_groups(GroupNames=[name])
    groups = response['SecurityGroups']

    # More than one? Ambiguous.
    if len(groups) > 1:
        # TODO: Set the description.
        raise Exception(f'ambiguous security group name: {name}')

    # None? We must create it.
    ec2 = boto3.resource('ec2')
    if not groups:
        response = client.create_security_group(
            GroupName=name,
            Description=description)
        return ec2.SecurityGroup(response['GroupId'])

    # Exactly one? Check for differences, then return it.
    assert len(groups) == 1
    group = groups[0]
    gid = group['GroupId']
    actual = group['Description']
    if actual != description:
        context.log.warning(
            f'description for security group {name} '
            f'(#{gid}) does not match:\n'
            f'expected: {description}\n'
            f'actual: {actual}'
        )
    return ec2.SecurityGroup(gid)

@pattern()
async def key_pair(self, context: Context):
    """An AWS key pair."""
    # pylint: disable=unused-argument
    name = self.name

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
