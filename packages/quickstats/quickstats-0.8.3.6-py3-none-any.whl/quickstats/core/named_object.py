from __future__ import annotations

from typing import List, Set, Optional, FrozenSet
import uuid

from .abstract_object import AbstractObject
from quickstats.utils.string_utils import PlainStr

class NamedObject(AbstractObject):
    """
    Represents an object with an optional name and a set of tags.

    Attributes
    ----------
    name : str
        The name of the object. If not provided, a unique name will be generated.
    tags : Set[str]
        A set of tags associated with the object.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None,        
        tags: Optional[List[str]] = None,
        verbosity: str = 'INFO',
        **kwargs
    ):
        """
        Initializes a NamedObject with optional name, tags, and verbosity.

        Parameters
        ----------
        name : Optional[str], default=None
            The name of the object. If None, a unique name will be assigned.
        tags : Optional[List[str]], default=None
            A list of tags for the object. If None, an empty set is used.
        verbosity : str, default='INFO'
            The verbosity level for logging or diagnostics.
        **kwargs : dict
            Additional keyword arguments for the parent class.
        """
        super().__init__(verbosity=verbosity, **kwargs)
        self.name = name
        self.aliases = aliases
        self.description = description
        self.tags = tags

    def __repr__(self) -> str:
        """
        String representation of the NamedObject using the `_repr_dict_`.

        Returns
        -------
        str
            A dynamically constructed string representation of the object.
        """
        repr_items = self._repr_dict_()
        repr_str = ", ".join(f"{key}={value!r}" for key, value in repr_items.items())
        return f"{self.__class__.__name__}({repr_str})"

    def _repr_dict_(self) -> Dict[str, Optional[str]]:
        """
        Returns a dictionary of attributes to be shown in the `repr`.

        This method can be overridden by derived classes to include additional
        attributes or modify the attributes shown in the `repr`.

        Returns
        -------
        Dict[str, Optional[str]]
            A dictionary of attribute names and their values to be shown in the `repr`.
        """
        repr_items = {
            "name": self.name
        }
        if self.aliases:
            repr_items["aliases"] = PlainStr(f'[{", ".join(sorted(list(self.aliases)))}]')
        if self.description is not None:
            repr_items["description"] = self.description
        return repr_items

    @property
    def name(self) -> str:
        """
        The name of the object.

        Returns
        -------
        str
            The name of the object.
        """
        return self._name

    @name.setter
    def name(self, value: Optional[str]) -> None:
        """
        Sets the name of the object.

        Parameters
        ----------
        value : Optional[str]
            The name to set. If None, a unique name will be assigned.

        Raises
        ------
        TypeError
            If the value is not a string.
        ValueError
            If the value is an empty string.
        """
        if value is None:
            self._name = self._generate_name()
        elif not isinstance(value, str):
            raise TypeError("`name` must be a string")
        elif not value.strip():
            raise ValueError("`name` cannot be empty")
        else:
            self._name = value.strip()

    @property
    def aliases(self) -> FrozenSet[str]:
        """The aliases for the argument."""
        return self._aliases

    @aliases.setter
    def aliases(self, value: Optional[List[str]] = None) -> None:
        if value:
            if self.name in value:
                raise ValueError(f"Alias cannot be the same as the argument name ('{self.name}').")
            if len(value) != len(set(value)):
                raise ValueError(f"Aliases must be unique for argument '{self.name}'. Found duplicates in {value}.")
            self._aliases = frozenset(value)
        else:
            self._aliases = frozenset()

    @property
    def class_name(self) -> str:
        """
        The name of the class.
    
        Returns
        -------
        str
            The name of the class of the object.
        """
        return self.__class__.__name__

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def tags(self) -> Set[str]:
        """
        The tags associated with the object.

        Returns
        -------
        Set[str]
            A set of tags.
        """
        return self._tags

    @tags.setter
    def tags(self, values: Optional[List[str]]) -> None:
        """
        Sets the tags for the object.

        Parameters
        ----------
        values : Optional[List[str]]
            A list of tags to set. If None, an empty set is used.

        Raises
        ------
        TypeError
            If any value in the list is not a string.
        """
        if values is None:
            self._tags = set()
        elif not all(isinstance(value, str) for value in values):
            raise TypeError("Every tag must be a string")
        else:
            self._tags = {value.strip() for value in values if value.strip()}

    def _generate_name(self) -> str:
        """
        Generates a unique name for the object.

        Returns
        -------
        str
            A unique name.
        """
        return uuid.uuid4().hex

    def rename(self, new_name: str) -> NamedObject:
        """
        Rename the object to a new name.

        Parameters
        ----------
        new_name : str
            The new name to assign to the object.

        Returns
        -------
        NamedObject
            The updated NamedObject instance (self).
        """
        self.name = new_name
        return self

    def add_tags(self, tags: Union[str, List[str]]):
        if isinstance(tags, str):
            tags = [tags]
        self._tags.update(tags)

    def remove_tags(self, tags: Union[str, List[str]]):
        if isinstance(tags, str):
            tags = [tags]
        self._tags.difference_update(tags)