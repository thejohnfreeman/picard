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
    async def security_group_rule(context, state, inputs):
        # pylint: disable=unused-argument
        client = boto3.client('ec2')
        response = client.describe_security_groups(GroupNames=[name])
        groups = response['SecurityGroups']
        if len(groups) > 1:
            # TODO: Set the description.
            raise Exception(f'more than one security group with name: {name}')
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
        # The group does not exist. We must create it.
        response = client.create_security_group(
            GroupName=name,
            Description=description)
        return ec2.SecurityGroup(response['GroupId'])
    return security_group_rule
