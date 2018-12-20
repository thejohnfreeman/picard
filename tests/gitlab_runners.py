"""A sample test to create two GitLab Runners in AWS."""

import picard
import picard.aws as aws

sg = aws.security_group('gitlab-runners', 'GitLab Runners')

if __name__ == '__main__':
    picard.main(sg)