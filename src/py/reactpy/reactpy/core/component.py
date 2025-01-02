from __future__ import annotations

import inspect
import logging
from functools import wraps
from typing import Any, Callable

from reactpy.core.types import ComponentType, VdomDict

from reactpy.core.id import task_name

logger = logging.getLogger(__name__)


# STJ: @component wrapper
def component(
    function: Callable[..., ComponentType | VdomDict | str | None]
) -> Callable[..., Component]:
    """A decorator for defining a new component.

    Parameters:
        function: The component's :meth:`reactpy.core.proto.ComponentType.render` function.
    """
    sig = inspect.signature(function)

    if "key" in sig.parameters and sig.parameters["key"].kind in (
        inspect.Parameter.KEYWORD_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    ):
        msg = f"Component render function {function} uses reserved parameter 'key'"
        raise TypeError(msg)

    @wraps(function)
    def constructor(*args: Any, key: Any | None = None, **kwargs: Any) -> Component:
        return Component(function, key, args, kwargs, sig)

    return constructor


# Instance returned by @component
class Component:
    """An object for rending component models."""

    __slots__ = "__weakref__", "_func", "_args", "_kwargs", "_sig", "key", "type"

    def __init__(
        self,
        function: Callable[..., ComponentType | VdomDict | str | None],
        key: Any | None,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        sig: inspect.Signature,
    ) -> None:
        self.key = key
        self.type = function
        self._args = args
        self._kwargs = kwargs
        self._sig = sig
        logger.info("%s Component.constructor(%s)", task_name(), self.type.__name__)

    def render(self) -> ComponentType | VdomDict | str | None:
        logger.info("%s Component.render(%s)",  task_name(), self.type.__name__)
        return self.type(*self._args, **self._kwargs)

    def __repr__(self) -> str:
        try:
            args = self._sig.bind(*self._args, **self._kwargs).arguments
        except TypeError:
            return f"{self.type.__name__}(...)"
        else:
            items = ", ".join(f"{k}={v!r}" for k, v in args.items())
            if items:
                return f"{self.type.__name__}({id(self):02x}, {items})"
            else:
                return f"{self.type.__name__}({id(self):02x})"
