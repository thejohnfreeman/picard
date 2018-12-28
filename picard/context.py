"""Context shared through the dependency graph."""

import logging
import typing as t

class Context:
    """A configuration mapping and a logger."""
    config: t.Mapping[str, t.Any] = {}
    log: logging.Logger = logging.getLogger()
