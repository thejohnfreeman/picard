"""Picard combines the idea of Ansible with the execution of Make."""

from picard.api import main, sync
from picard.context import Context
# I'm only slightly worried about the rebindings of ``file`` and ``target``...
from picard.file import FileTarget, file
from picard.rule import rule
from picard.shell import sh
from picard.target import target
from picard.typing import Target, TargetLike
