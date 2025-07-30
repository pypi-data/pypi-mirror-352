"""
Value constraints for validating numerical and choice-based conditions.

This module provides a set of constraint classes for enforcing value bounds
and valid choices on objects that support comparison operations.
"""

from __future__ import annotations

import numbers
from typing import (
    Any, Set, TypeVar, Hashable, Union, Optional,
    Collection, AbstractSet
)

from .registries import get_registry, create_registry_metaclass

T = TypeVar('T', bound=Hashable)
Number = Union[int, float]

ConstraintRegistry = get_registry('constraint')
ConstraintRegistryMeta = create_registry_metaclass(ConstraintRegistry)

class BaseConstraint(metaclass=ConstraintRegistryMeta):
    """
    Base class for all constraints.
    
    Provides common functionality for constraint checking and representation.
    """
    
    def __call__(self, obj: Any) -> bool:
        """
        Check if object satisfies constraint.

        Parameters
        ----------
        obj : Any
            Object to validate

        Returns
        -------
        bool
            True if constraint is satisfied
        """
        return True

    def __repr__(self) -> str:
        """Generate string representation of constraint."""
        attrs = ','.join(
            f"{k}={v!r}" 
            for k, v in self.__dict__.items() 
            if not k.startswith('_')
        )
        return f"{self.__class__.__name__}({attrs})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another constraint."""
        return isinstance(other, type(self))

    def __hash__(self) -> int:
        """Generate hash based on public attributes."""
        return hash(tuple(
            v for k, v in self.__dict__.items()
            if not k.startswith('_')
        ))

    @classmethod
    def get_label(cls) -> str:
        """Get constraint class name."""
        return cls.__name__

    def to_dict(self) -> dict:
        """
        Serialize the constraint into a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the constraint.
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    @classmethod
    def from_dict(cls, data: dict) -> "BaseConstraint":
        """
        Deserialize a constraint from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary representation of the constraint.

        Returns
        -------
        BaseConstraint
            The deserialized constraint object.
        """
        return cls(**data)

class RangeConstraint(BaseConstraint):
    """
    Constraint enforcing value bounds.

    Parameters
    ----------
    vmin : Number
        Minimum value of the range
    vmax : Number
        Maximum value of the range
    lbound : bool, optional
        If True, vmin is inclusive, by default True
    rbound : bool, optional
        If True, vmax is inclusive, by default True

    Raises
    ------
    ValueError
        If vmin > vmax or bounds are not boolean
    """

    def __init__(
        self,
        vmin: Number,
        vmax: Number,
        lbound: bool = True,
        rbound: bool = True
    ) -> None:
        if vmin > vmax:
            raise ValueError("vmin must be less than or equal to vmax")
        if not isinstance(lbound, bool) or not isinstance(rbound, bool):
            raise ValueError("lbound and rbound must be boolean values")

        self.vmin = vmin
        self.vmax = vmax
        self.lbound = lbound
        self.rbound = rbound
        self._lopt = '__le__' if lbound else '__lt__'
        self._ropt = '__ge__' if rbound else '__gt__'

    def __call__(self, obj: Any) -> bool:
        """
        Check if object falls within range.

        Parameters
        ----------
        obj : Any
            Object to validate

        Returns
        -------
        bool
            True if object is within range

        Raises
        ------
        ValueError
            If object doesn't support required comparison operations
        """
        if not hasattr(obj, self._lopt) or not hasattr(obj, self._ropt):
            raise ValueError(
                f"Object does not support required comparison operators: "
                f"{self._lopt} and {self._ropt}"
            )

        return (
            getattr(obj, self._lopt)(self.vmin) and
            getattr(obj, self._ropt)(self.vmax)
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another range constraint."""
        if not isinstance(other, RangeConstraint):
            return False
        return (
            self.vmin == other.vmin and
            self.vmax == other.vmax and
            self.lbound == other.lbound and
            self.rbound == other.rbound
        )

    def __hash__(self) -> int:
        """Generate hash based on constraint parameters."""
        return hash((self.vmin, self.vmax, self.lbound, self.rbound))


class MinConstraint(BaseConstraint):
    """
    Constraint enforcing minimum value.

    Parameters
    ----------
    vmin : Number
        Minimum allowable value
    inclusive : bool, optional
        If True, vmin is included in valid range, by default True

    Raises
    ------
    ValueError
        If inclusive is not boolean
    """

    def __init__(self, vmin: Number, inclusive: bool = True) -> None:
        if not isinstance(inclusive, bool):
            raise ValueError("inclusive must be a boolean value")

        self.vmin = vmin
        self.inclusive = inclusive
        self._opt = '__le__' if inclusive else '__lt__'

    def __call__(self, obj: Any) -> bool:
        """
        Check if object meets minimum constraint.

        Parameters
        ----------
        obj : Any
            Object to validate

        Returns
        -------
        bool
            True if object meets minimum requirement

        Raises
        ------
        ValueError
            If object doesn't support required comparison operation
        """
        if not hasattr(obj, self._opt):
            raise ValueError(
                f"Object does not support required comparison operator: {self._opt}"
            )
        return getattr(obj, self._opt)(self.vmin)

    def __eq__(self, other: object) -> bool:
        """Check equality with another minimum constraint."""
        if not isinstance(other, MinConstraint):
            return False
        return self.vmin == other.vmin and self.inclusive == other.inclusive

    def __hash__(self) -> int:
        """Generate hash based on constraint parameters."""
        return hash((self.vmin, self.inclusive))


class MaxConstraint(BaseConstraint):
    """
    Constraint enforcing maximum value.

    Parameters
    ----------
    vmax : Number
        Maximum allowable value
    inclusive : bool, optional
        If True, vmax is included in valid range, by default True

    Raises
    ------
    ValueError
        If inclusive is not boolean
    """

    def __init__(self, vmax: Number, inclusive: bool = True) -> None:
        if not isinstance(inclusive, bool):
            raise ValueError("inclusive must be a boolean value")

        self.vmax = vmax
        self.inclusive = inclusive
        self._opt = '__ge__' if inclusive else '__gt__'

    def __call__(self, obj: Any) -> bool:
        """
        Check if object meets maximum constraint.

        Parameters
        ----------
        obj : Any
            Object to validate

        Returns
        -------
        bool
            True if object meets maximum requirement

        Raises
        ------
        ValueError
            If object doesn't support required comparison operation
        """
        if not hasattr(obj, self._opt):
            raise ValueError(
                f"Object does not support required comparison operator: {self._opt}"
            )
        return getattr(obj, self._opt)(self.vmax)

    def __eq__(self, other: object) -> bool:
        """Check equality with another maximum constraint."""
        if not isinstance(other, MaxConstraint):
            return False
        return self.vmax == other.vmax and self.inclusive == other.inclusive

    def __hash__(self) -> int:
        """Generate hash based on constraint parameters."""
        return hash((self.vmax, self.inclusive))

class ChoiceConstraint(BaseConstraint):
    """
    Constraint restricting values to a set of choices.

    Parameters
    ----------
    *choices : T
        Allowable choices

    Examples
    --------
    >>> constraint = ChoiceConstraint('red', 'green', 'blue')
    >>> constraint('red')
    True
    >>> constraint('yellow')
    False
    """

    def __init__(self, *choices: T) -> None:
        self.choices: AbstractSet[T] = frozenset(choices)

    def __call__(self, obj: T) -> bool:
        """
        Check if object is an allowed choice.

        Parameters
        ----------
        obj : T
            Object to validate

        Returns
        -------
        bool
            True if object is an allowed choice

        Raises
        ------
        ValueError
            If object is not among allowed choices
        """
        if obj not in self.choices:
            raise ValueError(
                f"Invalid value: {obj} (Allowed values are: {sorted(self.choices)})"
            )
        return True

    def __eq__(self, other: object) -> bool:
        """Check equality with another choice constraint."""
        if not isinstance(other, ChoiceConstraint):
            return False
        return self.choices == other.choices

    def __hash__(self) -> int:
        """Generate hash based on choices."""
        return hash(self.choices)

def get(identifier: str) -> BaseConstraint:
    return ConstraintRegistry.get(identifier)