"""Batteries for Amazon Web Services.

The states in this module correspond to AWS resources, e.g. an EC2 instance or
an S3 bucket. That is, their post-condition asserts that the resource exists
with the given parameters. Each state is requires *at least* the parameters
necessary to create the resource. These parameters should be enough to
identify the resource in a search.
"""

import boto3 # type: ignore

from picard.rule import rule

def security_group(name, description=''):
    """An AWS security group."""

    @rule(name=name)
    async def security_group(context, self, inputs):
        # pylint: disable=unused-argument

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

    return security_group


def key_pair(name):
    """An AWS key pair.

    Parameters
    ----------
    name :
        A name for the key pair.
    """

    @rule(name=name)
    async def key_pair(context, self, inputs):
        # pylint: disable=unused-argument

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

    return key_pair
