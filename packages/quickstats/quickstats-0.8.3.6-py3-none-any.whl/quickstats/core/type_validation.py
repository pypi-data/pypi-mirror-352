"""
Runtime type validation utilities for Python type hints.

This module provides efficient runtime validation of objects against Python type hints,
including support for generics, unions, literals, and other complex type annotations.
Designed for Python 3.8+ with focus on performance and extensibility.
"""

from __future__ import annotations

__all__ = [
    'ValidatorFactory',
    'check_type',
    'get_type_hint_str',
    'get_annotation_str',
    'get_type_validator'
]

from collections import abc
from functools import lru_cache
from typing import (
    Any, Callable, Dict, List, Tuple, Union, Optional,
    TypeVar, get_args, get_origin, Type, final
)

# Handle Literal type availability
try:
    from typing import Literal
    HAS_LITERAL = True
except ImportError:
    try:
        from typing_extensions import Literal
        HAS_LITERAL = True
    except ImportError:
        Literal = None
        HAS_LITERAL = False

# Type definitions
ValidatorFunc = Callable[[Any], bool]
TypeHint = Any
T = TypeVar('T')

class ValidationError(TypeError):
    """
    Exception raised for type validation errors.
    
    Parameters
    ----------
    message : str
        Error description
    expected_type : Optional[TypeHint]
        Expected type annotation
    received_type : Optional[Type]
        Actual type received
    value : Optional[Any]
        Value that failed validation
    
    Examples
    --------
    >>> raise ValidationError("Invalid type", List[int], str, "not a list")
    ValidationError: Invalid type - expected List[int], got str ('not a list')
    """
    
    def __init__(
        self,
        message: str,
        expected_type: Optional[TypeHint] = None,
        received_type: Optional[Type] = None,
        value: Any = None
    ) -> None:
        self.expected_type = expected_type
        self.received_type = received_type
        self.value = value
        
        if expected_type is not None and received_type is not None:
            message = (
                f"{message} - expected {get_type_hint_str(expected_type)}, "
                f"got {received_type.__name__}"
            )
            if value is not None:
                message = f"{message} ({value!r})"
                
        super().__init__(message)


@final
class ValidatorFactory:
    """
    Factory for creating and caching type validators.
    
    This class provides efficient creation and caching of validator functions
    for various type hints. It handles complex type hierarchies and supports
    custom validation rules.
    
    Examples
    --------
    >>> validator = ValidatorFactory.get_validator(List[int])
    >>> validator([1, 2, 3])
    True
    >>> validator(['a', 'b'])
    False
    
    >>> # Validate nested types
    >>> nested_validator = ValidatorFactory.get_validator(Dict[str, List[int]])
    >>> nested_validator({'nums': [1, 2, 3]})
    True
    """
    
    CACHE_SIZE: int = 1024
    
    @staticmethod
    def _is_optional(type_hint: TypeHint) -> bool:
        """Check if type hint is Optional[T]."""
        if get_origin(type_hint) is Union:
            args = get_args(type_hint)
            return type(None) in args
        return False

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def create_union_validator(type_args: Tuple[TypeHint, ...]) -> ValidatorFunc:
        """Create an optimized validator for Union types."""
        simple_types = tuple(
            arg for arg in type_args
            if not get_args(arg) and not isinstance(arg, TypeVar)
        )
        
        complex_validators = tuple(
            ValidatorFactory.get_validator(arg)
            for arg in type_args
            if get_args(arg) or isinstance(arg, TypeVar)
        )
        
        if not complex_validators:
            return lambda obj: isinstance(obj, simple_types)
            
        if not simple_types:
            return lambda obj: any(v(obj) for v in complex_validators)
            
        def validate(obj: Any) -> bool:
            return isinstance(obj, simple_types) or any(v(obj) for v in complex_validators)
            
        return validate

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def create_sequence_validator(
        item_type: TypeHint,
        accepted_types: Tuple[Type, ...] = (list, tuple)
    ) -> ValidatorFunc:
        """Create an optimized validator for sequence types."""
        item_validator = (
            ValidatorFactory.get_validator(item_type)
            if item_type is not Any
            else lambda _: True
        )
        
        def validate(obj: Any) -> bool:
            if not isinstance(obj, accepted_types):
                return False
            return all(item_validator(item) for item in obj)
            
        return validate

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def create_mapping_validator(
        key_type: TypeHint,
        value_type: TypeHint
    ) -> ValidatorFunc:
        """Create an optimized validator for mapping types."""
        key_validator = ValidatorFactory.get_validator(key_type)
        value_validator = ValidatorFactory.get_validator(value_type)
        
        def validate(obj: Any) -> bool:
            if not isinstance(obj, abc.Mapping):
                return False
            return all(
                key_validator(k) and value_validator(v)
                for k, v in obj.items()
            )
            
        return validate

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def create_tuple_validator(type_args: Tuple[TypeHint, ...]) -> ValidatorFunc:
        """Create an optimized validator for tuple types."""
        if not type_args:
            return lambda obj: isinstance(obj, tuple)
            
        # Handle Tuple[T, ...]
        if len(type_args) == 2 and type_args[1] is Ellipsis:
            item_validator = ValidatorFactory.get_validator(type_args[0])
            return lambda obj: (
                isinstance(obj, tuple) and
                all(item_validator(item) for item in obj)
            )
            
        # Handle fixed-length tuples
        validators = tuple(
            ValidatorFactory.get_validator(arg)
            for arg in type_args
        )
        
        def validate(obj: Any) -> bool:
            if not isinstance(obj, tuple) or len(obj) != len(validators):
                return False
            return all(
                validator(item)
                for validator, item in zip(validators, obj)
            )
            
        return validate

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def create_literal_validator(allowed_values: Tuple[Any, ...]) -> ValidatorFunc:
        """Create an optimized validator for Literal types."""
        value_set = frozenset(allowed_values)
        return lambda obj: obj in value_set

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def get_validator(type_hint: TypeHint) -> ValidatorFunc:
        """
        Get or create a validator function for a type hint.
        
        Parameters
        ----------
        type_hint : TypeHint
            Type hint to validate against
            
        Returns
        -------
        ValidatorFunc
            Function that validates objects against the type hint
        """
        if type_hint is Any:
            return lambda _: True
            
        origin = get_origin(type_hint)
        if origin is None:
            if isinstance(type_hint, TypeVar):
                if type_hint.__constraints__:
                    return ValidatorFactory.create_union_validator(
                        type_hint.__constraints__
                    )
                if type_hint.__bound__:
                    return ValidatorFactory.get_validator(type_hint.__bound__)
                return lambda _: True
            return lambda obj: isinstance(obj, type_hint)
            
        args = get_args(type_hint)
        
        # Handle Optional types
        if ValidatorFactory._is_optional(type_hint):
            non_none_types = tuple(arg for arg in args if arg is not type(None))
            if len(non_none_types) == 1:
                validator = ValidatorFactory.get_validator(non_none_types[0])
                return lambda obj: obj is None or validator(obj)
            return ValidatorFactory.create_union_validator(args)
            
        # Handle common container types
        if origin in (list, abc.Sequence) and not issubclass(origin, tuple):
            return ValidatorFactory.create_sequence_validator(
                args[0] if args else Any
            )
            
        if origin in (dict, abc.Mapping):
            return ValidatorFactory.create_mapping_validator(
                args[0] if args else Any,
                args[1] if len(args) > 1 else Any
            )
            
        if origin == tuple:
            return ValidatorFactory.create_tuple_validator(args)
            
        if origin == Union:
            return ValidatorFactory.create_union_validator(args)
            
        if HAS_LITERAL and origin is Literal:
            return ValidatorFactory.create_literal_validator(args)
            
        # Handle other generic types
        if args:
            validator = ValidatorFactory.get_validator(origin)
            return lambda obj: validator(obj) and all(
                ValidatorFactory.get_validator(arg)(obj)
                for arg in args
            )
            
        return lambda obj: isinstance(obj, origin)


def check_type(
    obj: Any,
    type_hint: TypeHint,
    *,
    raise_error: bool = False
) -> bool:
    """
    Check if an object matches a type hint.
    
    Parameters
    ----------
    obj : Any
        Object to validate
    type_hint : TypeHint
        Type hint to validate against
    raise_error : bool, optional
        If True, raises ValidationError on type mismatch
    
    Returns
    -------
    bool
        True if object matches type hint
        
    Raises
    ------
    ValidationError
        If raise_error is True and validation fails
    """
    validator = ValidatorFactory.get_validator(type_hint)
    result = validator(obj)
    
    if not result and raise_error:
        raise ValidationError(
            "Type mismatch",
            expected_type=type_hint,
            received_type=type(obj),
            value=obj
        )
    return result


@lru_cache(maxsize=ValidatorFactory.CACHE_SIZE)
def get_type_hint_str(type_hint: TypeHint) -> str:
    """Get human-readable string representation of a type hint."""
    if type_hint is type(None):
        return 'None'
        
    origin = get_origin(type_hint)
    if origin is None:
        if isinstance(type_hint, TypeVar):
            if type_hint.__constraints__:
                constraints = ' | '.join(
                    get_type_hint_str(t) for t in type_hint.__constraints__
                )
                return f"{type_hint.__name__}[{constraints}]"
            if type_hint.__bound__:
                return f"{type_hint.__name__}[{get_type_hint_str(type_hint.__bound__)}]"
            return type_hint.__name__
        return getattr(type_hint, '__name__', str(type_hint))
        
    args = get_args(type_hint)
    if not args:
        return origin.__name__
        
    if origin is Union:
        non_none_args = tuple(arg for arg in args if arg is not type(None))
        args_str = ' | '.join(map(get_type_hint_str, non_none_args))
        
        return (
            f"Optional[{args_str}]"
            if type(None) in args
            else args_str
        )
        
    if HAS_LITERAL and origin is Literal:
        values_str = ' | '.join(repr(arg) for arg in args)
        return f"Literal[{values_str}]"
        
    args_str = ', '.join(map(get_type_hint_str, args))
    return f"{origin.__name__}[{args_str}]"
	

# Alias for backward compatibility
get_type_validator = ValidatorFactory.get_validator
get_annotation_str = get_type_hint_str