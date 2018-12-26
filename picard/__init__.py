"""Picard combines the idea of Ansible with the execution of Make."""

# I'm only slightly worried about the rebindings of ``file`` and ``rule``...
from picard.api import main, sync
from picard.context import Context
from picard.file import (
    FileRecipePostConditionError, FileTarget, file, file_target
)
from picard.pattern import pattern
from picard.rule import rule
from picard.shell import sh
from picard.typing import Target
