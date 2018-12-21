Need a better fmap. What is our order of precedence?

1. Is a known type (built-in implementation for range, str)
2. Is a Functor (has an _fmap_ method)
3. Is a Mapping (dict)
4. Is an Iterator (return a Generator by using yield)
5. Is an Iterable (list, set, tuple, bytes)

If it gets through all these and nothing matches, assume it is identity
functor.

(Try to come up with some benchmarks and test.)

Treat args and kwargs as ``Functor[Target]``.
Want to be able to define factories like this:

.. code-block:: python

    @factory()
    async def security_group(self, context, *, Description=None)
        ...

    sg = security_group('gitlab-runners.sg', Description='GitLab Runners')


:func:`factory` creates a class with:

- Constructor that takes name as first argument, saves args and kwargs, and
  extracts prerequisites from them.
- Recipe that fmaps :func:`sync` over args and kwargs to evaluate prereqs,
  and then passes them to implementation, logs entry and exit, and memoizes
  return value.
