"""
Utilities for working with nested dictionaries, providing recursive update and merge capabilities.

This module implements a custom dictionary class and helper functions for handling nested
dictionary structures with recursive update operations.
"""

from __future__ import annotations

from copy import deepcopy
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Type,
    TypeVar,
    Union,
)

from .typing import Mapping, MutableMapping

T = TypeVar('T', bound=Mapping[str, Any])

def recursive_update(
    target: MutableMapping[str, Any],
    source: Mapping[str, Any],
    /
) -> MutableMapping[str, Any]:
    """
    Update a dictionary recursively with values from another dictionary.

    Parameters
    ----------
    target : MutableMapping[str, Any]
        The dictionary to be updated.
    source : Mapping[str, Any]
        The dictionary containing updates.

    Returns
    -------
    MutableMapping[str, Any]
        The updated dictionary (same object as target).

    Notes
    -----
    This function modifies the target dictionary in-place. For nested dictionaries,
    it performs a deep update rather than simply replacing the nested dictionary.

    Examples
    --------
    >>> d1 = {'a': 1, 'b': {'c': 2}}
    >>> d2 = {'b': {'d': 3}}
    >>> recursive_update(d1, d2)
    {'a': 1, 'b': {'c': 2, 'd': 3}}
    """
    if not source:
        return target

    for key, value in source.items():
        if (
            isinstance(value, Mapping) 
            and key in target 
            and isinstance(target[key], MutableMapping)
        ):
            recursive_update(target[key], value)
        else:
            target[key] = value
    return target


def concatenate(
    mappings: Iterable[Optional[Mapping[str, Any]]],
    *, 
    copy: bool = False
) -> NestedDict:
    """
    Concatenate multiple dictionaries recursively.

    Parameters
    ----------
    mappings : Iterable[Optional[Mapping[str, Any]]]
        An iterable of dictionaries to concatenate. None values are skipped.
    copy : bool, optional
        If True, create a deep copy of each dictionary before updating, by default False.

    Returns
    -------
    NestedDict
        A new NestedDict containing the concatenated result.

    Examples
    --------
    >>> d1 = {'a': 1, 'b': {'c': 2}}
    >>> d2 = {'b': {'d': 3}, 'e': 4}
    >>> concatenate([d1, d2])
    {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}
    """
    result = NestedDict()
    for mapping in mappings:
        if not mapping:
            continue
        source = deepcopy(mapping) if copy else mapping
        recursive_update(result, source)
    return result


# Alias for convenience, keeping the same name for backward compatibility
concat = concatenate


def merge_classattr(
    cls: Type,
    attribute: str,
    *,
    copy: bool = False,
    parse: Optional[Callable[[Any], Mapping[str, Any]]] = None
) -> NestedDict:
    """
    Merge a class attribute from the class hierarchy using recursive update.

    Parameters
    ----------
    cls : Type
        The class whose MRO will be used to recursively update the attribute.
    attribute : str
        The name of the dictionary attribute to be updated.
    copy : bool, optional
        If True, create a deep copy of each attribute before updating, by default False.
    parse : Callable[[Any], Mapping[str, Any]], optional
        Function to transform the class attribute before merging.
        Must return a Mapping. If None, no transformation is applied.

    Returns
    -------
    NestedDict
        The merged attribute dictionary after applying recursive updates.

    Raises
    ------
    TypeError
        If the parsed attribute is not a Mapping.
    AttributeError
        If the specified attribute doesn't exist and parse function is None.

    Examples
    --------
    >>> class Base:
    ...     data = {'a': 1}
    >>> class Child(Base):
    ...     data = {'b': 2}
    >>> merge_classattr(Child, 'data')
    {'a': 1, 'b': 2}
    """
    result = NestedDict()
    
    for base_cls in reversed(cls.__mro__):
        try:
            base_data = getattr(base_cls, attribute)
        except AttributeError:
            continue

        if parse is not None:
            try:
                base_data = parse(base_data)
            except Exception as e:
                raise ValueError(
                    f"Failed to parse attribute '{attribute}' from {base_cls.__name__}"
                ) from e

        if not isinstance(base_data, Mapping):
            raise TypeError(
                f"Attribute '{attribute}' in {base_cls.__name__} "
                f"must be a Mapping, not {type(base_data).__name__}"
            )

        if copy:
            base_data = deepcopy(base_data)
        
        recursive_update(result, base_data)
    
    return result


class NestedDict(dict):
    """
    A dictionary subclass supporting recursive updates via operators.

    This class extends the built-in dict to provide recursive update operations
    using the & and &= operators, similar to set operations but for nested dictionaries.

    Methods
    -------
    merge(other)
        Update the dictionary recursively with values from another mapping.
    copy(deep=False)
        Create a shallow or deep copy of the dictionary.

    Examples
    --------
    >>> d1 = NestedDict({'a': 1, 'b': {'c': 2}})
    >>> d2 = {'b': {'d': 3}}
    >>> d3 = d1 & d2
    >>> print(d3)
    {'a': 1, 'b': {'c': 2, 'd': 3}}
    """

    def merge(self, other: Optional[Mapping[str, Any]]) -> None:
        """
        Update the dictionary recursively with values from another mapping.

        Parameters
        ----------
        other : Optional[Mapping[str, Any]]
            The mapping containing updates. If None, no update is performed.

        Raises
        ------
        TypeError
            If other is not None and not a Mapping instance.
        """
        if other is None:
            return

        if not isinstance(other, Mapping):
            raise TypeError(
                f"Expected Mapping, got {type(other).__name__}"
            )
        
        recursive_update(self, other)

    def __and__(self, other: Optional[Mapping[str, Any]]) -> NestedDict:
        """
        Create a new dictionary by recursively updating with another mapping.

        Parameters
        ----------
        other : Optional[Mapping[str, Any]]
            The mapping containing updates.

        Returns
        -------
        NestedDict
            A new dictionary containing the merged result.

        Raises
        ------
        TypeError
            If other is not None and not a Mapping instance.
        """
        return concatenate([self, other], copy=True)

    def __iand__(self, other: Optional[Mapping[str, Any]]) -> NestedDict:
        """
        Update the dictionary in-place recursively with another mapping.

        Parameters
        ----------
        other : Optional[Mapping[str, Any]]
            The mapping containing updates.

        Returns
        -------
        NestedDict
            Self, after applying the updates.

        Raises
        ------
        TypeError
            If other is not None and not a Mapping instance.
        """
        self.merge(other)
        return self

    def copy(self, deep: bool = False) -> NestedDict:
        """
        Create a copy of the dictionary.

        Parameters
        ----------
        deep : bool, optional
            If True, create a deep copy, by default False.

        Returns
        -------
        NestedDict
            A new dictionary containing the copied data.
        """
        return NestedDict(deepcopy(self) if deep else super().copy())