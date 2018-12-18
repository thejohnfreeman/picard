"""Context shared by the state graph.

Context makes it possible to pass information "up" the state graph (or "down",
depending on your perspective), from dependents to dependencies. It generally
carries a configuration and a shared logger.
"""

import logging
import typing as t

class Context:
    """For now, this is just a placeholder."""

    log: t.Any = logging
