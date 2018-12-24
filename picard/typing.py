"""Types for mypy."""

import typing as t
import typing_extensions as tex

from picard.context import Context

# mypy does not yet support nested types, so we must use :class:`t.Any`.
# Prerequisites = t.Union['Target', t.Iterable['Prerequisites']]
Prerequisites = t.Any
"""An arbitrary structure for target prerequisites.

The structure can be a single target, a (possibly empty) collection of
targets, or arbitrarily nested collections of targets. We just need a way to
walk the structure and pull out the targets buried within, which we have with
:func:`picard.functor.fmap` for arbitrarily nested functors.
"""

@tex.runtime
class Target(tex.Protocol):
    """A protocol_ (i.e. structural type) for targets.

    .. protocol_: https://www.python.org/dev/peps/pep-0544/

    A **target** represents some entity, e.g. a file or a running service.
    It has:

    - A unique human-readable name for debugging.
    - A (possibly empty) set of prerequisite targets. Capturing them gives us
      a representation of the dependency graph that we can use for debugging.
    - A recipe function that brings the entity into a specific state, and then
      returns a representation of it to be used by dependent targets.

    The terminology for targets has been lifted from Make_, where the
    combination of a target, prerequisites, and a recipe forms a **rule**. We
    could have called this class a ``Rule``, but when we pass these objects
    around, e.g. as prerequisites, we just think of them as targets, thus the
    name.

    .. _Make: https://www.gnu.org/software/make/manual/html_node/Rule-Introduction.html#Rule-Introduction

    The basic principle of every recipe is that it establishes
    a post-condition by the time it exits. In the style of Make, such
    a post-condition would be "the target file exists with a modified
    timestamp after that of all of its prerequisites." In the style of
    Ansible, a post-condition might be "the target service is running on its
    prerequisite host."

    There is one notable difference between our recipes and those of Make. In
    Make, a recipe is executed conditionally: only when the target does not
    exist, or has a modified timestamp before one of its prerequisites. In
    Picard, recipe functions may be called unconditionally. The common,
    expected practice is that recipes themselves check what changes they need
    to make, and that they make the fewest changes necessary to establish
    their post-condition.

    Each recipe returns an abstract representation of its target. When
    a target serves as a prerequisite for other targets, its representation
    may be used in their recipes. It is expected that a recipe returns the
    same value whether it needed to make changes or not. Recipes should
    generally memoize their return value to avoid duplicate work.
    """
    name: str
    prereqs: Prerequisites
    async def recipe(self, context: Context) -> t.Any:
        # pylint: disable=unused-argument,pointless-statement
        ...
