# WARNING: DO NOT USE THIS.
# This setup.py exists only to satisfy Read the Docs until they can support
# pyproject.toml (PEP 517):
# https://github.com/rtfd/readthedocs.org/issues/4912#issuecomment-444198329
# https://github.com/pypa/pip/pull/5743
from setuptools import setup
setup(
    name='picard',
    version='0.1.1',
    packages=['picard'],
    install_requires=[
        'boto3>=1.9,<1.10',
        'toml>=0.10,<0.11',
        'typing_extensions>=3.6,<3.7',
    ],
)
