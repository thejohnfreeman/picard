"""Patterns for compiling C and C++ objects and executables."""

import re
import typing as t

from picard.file import file, file_target, FileLike, FileTargetLike
from picard.shell import sh
from picard.typing import Target

def object_(source: FileTargetLike) -> Target:
    """Compile an object file from a source file.

    Parameters
    ----------
    source :
        A filename, path, or file target.

    Returns
    -------
    Target
        A :ref:`file target <file-target>` for the object file compiled from
        ``source``.
    """
    # TODO: Implement :func:`find_headers`.
    # headers = [file_target(h) for h in find_headers(filename)]
    headers: t.Iterable[FileTargetLike] = []
    source = file_target(source)
    @file(re.sub('\\.c$', '.o', source.name), source, *headers)
    async def target(self, context, source, *headers):
        # pylint: disable=unused-argument
        cc = context.config.get('CC', 'cc')
        cpp_flags = context.config.get('CPPFLAGS', None)
        c_flags = context.config.get('CFLAGS', None)
        await sh(cc, cpp_flags, c_flags, '-c', source)
    return target

def objects(*sources):
    """Return a set of object files mapped from a set of source files."""
    return [object_(s) for s in sources]

def executable(filename: FileLike, *objects: FileTargetLike) -> Target:
    """Link an executable from object files.

    Parameters
    ----------
    filename :
        The filename or path to where the executable should be built.
    *objects :
        A set of filenames, paths, or targets for the object files.

    Returns
    -------
    Target
        A :ref:`file target <file-target>` for the executable linked from
        ``objects``.
    """
    @file(filename, *objects)
    async def target(self, context, *objects):
        # pylint: disable=unused-argument
        cc = context.config.get('CC', 'cc')
        ld_flags = context.config.get('LDFLAGS', None)
        ld_libs = context.config.get('LDLIBS', None)
        await sh(cc, ld_flags, '-o', self.name, *objects, ld_libs)
    return target
