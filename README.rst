======
picard
======
------
Make it so.
------

The idea of Ansible with the execution of Make.

Start with what I call a "state declaration", e.g. "executable X is built from
its sources and is up-to-date" or "there exists a group of running instances
with this configuration". States may depend on each other, e.g. "the state of
this instance depends on the state of that security group". Picard is like an
rsync for these states: it finds the differences between your current state
and your target state, and executes just the necessary changes to transition
from the first to the second.

In this way, it is much like Ansible or Make. Make is limited to considering
the state of the local filesystem, while Ansible can consider more general
states, e.g. the existence and configuration of remote machines. Ansible's
input is a rigid declarative template (based on Jinja), while Make's input is
an executable script that builds the abstract definition of the target state
and gets to leverage functions and variables. Picard tries to combine the best
of both worlds in pure Python.

Picard has a few main components:

1. An abstract interface for state types to implement.
2. Decorators to ease the implementation of common patterns of state types.
3. Out-of-the-box state types for common use cases, e.g. files (a la Make) and
   Amazon Web Services.
4. A default command line driver.

.. code-block:: python

   import asyncio
   import re

   import picard

   async def sh(*args, **kwargs):
       p = await asyncio.create_subprocess_exec(*args, **kwargs)
       await p.wait()

   def source(filename):
       """Compute header file dependencies from source file."""
       headers = [picard.state(h) for h in find_headers(filename)]
       return picard.file(filename, headers)()

   def object_from_source(source):
       """Compile an object file from a source file."""
       source = picard.state(source)
       @picard.file(re.sub('\\.c$', '.o', source.name), [source])
       async def object_(context, inputs):
           await sh('gcc', '-c', *inputs)
       return object_

   # Start with one source file, which we expect to exist.
   sources = [source('hello.c')]
   # Compute object files from source files.
   objects = [object_from_source(s) for s in sources]

   # Link all object files into one executable.
   @picard.file('hello', objects)
   async def hello(context, inputs):
       await sh('gcc', '-o', 'hello', *inputs)

   # Select a target on the command line, using "hello" as the default.
   if __name__ == '__main__':
       picard.main(hello)
