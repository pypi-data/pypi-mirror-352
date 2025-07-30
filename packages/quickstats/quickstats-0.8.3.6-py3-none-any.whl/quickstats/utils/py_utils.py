import gc
import sys
import inspect
from typing import List

def get_argnames(obj, required_only: bool = False) -> List[str]:
    """
    Retrieves the argument names of a given callable object.

    Parameters
    ----------
    obj : callable
        The object (function or method) to inspect.
    required_only : bool, optional
        If True, only required arguments (without default values) are returned. Default is False.

    Returns
    -------
    list
        A list of argument names.

    Notes
    -----
    - For class methods, 'self' or 'cls' is excluded from the list of argument names.
    """
    sig = inspect.signature(obj)
    if required_only:
        argnames = [
            name for name, param in sig.parameters.items()
            if param.default is param.empty and
            param.kind in [param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY]
        ]
    else:
        argnames = [
            name for name, param in sig.parameters.items()
            if param.kind in [param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY]
        ]

    # Remove 'self' in case of a class object
    if isinstance(obj, type):
        argnames = argnames[1:]

    return argnames

def get_reference_count(obj) -> int:
    """
    Retrieves the reference count of a given object.

    Parameters
    ----------
    obj : object
        The object to inspect.

    Returns
    -------
    int
        The reference count of the object.
    """
    return sys.getrefcount(obj)

def get_referrers(obj) -> list:
    """
    Retrieves the referrers of a given object.

    Parameters
    ----------
    obj : object
        The object to inspect.

    Returns
    -------
    list
        A list of objects that refer to the given object.
    """
    return gc.get_referrers(obj)