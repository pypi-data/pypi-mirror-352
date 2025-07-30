from typing import Dict, Type, Any, Optional, Callable, Set, List, TypeVar
from abc import ABCMeta
from collections import defaultdict

from .logger import _LOGGER_

T = TypeVar('T')

class RegistryError(Exception):
    """Base exception for registry-related errors."""
    pass

class DuplicateRegistrationError(RegistryError):
    """Raised when attempting to register a duplicate class name."""
    pass

class ValidationError(RegistryError):
    """Raised when class validation fails during registration."""
    pass

class Registry:
    """
    Class registry that maintains registered classes and handles validation.
    """
    def __init__(self):
        self._entries: Dict[str, Type] = {}
        self._aliases: Dict[str, Set[str]] = defaultdict(set)
        self._validators: List[Callable[[Type], bool]] = []
    
    def _validate_class(self, cls: Type) -> None:
        """Run all registered validators against a class."""
        for validator in self._validators:
            if not validator(cls):
                raise ValidationError(f"Class {cls.__name__} failed validation")

    def register(self, cls: Type[T], key: Optional[str] = None, aliases: Optional[list[str]] = None) -> None:
        """Register a class with optional custom key and aliases."""
        reg_key = key or cls.__name__
        
        if reg_key in self._entries:
            raise DuplicateRegistrationError(f"Key '{reg_key}' is already registered")
        
        if aliases:
            for alias in aliases:
                if alias in self._entries:
                    raise DuplicateRegistrationError(
                        f"Alias '{alias}' conflicts with existing registration"
                    )
                self._aliases[reg_key].add(alias)
        
        self._validate_class(cls)
        self._entries[reg_key] = cls

    def get(self, name: str, default: Any = None) -> Optional[Type[T]]:
        """Retrieve a class by name or alias."""
        if name in self._entries:
            return self._entries[name]
        
        for key, aliases in self._aliases.items():
            if name in aliases:
                return self._entries[key]
        
        return default

    def remove(self, key: str) -> None:
        """Remove a registered class by its key or alias."""
        if key in self._entries:
            del self._entries[key]
            self._aliases.pop(key, None)
        else:
            for reg_key, aliases in self._aliases.items():
                if key in aliases:
                    aliases.remove(key)
                    return
            raise RegistryError(f"Key or alias '{key}' not found in registry")

    def pop(self, key: str) -> Optional[Type[T]]:
        """Remove and return a registered class by its key or alias."""
        if key in self._entries:
            cls = self._entries.pop(key)
            self._aliases.pop(key, None)
            return cls
        
        for reg_key, aliases in self._aliases.items():
            if key in aliases:
                aliases.remove(key)
                return self._entries.get(reg_key)
        
        return None

    def add_validator(self, validator: Callable[[Type], bool]) -> None:
        """Add a validation function for registrations."""
        self._validators.append(validator)

    def all_entries(self, include_aliases: bool = False) -> Dict[str, Type[T]]:
        """Get all registered entries, optionally including aliases."""
        entries = dict(self._entries)
        if include_aliases:
            for key, aliases in self._aliases.items():
                for alias in aliases:
                    entries[alias] = self._entries[key]
        return entries

    def clear(self) -> None:
        """Clear all registered entries and aliases."""
        self._entries.clear()
        self._aliases.clear()
        self._validators.clear()


# Global registry storage
_registries: Dict[str, Registry] = {}

def get_registry(name: str) -> Registry:
    """Get or create a registry with the given name."""
    if name not in _registries:
        _registries[name] = Registry()
    return _registries[name]

def create_registry_metaclass(registry: Registry) -> Type[ABCMeta]:
    """
    Factory function to create a metaclass for a dedicated registry.

    Parameters
    ----------
    registry : Registry
        The registry to associate with the metaclass.

    Returns
    -------
    Type[ABCMeta]
        A metaclass that registers classes in the given registry.
    """

    class DedicatedRegistryMeta(ABCMeta):
        _registry = registry

        def __new__(mcs, name: str, bases: tuple, namespace: dict) -> Type:
            cls = super().__new__(mcs, name, bases, namespace)

            if not getattr(cls, "__abstractmethods__", False):
                reg_key = getattr(cls, "__registry_key__", cls.__name__)
                aliases = getattr(cls, "__registry_aliases__", None)

                if reg_key == "_base":
                    return cls

                try:
                    mcs._registry.register(cls, key=reg_key, aliases=aliases)
                except ValidationError as e:
                    _LOGGER_.warning(f"Class '{cls.__name__}' failed validation: {e}")
                except DuplicateRegistrationError as e:
                    _LOGGER_.warning(f"Duplicate registration for '{cls.__name__}': {e}")
            return cls

    return DedicatedRegistryMeta