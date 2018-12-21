======
picard
======
------
Make it so.
------

.. image:: https://travis-ci.org/thejohnfreeman/picard.svg?branch=master
    :target: https://travis-ci.org/thejohnfreeman/picard

The idea of Ansible with the execution of Make.

With Picard, you define a set of targets, each with a recipe that leaves it in
a desired state, e.g. a compiled executable or a running service. Targets may
depend on each other, e.g. "this executable depends on that source file" or
"this service depends on that host". Like Make, Picard executes the recipe for
each target in dependency order.

Like Ansible, Picard comes with many sophisticated recipes out-of-the-box
that behave like rsync: they find the differences between a target's present
state and its goal state, and execute just the changes necessary to transition
from the first to the second.

Make is limited to considering targets on the local filesystem, while Ansible
can consider more general targets and states, e.g. the existence and
configuration of remote machines. Ansible's input is a rigid declarative
template (based on Jinja), while Make's input is an executable script that
builds the abstract definitions of the targets and gets to leverage functions
and variables. Picard tries to combine the best of both worlds in pure Python.

Picard has a few main components:

1. An abstract interface for target types to implement.
2. Decorators to ease the implementation of common patterns of target types.
3. Batteries-included target types for common use cases, e.g. files (a la
   Make) and Amazon Web Services (AWS) resources.
4. A default command line driver.

.. code-block:: python

   import asyncio
   import re

   import picard

   def source(filename):
       """Compute header file dependencies from source file."""
       headers = [picard.target(h) for h in find_headers(filename)]
       return picard.file(filename, headers)()

   def object_from_source(source):
       """Compile an object file from a source file."""
       source = picard.target(source)
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
