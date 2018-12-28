"""A sample test to create two GitLab Runners in AWS."""

import picard
import picard.aws as aws

# pylint: disable=no-value-for-parameter

sg = aws.security_group('gitlab-runners', description='GitLab Runners')
kp = aws.key_pair('gitlab-runners-key')

# We need to launch an instance, install software, and then save it as a new
# Amazon Machine Image, instead of trying to install software on every new
# instance. Do this out-of-band from the provisioning.

if __name__ == '__main__':
    picard.make(sg)
