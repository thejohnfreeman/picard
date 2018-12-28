.. _file-target:

Files
=====

Targets based on files and modified timestamps as in Make_. File targets
evaluate to the :class:`pathlib.Path` of their target.

.. _Make: https://www.gnu.org/software/make/manual/make.html

Consider a simple Makefile that builds an executable from a C source file:

.. code-block:: Makefile

    hello : hello.o
            $(CC) $(LDFLAGS) -o hello hello.o $(LDLIBS)

    hello.o : hello.c
            $(CC) $(CPPFLAGS) $(CFLAGS) -c hello.c

Here is the same example in Picard using :func:`picard.file`. One notable
difference is that, due to Python scope rules, you must declare prerequisites
before the targets that depend on them.

.. literalinclude:: ../examples/hello/make.py

.. note::
    If you are compiling C or C++, these patterns in this example have already
    been encapsulated in :mod:`picard.clang`.
