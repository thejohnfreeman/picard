"""Batteries for C/C++ compilation."""

import re

from picard.file import file, file_target
from picard.shell import sh

def source(filename):
    """Compute header file dependencies from a source file."""
    # TODO: Implement :func:`find_headers`.
    # headers = [file_target(h) for h in find_headers(filename)]
    return file(filename)()


def sources(*filenames):
    return [source(f) for f in filenames]


def object_from_source(source):
    """Compile an object file from a source file."""
    source = file_target(source)
    @file(re.sub('\\.c$', '.o', source.name), [source])
    async def object_(self, context, prereqs):
        # pylint: disable=unused-argument
        # TODO: Move standard environment variables like CC, CXX, CFLAGS, ...
        # into :param:`context` from :func:`picard.main` and use them here.
        await sh('gcc', '-c', *map(str, prereqs))
    return object_


def objects(sources):
    """Return a set of object files mapped from a set of source files."""
    return [object_from_source(s) for s in sources]


def executable(filename, objects):
    """Link an executable from object files."""
    @file(filename, objects)
    async def target(self, context, prereqs):
        # pylint: disable=unused-argument
        await sh('gcc', '-o', self.name, *map(str, prereqs))
    return target
