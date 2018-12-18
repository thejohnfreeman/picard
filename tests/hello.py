"""A sample test in the style of a Makefile.

Compiles an executable from an object file from a source file.
"""

# pylint: disable=missing-docstring,unused-argument,invalid-name

import asyncio
import re

import picard

code = """
#include <stdio.h>

int main() {
    printf("Hello, world!\\n");
}
"""


async def sh(*args, **kwargs):
    p = await asyncio.create_subprocess_exec(*args, **kwargs)
    await p.wait()


def object_from_source(source):
    """Compile an object file from a source file."""
    @picard.file(re.sub('\\.c$', '.o', source.name), [source])
    async def object_(context, inputs):
        await sh('gcc', '-c', *inputs)
    return object_


@picard.file('hello.c')
async def source(context, inputs):
    with open('hello.c', 'w') as file:
        file.write(code)


sources = [source]
objects = [object_from_source(s) for s in sources]


@picard.file('hello', objects)
async def hello(context, inputs):
    await sh('gcc', '-o', 'hello', *inputs)


if __name__ == '__main__':
    picard.main(hello)
