from typing import Any, Callable
from ..lib import array, matrix
from ..types.matrix import Matrix
from .function_isolation import isolate_function

__scope_id__ = ''

methods = {}


def method(func: Callable) -> Callable:
    """
    Decorator to mark a function as a Pine method.
    This is used to indicate that the function should be treated as a method in Pine Script.
    """
    setattr(func, '__pine_method__', True)
    return func


# noinspection PyShadowingNames
def method_call(method: str | Callable, var: Any, *args, **kwargs) -> Any:
    global __scope_id__

    # If method is a string
    if isinstance(method, str):
        try:
            if isinstance(var, list):
                return getattr(array, method)(var, *args, **kwargs)

            elif isinstance(var, Matrix):
                return getattr(matrix, method)(var, *args, **kwargs)
        except AttributeError:
            pass

        # TODO: find the methods registered from user libraries
        assert False

    # It is a local method, it should be a local function
    elif callable(method):
        return isolate_function(method, '__method_call__', __scope_id__)(var, *args, **kwargs)

    return None
