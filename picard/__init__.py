"""Picard combines the idea of Ansible with the execution of Make."""

from picard.api import main, sync
from picard.context import Context
# I'm only slightly worried about the rebindings of ``file`` and ``state``...
from picard.file import FileState, file
from picard.rule import rule
from picard.shell import sh
from picard.state import state
from picard.typing import State, StateLike
