"""A sample test in the style of a Makefile.

Compiles an executable from an object file from a source file.
"""

# pylint: disable=missing-docstring,unused-argument,invalid-name

import picard
import picard.clang as clang

code = """
#include <stdio.h>

int main() {
    printf("Hello, world!\\n");
    return 0;
}
"""

@picard.file('hello.c')
async def source(self, context):
    with open('hello.c', 'w') as file:
        file.write(code)

sources = [source]
objects = clang.objects(*sources)
hello = clang.executable('hello', *objects)

if __name__ == '__main__':
    picard.make(hello)
