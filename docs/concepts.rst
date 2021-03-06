Concepts
========

Most of the terminology in Picard has been lifted from Make, which
I anticipate will be familiar to most of the people reading this. By reusing
the same terms for the same or similar concepts, I hope to ease their
comprehension.


Targets
-------

A **target** represents some entity, e.g. a file or a process. It has:

- A unique human-readable name for debugging.
- A (possibly empty) set of **prerequisite** targets.
- A **recipe** function that brings the entity into a specific state, and then
  returns a representation of it to be used by dependent targets. Recipes are
  asynchronous to enable concurrency.

.. code-block:: python

    class Target:
      name: str
      prereqs: Traversable['Target']
      async def recipe(self, context: Context) -> Any: ...

In Make__, the combination of a target, prerequisites, and a recipe forms
a **rule**. We could have called this class a ``Rule``, but when we pass these
objects around, e.g. as prerequisites, we just think of them as targets, thus
the name.

.. _rule: https://www.gnu.org/software/make/manual/html_node/Rule-Introduction.html#Rule-Introduction
__ rule_


Prerequisites
~~~~~~~~~~~~~

The type of the prerequisites is a non-specific traversable_ that supports
iteration and mapping. Trivially, this can be a single value, but more often
it will be an arbitrary structure of nested collections, like a JSON value.
This way, you can use whatever structure you want to express your
prerequisites, as long as it can be iterated (to capture the dependency edges)
and mapped (for evaluating targets buried within).

.. _traversable: https://hackage.haskell.org/package/base/docs/Data-Traversable.html


Recipes
~~~~~~~

The basic principle of every recipe is that it establishes a post-condition by
the time it exits. In the style of Make, such a post-condition would be "the
target file exists with a modified timestamp after that of all of its
prerequisites." In the style of Ansible, a post-condition might be "the target
service is running on its prerequisite host."

There is one notable difference between Picard's recipes and those of Make. In
Make, a recipe is executed conditionally: only when the target does not exist,
or has a modified timestamp before one of its prerequisites. In Picard, recipe
functions are called unconditionally. The common, expected practice is that
recipes themselves check what changes they need to make, and that they make
the fewest changes necessary to establish their post-condition. Handing over
this responsibility to users is the only way to enable tests beyond modified
timestamps.

Each recipe returns an abstract representation of its target, e.g. a file path
or a hostname and port. When a target serves as a prerequisite for other
targets, its representation may be used in their recipes. When deciding what
a recipe should return, consider what dependents may need. It is expected that
a recipe returns the same value whether it needed to make changes or not.
Recipes should generally memoize their return value to avoid duplicate work.

Each recipe is given an argument called the **context**. Context makes it
possible to pass information "up" the dependency graph (or "down", depending
on your perspective), from targets to their prerequisites. It generally
carries a configuration and a logger.

The process of calling a target's recipe with a context is called
**synchronization** or **evaluation**. We generally use "synchronization" to
emphasize the process of changing an external entity to match the parameters
of the target, and "evaluation" to emphasize the abstract value returned by
the recipe in preparation for another recipe.


Rules
-----

A target is a combination of a name, a set of prerequisites, and an (async)
recipe function. Because every async function in Python has a name, we just
need to add a set of prerequisites to make a target, which we can do with
a decorator much easier than defining a class. Picard calls this decorator
``rule`` because it lets us build targets from recipe functions with a syntax
that mimics Make:

.. code-block:: python

    @picard.rule()
    async def clean(self, context):
        picard.sh('rm', '-rf', 'build')

The arguments to the decorator, if any, are the target's prerequisites. The
decorated function is its recipe. The first argument to the recipe is the
context. The rest of the positional and keyword arguments are the same as what
was passed to the decorator, except all targets within will have been replaced
by their evaluation.

.. code-block:: python

    @picard.rule()
    async def a(context):
        ...

    @picard.rule()
    async def b(context):
        ...

    @picard.rule(xs=[a, b])
    async def target(context, *, xs):
        a, b = xs
        # In here, ``a`` and ``b`` are the values returned by
        # evaluating the targets ``a`` and ``b`` with ``context``.


Patterns
--------

A **pattern** is a template for targets, named after Make's `pattern rules`_.
A pattern is first defined by supplying a generic recipe, and then it is
instantiated one or more times to make targets.

.. _`pattern rules`: https://www.gnu.org/software/make/manual/html_node/Pattern-Rules.html

The recipe given to a pattern definition is much the same as that given to
a rule definition, except that it has an additional first parameter: the
target itself. A pattern does not yet define a target, so the recipe cannot
know it until it is called.

Defining a pattern creates a **constructor** which you can use to stamp out
targets. The constructor expects slightly different arguments than the recipe
you supplied for the pattern. Its first parameter is the name of the target.
The rest of the positional and keyword arguments can be whatever you want to
pass through to the recipe. It may contain a mix of values and targets. Any
targets nestled within will be considered prerequisites and evaluated before
being passed to the recipe. In other words, the recipe will only see values,
not targets.

.. code-block:: python

    import picard

    @picard.pattern()
    async def object_file(target, context, source):
        await picard.sh('gcc', '-c', source, '-o', target.name)

    hello_o = object_file('hello.o', 'hello.c')
    example_o = object_file('example.o', source='example.c')


Drivers
-------

Once you've defined a set of rules, you need to choose one or more targets and
synchronize them (which will recursively synchronize their prerequisites).
Picard offers two functions to help with this.


sync
~~~~

.. code-block:: python

    sync(target: Target, context: Context = None) -> Any

Synchronize a target with an optional context and return its value. If no
context is given, a default context will be constructed, which will have two
properties: an empty configuration named ``config``, and a logger (the root
logger from the ``logging`` module) named ``log``.


make
~~~~

.. code-block:: python

    make(
        target: Target,
        config: Mapping[str, Any] = {},
        rules: Mapping[str, Target] = None,
    )

A command line interface similar to Make_. ``make`` takes a few parameters:

1. ``target``: The default target to synchronize. In Make, this would be the
   first declared target. With Picard, you must pass it.
2. ``config``: The default configuration, a mapping from strings to values.
3. ``rules``: The set of known rules. If not given, it will default to the set
   of variables in the module from which ``make`` was called.

``make`` takes a few steps:

1. It parses the command line for options of the form ``name=value`` or
   ``--name value``, and then considers the rest of the command line
   arguments, if any, to be names of targets.
2. It builds a configuration mapping by taking the defaults in ``config``,
   then overlaying variables from the environment, and then overlaying the
   options it parsed in step 1.
3. It packages the configuration it built in step 2 with the root logger from
   the ``logging`` module into a context.
4. It searches the ``rules`` mapping for the targets named in step 1 (or if
   none were found, the default ``target``), and then synchronizes them all
   with the context built in step 3.

``make`` is meant to be used like this:

.. code-block:: python

    import picard

    # Define targets.
    target = ...

    if __name__ == '__main__':
        picard.make(target)
