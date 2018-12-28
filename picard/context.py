"""Context shared through the dependency graph."""

import logging
import typing as t

class Context:
    """A configuration mapping and a logger."""

    def __init__(
            self,
            config: t.Mapping[str, t.Any] = None,
            log: logging.Logger = logging.getLogger(),
    ) -> None:
        self.config = {} if config is None else config
        self.log = log
