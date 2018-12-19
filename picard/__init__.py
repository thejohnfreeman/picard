"""Picard combines the idea of Ansible with the execution of Make."""

from picard.api import main, sync
from picard.context import Context
from picard.file import FileState, file
# I'm only slightly worried about this rebinding of ``state``...
from picard.state import state
from picard.typing import State, StateLike
