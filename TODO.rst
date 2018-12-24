(Try to come up with some benchmarks and test.)

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

- @rule
- @pattern
- @file

Take docstrings from :class:`picard.typing.Target` and :mod:`picard.rule`.
