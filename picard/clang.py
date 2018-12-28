"""Batteries for C/C++ compilation."""

import re

from picard.file import file, file_target
from picard.shell import sh

def object_from_source(source):
    """Compile an object file from a source file."""
    # TODO: Implement :func:`find_headers`.
    # headers = [file_target(h) for h in find_headers(filename)]
    headers = []
    source = file_target(source)
    @file(re.sub('\\.c$', '.o', source.name), source, *headers)
    async def object_(self, context, source, *headers):
        # pylint: disable=unused-argument
        # TODO: Move standard environment variables like CC, CXX, CFLAGS, ...
        # into :param:`context` from :func:`picard.make` and use them here.
        await sh('gcc', '-c', str(source))
    return object_

def objects(*sources):
    """Return a set of object files mapped from a set of source files."""
    return [object_from_source(s) for s in sources]

def executable(filename, *objects):
    """Link an executable from object files."""
    @file(filename, *objects)
    async def target(self, context, *objects):
        # pylint: disable=unused-argument
        await sh('gcc', '-o', self.name, *map(str, objects))
    return target
