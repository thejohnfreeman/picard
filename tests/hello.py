"""A sample test in the style of a Makefile.

Compiles an executable from an object file from a source file.
"""

import asyncio
import re

import picard


def object_from_source(source):
    """Compile an object file from a source file."""
    @picard.file(re.sub('\\.c$', '.o', source), [source])
    async def object_(context, inputs):
        # pylint: disable=unused-argument
        await asyncio.create_subprocess_exec(['gcc', '-c'] + inputs)
    return object_


sources = ['hello.c'] # pylint: disable=invalid-name
objects = [object_from_source(s) for s in sources] # pylint: disable=invalid-name


@picard.file('hello', objects)
async def hello(context, inputs):
    # pylint: disable=unused-argument
    await asyncio.create_subprocess_exec(['gcc', '-o', 'hello'] + inputs)


if __name__ == '__main__':
    picard.main()
