"""Batteries for Amazon Web Services.

The states in this module correspond to AWS resources, e.g. an EC2 instance or
an S3 bucket. That is, their post-condition asserts that the resource exists
with the given parameters. Each state is requires *at least* the parameters
necessary to create the resource. These parameters should be enough to
identify the resource in a search.
"""

import boto3 # type: ignore

from picard.abc import AbstractState, log_to_context
from picard.context import Context

class SecurityGroupState(AbstractState):
    """An AWS security group."""

    def __init__(self, name: str, description=''):
        super().__init__(name)
        self.description = description

    @log_to_context()
    async def sync(self, context: Context):
        name = self.name
        description = self.description

        # Search for the security group by name.
        client = boto3.client('ec2')
        response = client.describe_security_groups(GroupNames=[name])
        groups = response['SecurityGroups']

        # More than one? Ambiguous.
        if len(groups) > 1:
            # TODO: Set the description.
            raise Exception(f'ambiguous security group name: {name}')

        # Exactly one? Check for differences, then return it.
        ec2 = boto3.resource('ec2')
        if len(groups) == 1:
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

        # None? We must create it.
        response = client.create_security_group(
            GroupName=name,
            Description=description)
        return ec2.SecurityGroup(response['GroupId'])


security_group = SecurityGroupState


class KeyPairState(AbstractState):
    """An AWS key pair."""

    @log_to_context()
    async def sync(self, context: Context):
        # pylint: disable=unused-argument
        name = self.name

        # Search for the key pair by name.
        client = boto3.client('ec2')
        response = client.describe_key_pairs(KeyNames=[name])
        key_pairs = response['KeyPairs']

        # More than one? Ambiguous.
        if len(key_pairs) > 1:
            raise Exception(f'ambiguous key pair name: {name}')

        # Exactly one? Return it.
        ec2 = boto3.resource('ec2')
        if len(key_pairs) == 1:
            return ec2.KeyPair(name)

        # None? We must create it.
        response = client.create_key_pair(KeyName=name)
        return ec2.KeyPair(name)
        # Can we get the key material *after* the key has been created?


key_pair = KeyPairState
