from __future__ import annotations

import sys
from enum import Enum
from typing import (
    Any, Optional, Union, List, Dict, TypeVar, Type, ClassVar,
    cast, NoReturn
)

# Handle Python version differences for TypeAlias
if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

__all__ = ["CaseInsensitiveStrEnum", "GeneralEnum", "DescriptiveEnum"]

# Type definitions
T = TypeVar('T', bound='GeneralEnum')
EnumValue: TypeAlias = Union[int, str, 'GeneralEnum']

class CaseInsensitiveStrEnum(str, Enum):
    """
    String enumeration that supports case-insensitive comparison.
    
    This class extends the standard string Enum to allow case-insensitive
    matching when looking up enum members.
    
    Examples
    --------
    >>> class Format(CaseInsensitiveStrEnum):
    ...     JSON = "json"
    ...     XML = "xml"
    >>> Format("JSON") == Format.JSON
    True
    >>> Format("json") == Format.JSON
    True
    """
    
    @classmethod
    def _missing_(cls, value: Any) -> Optional[CaseInsensitiveStrEnum]:
        """Handle missing enum values with case-insensitive matching."""
        if not isinstance(value, str):
            return None
            
        value_lower = value.lower()
        for member in cls:
            if member.lower() == value_lower:
                return member
        return None


class GeneralEnum(Enum):
    """
    Enhanced enumeration with parsing and lookup capabilities.
    
    This class extends the standard Enum to provide additional functionality
    like flexible parsing, aliasing, and attribute-based lookups.
    
    Attributes
    ----------
    __aliases__ : ClassVar[Dict[str, str]]
        Class-level mapping of alias names to enum member names
    
    Methods
    -------
    parse(value: Optional[Union[int, str, GeneralEnum]]) -> Optional[GeneralEnum]
        Convert a string, int, or enum value to an enum member
    get_members() -> List[str]
        Get list of all member names
    get_member_by_attribute(attribute: str, value: Any) -> Optional[GeneralEnum]
        Find enum member by attribute value
    
    Examples
    --------
    >>> class Status(GeneralEnum):
    ...     ACTIVE = 1
    ...     INACTIVE = 2
    ...     __aliases__ = {"enabled": "active"}
    >>> Status.parse("active")
    <Status.ACTIVE: 1>
    >>> Status.parse("enabled")
    <Status.ACTIVE: 1>
    """
    
    __aliases__: ClassVar[Dict[str, str]] = {}

    def __eq__(self, other: Any) -> bool:
        """
        Compare enum members with support for parsing string/int values.
        
        Parameters
        ----------
        other : Any
            Value to compare against
            
        Returns
        -------
        bool
            True if values are equal
        """
        if isinstance(other, Enum):
            if not isinstance(other, type(self)):
                return False
            return self.value == other.value
            
        try:
            other_member = self.parse(other)
            return self.value == other_member.value if other_member is not None else False
        except ValueError:
            return False

    def __hash__(self) -> int:
        """Generate hash based on enum value."""
        return hash(self.value)

    @classmethod
    def _missing_(cls: Type[T], value: Any) -> Optional[T]:
        """Handle missing enum values by attempting to parse them."""
        try:
            return cls.parse(value)
        except ValueError:
            return None
    
    @classmethod
    def on_parse_exception(cls, expr: str) -> NoReturn:
        """
        Handle invalid parse attempts with detailed error message.
        
        Parameters
        ----------
        expr : str
            The invalid expression that failed to parse
            
        Raises
        ------
        ValueError
            Always raised with detailed error message
        """
        valid_options = ", ".join(cls.get_members())
        raise ValueError(
            f'Invalid option "{expr}" for enum class "{cls.__name__}". '
            f'Allowed options: {valid_options}'
        )
    
    @classmethod
    def parse(
        cls: Type[T], 
        value: Optional[EnumValue] = None,
        silent: bool = False
    ) -> Optional[T]:
        """
        Parse a value into the corresponding enum member.
    
        Parameters
        ----------
        value : Optional[Union[int, str, GeneralEnum]]
            Value to convert to enum member. Can be:
            - None (returns None)
            - Integer (matched against enum values)
            - String (matched against member names or aliases)
            - Enum instance (returned if matching type)
        silent : bool, optional
            If True, return None instead of raising an error when parsing fails.
            
        Returns
        -------
        Optional[T]
            Corresponding enum member or None if input is None or parsing fails (if silent=True).
            
        Raises
        ------
        ValueError
            If value cannot be parsed to a valid enum member and silent=False.
            
        Examples
        --------
        >>> class Color(GeneralEnum):
        ...     RED = 1
        ...     BLUE = 2
        >>> Color.parse("red")
        <Color.RED: 1>
        >>> Color.parse(2)
        <Color.BLUE: 2>
        >>> Color.parse("invalid", silent=True)  # Returns None instead of raising an error
        None
        """
        if value is None:
            return None
    
        if isinstance(value, cls):
            return value
    
        if isinstance(value, Enum):
            if not silent:
                cls.on_parse_exception(str(value))
            return None
    
        if isinstance(value, str):
            value_lower = value.strip().lower()
            members_map = cls.get_members_map()
            if value_lower in members_map:
                return members_map[value_lower]
    
            aliases_map = cls.get_aliases_map()
            if value_lower in aliases_map:
                return cls.parse(aliases_map[value_lower], silent=silent)
    
            if not silent:
                cls.on_parse_exception(value)
            return None
    
        values_map = cls.get_values_map()
        if value in values_map:
            return values_map[value]
    
        if not silent:
            cls.on_parse_exception(str(value))
        return None

    @classmethod
    def get_members(cls) -> List[str]:
        """
        Get list of all member names in lowercase.
        
        Returns
        -------
        List[str]
            Member names in lowercase
        """
        return [name.lower() for name in cls.__members__]
    
    @classmethod
    def get_members_map(cls: Type[T]) -> Dict[str, T]:
        """
        Get mapping of lowercase names to enum members.
        
        Returns
        -------
        Dict[str, T]
            Mapping of {lowercase_name: enum_member}
        """
        return {
            name.lower(): member 
            for name, member in cls.__members__.items()
        }

    @classmethod
    def get_values_map(cls: Type[T]) -> Dict[Any, T]:
        """
        Get mapping of enum values to members.
        
        Returns
        -------
        Dict[Any, T]
            Mapping of {enum_value: enum_member}
        """
        return {
            member.value: member 
            for member in cls.__members__.values()
        }
    
    @classmethod
    def get_aliases_map(cls) -> Dict[str, str]:
        """
        Get mapping of lowercase aliases to member names.
        
        Returns
        -------
        Dict[str, str]
            Mapping of {lowercase_alias: member_name}
        """
        return {
            alias.lower(): target.lower() 
            for alias, target in cls.__aliases__.items()
        }
    
    @classmethod
    def has_member(cls, name: str) -> bool:
        """
        Check if member exists with given name.
        
        Parameters
        ----------
        name : str
            Name to check (case-insensitive)
            
        Returns
        -------
        bool
            True if member exists
        """
        return name.lower() in cls.get_members()
    
    @classmethod
    def get_member_by_attribute(
        cls: Type[T], 
        attribute: str, 
        value: Any
    ) -> Optional[T]:
        """
        Find enum member by attribute value.
        
        Parameters
        ----------
        attribute : str
            Name of attribute to check
        value : Any
            Value to match
            
        Returns
        -------
        Optional[T]
            Matching enum member or None if not found
            
        Examples
        --------
        >>> class Format(GeneralEnum):
        ...     JSON = (1, "JavaScript Object Notation")
        ...     def __init__(self, id, desc):
        ...         self.id = id
        ...         self.desc = desc
        >>> Format.get_member_by_attribute('id', 1)
        <Format.JSON: 1>
        """
        for member in cls.__members__.values():
            if hasattr(member, attribute):
                if getattr(member, attribute) == value:
                    return member
        return None


class DescriptiveEnum(GeneralEnum):
    """
    Enumeration with additional descriptive text for each member.
    
    This class extends GeneralEnum to add a description field to each
    enum member, useful for human-readable labels and documentation.
    
    Parameters
    ----------
    value : int
        The enum value
    description : str, optional
        Human-readable description of the enum member
    
    Examples
    --------
    >>> class Status(DescriptiveEnum):
    ...     ACTIVE = (1, "Item is currently active")
    ...     INACTIVE = (2, "Item has been deactivated")
    >>> Status.ACTIVE.description
    'Item is currently active'
    """

    description: str

    def __new__(cls, value: int, description: str = "") -> DescriptiveEnum:
        """Create new enum member with description."""
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @classmethod
    def on_parse_exception(cls, expr: str) -> NoReturn:
        """
        Handle invalid parse attempts with descriptive error.
        
        Parameters
        ----------
        expr : str
            The invalid expression
            
        Raises
        ------
        ValueError
            With detailed error including available options and descriptions
        """
        class_name = cls.__name__
        descriptions = "\n".join(
            f"    {name.lower()} - {member.description}"
            for name, member in cls.__members__.items()
        )
        
        raise ValueError(
            f'Invalid option "{expr}" for enum class "{class_name}"\n'
            f'Available options:\n{descriptions}'
        )