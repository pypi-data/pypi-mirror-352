from __future__ import annotations

from typing import List, Set, Optional, Dict, Union, Type, Tuple, Any

from quickstats import NamedObject
from quickstats.core.typing import NOTSET
from quickstats.utils.string_utils import PlainStr

class Argument(NamedObject):
    """
    Represents an argument with a name, value, and optional description and tags.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        value: Any = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        verbosity: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            name=name,
            aliases=aliases,
            tags=tags,
            description=description,
            verbosity=verbosity,
            **kwargs
        )
        self.value = value

    def _repr_dict_(self) -> Dict[str, Optional[str]]:
        repr_items = super()._repr_dict_()
        repr_items["value"] = self.value
        return repr_items  

    @property
    def value(self) -> Any:
        """The current value of the argument."""
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        """
        Set the value of the argument with validation.

        Raises
        ------
        ValueError
            If the value does not meet the validation requirements.
        """
        try:
            value = self.validate_value(value)
        except Exception as e:
            raise ValueError(
                f"Failed to set value for Argument '{self.name}': {e}"
            ) from e
        self._value = value

    def validate_value(self, value: Any) -> Any:
        return value


class ArgumentSet(NamedObject):
    """
    Represents a collection of Arguments with additional management functionality.

    Attributes
    ----------
    type : Union[Type, Tuple[Type]]
        The allowed type(s) for the components in the ArgumentSet. Must be a subclass of Argument.
    components : Dict[str, Argument]
        The components stored in the ArgumentSet.
    """

    def __init__(
        self,
        components: Optional[Union[List[Argument], Tuple[Argument, ...], ArgumentSet]] = None,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        type: Union[Type[Argument], Tuple[Type[Argument], ...]] = Argument,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        verbosity: Optional[str] = None,
        **kwargs
    ):
        super().__init__(name=name, aliases=aliases, tags=tags, verbosity=verbosity, **kwargs)
        self._type = None
        self.type = type
        self._is_locked = False
        self._components = {}
        self._alias_to_name: Dict[str, str] = {}
        self.append(components or [])

    def _resolve_name(self, name_or_alias: str, strict: bool = True) -> Optional[str]:
        """Resolves an alias to its primary name if it's an alias, otherwise returns the input."""
        if name_or_alias in self._components:
            return name_or_alias
        if name_or_alias in self._alias_to_name:
            return self._alias_to_name[name_or_alias]
        if strict:
            raise KeyError(f"Component with name or alias '{name_or_alias}' not found.")
        return None

    def _check_name(self, name: str) -> None:
        """Ensure that a component with the given name exists."""
        if not self.contains(name):
            raise KeyError(f"Component with name '{name}' not found.")
        
    def __getitem__(self, key: Union[str, int, slice]) -> Union[Argument, ArgumentSet]:
        """
        Retrieve a component by name, index, or slice.
    
        Parameters
        ----------
        key : Union[str, int, slice]
            The key to retrieve the component. It can be:
            - A string (name of the component).
            - An integer (index of the component in insertion order).
            - A slice (range of indices).
    
        Returns
        -------
        Union[Argument, ArgumentSet]
            The requested component if a single name or index is provided,
            or a new ArgumentSet if a slice is provided.
    
        Raises
        ------
        KeyError
            If the provided key is a string and does not exist in the ArgumentSet.
        IndexError
            If the key is an integer or slice and is out of range.
        TypeError
            If the key is not of a supported type.
        """
        if isinstance(key, str):
            name = self._resolve_name(key, strict=True)
            return self._components[name]
    
        elif isinstance(key, int):
            try:
                name = list(self._components.keys())[key]
                return self._components[name]
            except IndexError:
                raise IndexError(f"Index {key} is out of range.")
    
        elif isinstance(key, slice):
            names = list(self._components.keys())[key]
            return self.select(names=names, new_name=f"{self.name}_slice")
    
        else:
            raise TypeError("Key must be a string, integer, or slice.")

    def __contains__(self, key: str) -> bool:
        """Checks if a name or alias exists in the set."""
        return key in self._components or key in self._alias_to_name

    def __len__(self) -> int:
        """
        Return the number of components in the ArgumentSet.

        Returns
        -------
        int
            The number of components in the ArgumentSet.

        Examples
        --------
        >>> arg_set = ArgumentSet()
        >>> len(arg_set)
        0
        >>> arg_set.append(Argument(name="arg1"))
        >>> len(arg_set)
        1
        """
        return len(self._components)
        
    @property
    def components(self) -> Dict[str, Argument]:
        return self._components

    @components.setter
    def components(
        self, values: Union[List[Argument], Tuple[Argument, ...], ArgumentSet]
    ) -> None:
        """
        Set the components for the ArgumentSet.

        Parameters
        ----------
        values : Union[List[Argument], Tuple[Argument, ...], ArgumentSet]
            A list, tuple, or ArgumentSet of Argument objects to add.

        Raises
        ------
        TypeError
            If a component is not of the allowed type.
        ValueError
            If a component with a duplicate name is found.
        """
        self._on_modify()
        self.clear()
        self.append(values)

    @property
    def type(self) -> Union[Type[Argument], Tuple[Type[Argument], ...]]:
        return self._type

    @type.setter
    def type(self, value: Union[Type[Argument], Tuple[Type[Argument], ...]]) -> None:
        """
        Set the type property, which can only be set once.

        Parameters
        ----------
        value : Union[Type[Argument], Tuple[Type[Argument], ...]]
            The allowed type(s) for the components in the ArgumentSet.

        Raises
        ------
        TypeError
            If the value is not a type or a tuple of types, or if it is not a subclass of Argument.
        ValueError
            If the type property is already initialized.
        """
        if self._type is not None:
            raise ValueError("The `type` property can only be set once.")

        if not isinstance(value, (type, tuple)):
            raise TypeError("`type` must be a type or a tuple of types.")
        if isinstance(value, tuple):
            if not all(isinstance(t, type) for t in value):
                raise TypeError("All elements in `type` tuple must be types.")
            if not all(issubclass(t, Argument) for t in value):
                raise TypeError("All elements in `type` tuple must be subclasses of `Argument`.")
        elif not issubclass(value, Argument):
            raise TypeError("`type` must be a subclass of `Argument`.")

        self._type = value

    @property
    def names(self) -> List[str]:
        """
        Get the list of names of all components in the ArgumentSet.
    
        Returns
        -------
        List[str]
            A list of component names.
        """
        return list(self._components.keys())

    @property
    def values(self) -> Dict[str, Any]:
        """
        Get a dictionary of component names mapped to their values.
    
        Returns
        -------
        Dict[str, Any]
            A dictionary where the keys are component names and the values are the `value` attributes of the components.
        """
        return {name: component.value for name, component in self._components.items()}

    @property
    def size(self) -> int:
        """Return the number of components in the ArgumentSet."""
        return len(self)

    @property
    def first(self) -> Optional[Argument]:
        """Return the first component in the ArgumentSet, or None if empty."""
        return next(iter(self._components.values()), None)

    @property
    def last(self) -> Optional[Argument]:
        """Return the last component in the ArgumentSet, or None if empty."""
        return next(reversed(self._components.values()), None)

    def _repr_dict_(self) -> Dict[str, Optional[str]]:
        repr_items = super()._repr_dict_()
        repr_items.update({
            "type": self.type.__name__ if isinstance(self.type, type) else [t.__name__ for t in self.type],
            "components": PlainStr(f'[{", ".join(self.names)}]'),
        })
        return repr_items

    def _on_modify(self):
        if self._is_locked:
            raise RuntimeError(f'Failed to modify {self.name}: components are locked')

    def _validate_components(self):
        pass

    def contains(self, name_or_alias: str) -> bool:
        """Check if a component with the given name or alias exists."""
        return name_or_alias in self

    def append(
        self,
        value: Union[Argument, List[Argument], Tuple[Argument, ...], ArgumentSet]
    ) -> None:
        """
        Add components to the ArgumentSet.

        Parameters
        ----------
        value : Union[Argument, List[Argument], Tuple[Argument, ...], ArgumentSet]
            A single Argument, a list/tuple of Arguments, or another ArgumentSet.

        Raises
        ------
        TypeError
            If a component is not of the allowed type.
        ValueError
            If a component with a duplicate name is found.
        """
        if isinstance(value, Argument):
            self._add_component(value)
        elif isinstance(value, (list, tuple)):
            for v in value:
                self._add_component(v)
        elif isinstance(value, ArgumentSet):
            for v in value.components.values():
                self._add_component(v)
        else:
            raise TypeError(
                f"`append` expects an Argument, a list/tuple of Arguments, or an ArgumentSet, got {type(value)}."
            )

    def _add_component(self, arg: Argument) -> None:
        """
        Add a single component to the ArgumentSet.

        Parameters
        ----------
        arg : Argument
            The component to add.

        Raises
        ------
        TypeError
            If the component is not of the allowed type.
        ValueError
            If a component with the same name already exists in the set.
        """
        self._on_modify()
        if not isinstance(arg, self.type):
            raise TypeError(f"Component '{arg}' must be of type {self.type}.")
        if arg.name in self._components:
            raise ValueError(f"Argument with name '{arg.name}' already exists in this set.")
        if arg.name in self._alias_to_name:
            raise ValueError(
                f"Name '{arg.name}' conflicts with an existing alias for argument '{self._alias_to_name[arg.name]}'."
            )
        for alias in arg.aliases:
            if alias == arg.name:
                raise ValueError(
                    f"Alias '{alias}' cannot be the same as the argument name for '{arg.name}'."
                )
            if alias in self._alias_to_name:
                raise ValueError(
                    f"Alias '{alias}' for argument '{arg.name}' conflicts with an existing alias for argument '{self._alias_to_name[alias]}'."
                )
            if alias in self._components:
                raise ValueError(
                    f"Alias '{alias}' for argument '{arg.name}' conflicts with an existing argument name."
                )
        self._components[arg.name] = arg
        for alias in arg.aliases:
            self._alias_to_name[alias] = arg.name
        
        self._validate_components()

    def _clone(
        self,
        components: Optional[Union[List[Argument], Tuple[Argument, ...], ArgumentSet]] = None,
        name: Optional[str] = None
    ):
        return type(self)(
            components=components,
            name=name,
            type=self.type,
            description=self.description,
            tags=list(self.tags),
            verbosity=self.init_verbosity
        )

    def select(
        self,
        names: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        class_names: Optional[List[str]] = None,
        new_name: Optional[str] = None,
        to_list: bool = False
    ) -> ArgumentSet:
        """
        Select a subset of components based on names (or aliases), tags, or class names.
        If both a name and its alias are in the 'names' list, the argument is included once.
        Parameters
        ----------
        names : Optional[List[str]], optional
            A list of names (or aliases) to select. If None, no filtering by name is applied.
        tags : Optional[List[str]], optional
            A list of tags to filter by. If None, no filtering by tags is applied.
        class_names : Optional[List[str]], optional
            A list of class names to filter by. If None, no filtering by class names is applied.
        new_name : Optional[str], optional
            The name of the resulting ArgumentSet. Defaults to None.
    
        Returns
        -------
        ArgumentSet
            A new ArgumentSet containing the selected components.
        """
        new_name = new_name or f"{self.name}_selected"

        if (names is not None and not names) or \
           (tags is not None and not tags) or \
           (class_names is not None and not class_names):
                return self._clone(components=[], name=new_name)
        
        selected_names = None
        if names is not None:
            selected_names = set()
            for name in names:
                resolved_name = self._resolve_name(name, strict=False)
                if resolved_name is not None:
                    selected_names.add(resolved_name)
                    
        selected_components: List[Argument] = []
        for name, component in self._components.items():
            if selected_names is not None and name not in selected_names:
                continue
            if tags is not None and not (component.tags and set(tags) & component.tags):
                continue
            if class_names is not None and component.class_name not in class_names:
                continue
            selected_components.append(component)

        if to_list:
            return selected_components
        return self._clone(components=selected_components, name=new_name)

    def get(self, name_or_alias: str) -> Argument:
        """Retrieve a component by name or alias."""
        name = self._resolve_name(name_or_alias, strict=True)
        return self._components[name]

    def delete(self, name_or_alias: str) -> None:
        """Remove a component by name or alias."""
        self.pop(name_or_alias, default=NOTSET)

    def clear(self) -> None:
        """Remove all components."""
        self._on_modify()
        self._components.clear()
        self._alias_to_name.clear()
        self._validate_components()

    def pop(self, name_or_alias: str, default: Optional[Any] = NOTSET) -> Optional[Argument]:
        """
        Remove and return a component by name or alias. If the name or alias does not exist,
        return the default value if provided.

        Parameters
        ----------
        name_or_alias : str
            The name or alias of the component to pop.
        default : Optional[Any], optional
            The value to return if the name or alias does not exist. Defaults to None.

        Returns
        -------
        Optional[Argument]
            The removed component, or the default value if the name or alias does not exist.
        """
        self._on_modify()
        name = self._resolve_name(name_or_alias, strict=default is NOTSET)
        if name is None or name not in self._components:
            return default
        component = self._components.pop(name)
        aliases_to_remove = [alias for alias, p_name in self._alias_to_name.items() if p_name == name]
        for alias in aliases_to_remove:
            del self._alias_to_name[alias]
        self._validate_components()
        return component