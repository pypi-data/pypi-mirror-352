import inspect
import numbers
from collections.abc import Mapping
from typing import (
    Union, final, Any, TypeVar, Tuple, List, Type,
    Optional
)

import numpy as np
from numpy.typing import ArrayLike

from .modules import get_module_version
if get_module_version('python') >= (3, 9, 0):
    from collections.abc import (
        Iterable,
        Mapping,
        MutableMapping,
        Generator,
    )
else:
    from typing import (
        Iterable,
        Mapping,
        MutableMapping,
        Generator,
    )

try:                                     # 3.8+
    from typing import get_origin, get_args
except ImportError:                      # 3.7
    try:
        from typing_extensions import get_origin, get_args
    except ModuleNotFoundError:          # no typing-extensions
        def get_origin(tp):
            return getattr(tp, "__origin__", None)

        def get_args(tp):
            return getattr(tp, "__args__", ())

__all__ = ["Numeric", "Scalar", "Real", "ArrayLike", "NOTSET", "NOTSETTYPE", "T",
           "Iterable", "Mapping", "MutableMapping", "Generator",
           "is_container", "is_hashable", "is_iterable", "is_class",
           "is_function", "is_indexable_sequence", "get_origin",
           "get_args"]

Numeric = Union[int, float]

Scalar = Numeric

Real = numbers.Real

ArrayType = Union[np.ndarray, List[float], Tuple[float, ...]]

ArrayContainer = Union[Tuple[ArrayLike, ...], List[ArrayLike], np.ndarray]

@final
class NOTSETTYPE:
    """A type used as a sentinel for unspecified values."""
    
    def __copy__(self):
        return self
        
    def __deepcopy__(self, memo: Any):
        return self

    def __reduce__(self):
        return "NOTSET"

NOTSET = NOTSETTYPE()

T = TypeVar('T')

def is_container(obj: Any) -> bool:
    return hasattr(obj, '__contains__')

def is_hashable(obj: Any) -> bool:
    return hasattr(obj, '__hash__')

def is_iterable(obj: Any) -> bool:
    return hasattr(obj, '__iter__')

def is_class(obj: Any) -> bool:
    return inspect.isclass(obj)

def is_function(obj: Any) -> bool:
    return inspect.isfunction(obj)

def is_lambda(obj: Any) -> bool:
    return inspect.isfunction(obj) and obj.__name__ == "<lambda>"

def is_indexable_sequence(obj: Any) -> bool:
    """
    Return True if `obj` behaves like a sequence (supports iteration, indexing, and len())
    but is NOT a mapping, string, bytes, set, or generator.

    This will catch things like:
      - list, tuple
      - numpy.ndarray
      - custom sequence types implementing __iter__, __getitem__, and __len__

    And will exclude:
      - dict or other Mapping
      - str, bytes
      - set
      - generators, iterators without __len__ or __getitem__

    Parameters
    ----------
    obj : Any
        The object to test.

    Returns
    -------
    bool
        True if `obj` is a pure indexable sequence; False otherwise.
    """
    return (
        hasattr(obj, '__iter__')
        and hasattr(obj, '__getitem__')
        and hasattr(obj, '__len__')
        and not isinstance(obj, (str, bytes, Mapping))
    )

def generic_args(
    instance: object,
    generic_base: Optional[Type[Any]] = None,
) -> Optional[list[type]]:
    """
    Return a list of concrete type arguments with which a generic base
    of ``instance`` was instantiated. Returns None if no arguments can be found.

    Parameters
    ----------
    instance : object
        The object whose generic type parameters are to be extracted.

    generic_base : Optional[Type[Any]]
        The unparameterized generic base class to search for. If not given,
        the function attempts to infer it from the instance's __orig_class__.

    Returns
    -------
    Optional[list[type]]
        A list of generic type arguments, or None if none are found.

    Examples
    --------
    >>> class Pair(Generic[T, U]): ...
    >>> p = Pair[int, str]()
    >>> generic_args(p)
    [<class 'int'>, <class 'str'>]

    >>> class MyPair(Pair[int, str]): ...
    >>> generic_args(MyPair())
    [<class 'int'>, <class 'str'>]

    >>> generic_args(Pair())
    None
    """
    oc = getattr(instance, "__orig_class__", None)

    if generic_base is None:
        generic_base = get_origin(oc) or instance.__class__

    if oc and get_origin(oc) is generic_base:
        args = get_args(oc)
        return list(args) if args else None

    for base in getattr(instance.__class__, "__orig_bases__", ()):
        if get_origin(base) is generic_base:
            args = get_args(base)
            return list(args) if args else None

    return None