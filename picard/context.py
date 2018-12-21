"""Context shared through the dependency graph.

Context makes it possible to pass information "up" the dependency graph (or
"down", depending on your perspective), from targets to prerequisites. It
generally carries a configuration and a shared logger.
"""

import logging
import typing as t

class Context:
    """For now, this is just a placeholder."""

    log: t.Any = logging
