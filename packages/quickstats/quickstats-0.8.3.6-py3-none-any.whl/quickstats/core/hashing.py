from typing import List, Any, Dict, Tuple, Union

import numpy as np

def dict_to_tuple(d: Dict[Any, Any]) -> Tuple[Any, ...]:
    """Convert a dictionary into a hashable tuple of sorted (key, value) pairs.

    This function recursively converts a dictionary and its nested structures into
    a hashable tuple format where dictionary items are sorted by keys.

    Parameters
    ----------
    d : dict
        The dictionary to convert to a hashable format.

    Returns
    -------
    tuple
        A hashable tuple representation of the dictionary with sorted (key, value) pairs.

    Examples
    --------
    >>> dict_to_tuple({'b': 2, 'a': 1})
    (('a', 1), ('b', 2))

    >>> dict_to_tuple({'x': {'b': 2, 'a': 1}, 'y': [1, 2]})
    (('x', (('a', 1), ('b', 2))), ('y', (1, 2)))

    Notes
    -----
    The function handles the following data types:
    - Dictionaries: Converted to sorted tuples of (key, value) pairs
    - Lists and sets: Converted to sorted tuples
    - Tuples: Preserved but contents made hashable
    - Other types: Left unchanged
    """
    def _make_hashable(obj: Any) -> Any:
        if isinstance(obj, dict):
            return dict_to_tuple(obj)
        elif isinstance(obj, np.ndarray):
            return array_to_tuple(obj)
        elif isinstance(obj, (list, set)):
            return tuple(sorted(_make_hashable(e) for e in obj))
        elif isinstance(obj, tuple):
            return tuple(_make_hashable(e) for e in obj)
        else:
            return obj

    return tuple(
        sorted(
            (key, _make_hashable(value))
            for key, value in d.items()
        )
    )

def array_to_tuple(arr: np.ndarray) -> Tuple[Tuple[int, ...], Union[bytes, Tuple[Any, ...]]]:
    """Convert a numpy array into a hashable tuple representation.

    The function captures the essential characteristics of the array
    including shape and data in a hashable format.

    Parameters
    ----------
    arr : np.ndarray
        The numpy array to convert.

    Returns
    -------
    tuple
        A tuple of (shape, data) where:
        - shape is a tuple of integers
        - data is either bytes (for simple dtypes) or tuple (for structured/object dtypes)

    Examples
    --------
    >>> x = np.array([[1, 2], [3, 4]])
    >>> array_to_tuple(x)
    ((2, 2), b'\\x01\\x00...'))  # bytes will depend on system endianness

    >>> y = np.array(['a', 'b'])  # object dtype
    >>> array_to_tuple(y)
    ((2,), ('a', 'b'))
    """
    if arr.dtype.kind in 'OUS':  # Object, Unicode, String dtypes
        return (arr.shape, tuple(arr.flatten()))
    else:
        return (arr.shape, arr.tobytes())

def hash_array(arr: np.ndarray) -> int:
    """Compute a hash value for a numpy array using its internal buffer.

    This function creates a hash of the array's data buffer along with its
    shape and dtype to ensure arrays with different shapes or types but same
    data get different hashes.

    Parameters
    ----------
    arr : np.ndarray
        The numpy array to hash.

    Returns
    -------
    int
        A hash value for the array.

    Examples
    --------
    >>> x = np.array([[1, 2], [3, 4]])
    >>> hash_array(x)  # Returns an integer hash
    >>> y = x.copy()
    >>> hash_array(x) == hash_array(y)  # True
    >>> z = x.reshape(-1)
    >>> hash_array(x) == hash_array(z)  # False, different shapes
    """
    return hash(array_to_tuple(arr))

def hash_dict(d: Dict[Any, Any]) -> int:
    """Compute a hash value for a dictionary.

    The function first converts the dictionary to a hashable tuple format
    and then applies Python's built-in hash function.

    Parameters
    ----------
    d : dict
        The dictionary to hash.

    Returns
    -------
    int
        Hash value of the dictionary.

    Examples
    --------
    >>> d1 = {'a': 1, 'b': 2}
    >>> d2 = {'b': 2, 'a': 1}
    >>> hash_dict(d1) == hash_dict(d2)
    True
    """
    return hash(dict_to_tuple(d))