from typing import Callable
import inspect
import sys

__all__ = ['export']

_do_nothing = lambda: None


def export(*to_export: Callable | str) -> Callable:
    """
    Decorator to add function name into its module's __all__ list
    It can also be used as a function to export a list of names or a single name

    :param to_export: The function to export or a list of names to export
    :return: The decorated function (the same function)
    """
    assert to_export, "@export decorator must be called with a function or a list of names to export!"
    to_export = list(to_export)  # type: ignore
    assert callable(to_export[0]) or all(isinstance(name, str) for name in to_export), \
        "@export decorator can only be used on function or list of strings of module attributes!"

    # Get the from the decorator called
    caller = inspect.stack()[1]
    module = sys.modules[caller.frame.f_globals['__name__']]
    if not hasattr(module, '__all__'):
        module.__all__ = []  # type: ignore

    # Function
    if len(to_export) == 1 and callable(to_export[0]):
        module.__all__.append(to_export[0].__name__)
        return to_export[0]

    # List of names
    for name in to_export:
        module.__all__.append(name)

    # Return do_nothing function
    return _do_nothing
