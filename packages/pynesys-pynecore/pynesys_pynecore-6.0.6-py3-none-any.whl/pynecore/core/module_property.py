from __future__ import annotations
from typing import TypeVar, overload, Protocol, Any, Generic

T = TypeVar('T')


class ModuleProperyProtocol(Protocol[T]):
    @overload
    def __call__(self) -> T: ...

    @overload
    def __call__(self, *args: Any, **kwargs: Any) -> T: ...

    def __call__(self, *args: Any, **kwargs: Any) -> T: ...


def module_property(func) -> ModuleProperyProtocol[T] | T:
    """
    Decorator for Pine-style hybrid property/functions.
    """
    setattr(func, '__module_property__', True)
    return func
