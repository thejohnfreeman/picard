(Try to come up with some benchmarks and test.)

Refactor @rules to use PatternTarget:

- Use type :class:`typing.Any` for :class:`picard.pattern.Recipe`.
- :func:`pattern` returns a function, not a class.
- PatternTarget takes its :prop:`_recipe` in constructor.
- :func:`rule` instantiates a :class:`PatternTarget`
- Try to refine :class:`picard.pattern.Recipe`.

Treat args and kwargs as ``Functor[Target]``.
Want to be able to define factories like this:

.. code-block:: python

    @pattern()
    async def security_group(self, context, *, Description=None)
        ...

    sg = security_group('gitlab-runners.sg', Description='GitLab Runners')


:func:`pattern` creates a class with:

- Constructor that takes name as first argument, saves args and kwargs, and
  extracts prerequisites from them.
- Recipe that fmaps :func:`sync` over args and kwargs to evaluate prereqs,
  and then passes them to implementation, logs entry and exit, and memoizes
  return value.

Fix documentation with this progression:

- Target
- @rule
- @pattern
- @file

Take docstrings from :class:`picard.typing.Target` and :mod:`picard.rule`.
