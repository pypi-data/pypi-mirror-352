"""
A module providing a flexible tree data structure with named nodes.

This module implements a tree structure where each node has a name, optional data,
and can have multiple children. Nodes can be accessed using domain-style notation
(e.g., 'parent.child.grandchild') and support dict-like operations.

Examples
--------
>>> # Create a basic tree
>>> root = NamedTreeNode("root", data="root_data")
>>> root.add_child(NamedTreeNode("child1", "child1_data"))
>>> print(root)
root: 'root_data'
    child1: 'child1_data'

>>> # Use domain notation
>>> root.set("new_data", domain="child1")
>>> print(root.get(domain="child1"))
'new_data'

>>> # Use dictionary updates
>>> root |= {"name": "child2", "data": "child2_data", "children": {}}
>>> print(root)
root: 'root_data'
    child1: 'new_data'
    child2: 'child2_data'
"""
from __future__ import annotations

from typing import (
    Any, Optional, List, Dict, Union, Iterator, TypeVar, Generic, 
    Sequence, Mapping, ClassVar, Type
)
from dataclasses import dataclass
from functools import lru_cache
import copy
import re

from .enums import DescriptiveEnum
from .typing import NOTSET, generic_args
from .type_validation import check_type

# Type variables and aliases
T = TypeVar('T')
DomainType = Optional[str]
NodeData = TypeVar('NodeData')

class TraversalMode(DescriptiveEnum):
    """Traversal modes for tree iteration."""
    PRE_ORDER = (0, "Visit node, then children")
    POST_ORDER = (1, "Visit children, then node")
    BREADTH_FIRST = (2, "Visit level by level")

class TreeError(Exception):
    """Base exception for tree-related errors."""
    pass

class InvalidNodeError(TreeError):
    """Exception raised for invalid node operations."""
    pass

class DomainError(TreeError):
    """Exception raised for invalid domain operations."""
    pass

class ValidationError(TreeError):
    """Exception raised for data validation errors."""
    pass

@dataclass
class NodeConfig:
    """Configuration for tree nodes.
    
    Parameters
    ----------
    separator : str, default='.'
        Separator used for domain paths
    allow_empty_data : bool, default=True
        Whether to allow empty data
    validate_names : bool, default=False
        Whether to validate node names against pattern
    validate_data_type : bool, default=False
        Whether to validate data against the node's type parameter
    name_pattern : str, default=r'^[a-zA-Z][a-zA-Z0-9_]*$'
        Pattern for valid node names if validate_names is True
    """
    separator: str = '.'
    allow_empty_data: bool = True
    validate_names: bool = False  # Default to False for performance
    validate_data_type: bool = False  # Default to False for performance
    name_pattern: str = r'^[a-zA-Z][a-zA-Z0-9_]*$'

class NamedTreeNode(Generic[NodeData]):
    """
    A tree node with a name, optional data, and child nodes.
    
    This class implements a flexible tree structure where each node has:
    - A unique name within its parent's scope
    - Optional data of any type
    - Zero or more child nodes
    - Support for domain-style access (e.g., 'parent.child.grandchild')
    - Bidirectional traversal with parent references
    
    Attributes
    ----------
    name : str
        The name of the node
    data : Optional[NodeData]
        The data stored in the node
    children : Dict[str, NamedTreeNode]
        Dictionary of child nodes keyed by their names
    parent : Optional[NamedTreeNode]
        Reference to parent node or None if root
        
    Examples
    --------
    >>> # Create a basic tree
    >>> root = NamedTreeNode[str]("root", "root_data")
    >>> root.add_child(NamedTreeNode("child1", "child1_data"))
    >>> root["child2"] = "child2_data"
    
    >>> # Access data
    >>> print(root.get("child1"))
    'child1_data'
    >>> print(root["child2"])
    'child2_data'
    
    >>> # Update with dictionary
    >>> root |= {
    ...     "name": "child3",
    ...     "data": "child3_data",
    ...     "children": {}
    ... }
    
    >>> # Traverse the tree
    >>> for node in root.iter_subtree(mode=TraversalMode.PRE_ORDER):
    ...     print(node.name)
    """
    
    # Class-level configuration
    config: ClassVar[NodeConfig] = NodeConfig()
    
    def __init__(
        self, 
        name: str = 'root', 
        data: NodeData = NOTSET,
        separator: Optional[str] = None,
        parent: Optional[NamedTreeNode] = None
    ) -> None:
        """
        Initialize a named tree node.
        
        Parameters
        ----------
        name : str, default 'root'
            The name of the node. Must be a valid identifier.
        data : NodeData, default NOTSET
            The data to store in the node.
        separator : Optional[str], default None
            The separator to use for domain strings. If None, uses class default.
        parent : Optional[NamedTreeNode], default None
            Parent node reference for bidirectional traversal.
            
        Raises
        ------
        ValidationError
            If the name is invalid or data validation fails.
        """
        self._validate_name(name)
        self._name = name     
        self._data = data
        self._children = {}
        self._parent = parent
        self._data_type = None
        self._separator = separator or self.config.separator

    def _validate_name(self, name: str) -> None:
        """
        Validate node name.
        
        Parameters
        ----------
        name : str
            The name to validate
            
        Raises
        ------
        ValidationError
            If the name is invalid
        """
        if not isinstance(name, str):
            raise ValidationError(f"Name must be a string, got {type(name)}")
            
        if not name:
            raise ValidationError("Name cannot be empty")
            
        if self.config.validate_names:
            if not re.match(self.config.name_pattern, name):
                raise ValidationError(
                    f"Invalid name '{name}'. Must match pattern: {self.config.name_pattern}"
                )

    def _validate_data(self, data: Optional[NodeData]) -> Optional[NodeData]:
        """
        Validate node data.
        
        Parameters
        ----------
        data : Optional[NodeData]
            Data to validate
            
        Returns
        -------
        Optional[NodeData]
            Validated data
            
        Raises
        ------
        ValidationError
            If data validation fails
        """
        # Handle None data
        if data is NOTSET:
            if not self.config.allow_empty_data:
                raise ValidationError("Empty data not allowed")
            return NOTSET

        # Perform type validation if enabled and type is known
        if self.config.validate_data_type and self.data_type is not None:
            if not check_type(data, self.data_type):
                raise ValidationError(
                    f"Data type mismatch: expected {self._data_type.__name__}, "
                    f"got {type(data).__name__}"
                )
        
        return data

    @lru_cache(maxsize=128)
    def _split_domain(self, domain: Optional[str] = None) -> Tuple[str, ...]:
        """Split domain string into components."""
        if not domain:
            return tuple()
            
        if not isinstance(domain, str):
            domain = str(domain)
            
        return tuple(domain.split(self.separator))

    def __setitem__(self, domain: str, data: NodeData) -> None:
        """
        Set data for a node at the specified domain.
        
        Parameters
        ----------
        domain : str
            The domain path to the node
        data : NodeData
            The data to set
        
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child.grandchild"] = "data"
        >>> print(root["child.grandchild"])
        'data'
        """
        try:
            self.set(data=data, domain=domain)
        except Exception as e:
            raise DomainError(f"Failed to set item at '{domain}': {str(e)}") from e

    def __getitem__(self, domain: str) -> Optional[NodeData]:
        """
        Get data from a node at the specified domain.
        
        Parameters
        ----------
        domain : str
            The domain path to the node
            
        Returns
        -------
        NodeData
            The data at the specified domain
            
        Raises
        ------
        KeyError
            If the domain doesn't exist
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child"] = "data"
        >>> print(root["child"])
        'data'
        """
        return self.get(domain=domain, default=None, strict=True)

    def __or__(self, other: Union[NamedTreeNode[NodeData], Dict[str, Any]]) -> NamedTreeNode[NodeData]:
        """
        Combine this node with another node or dictionary.
        
        Parameters
        ----------
        other : Union[NamedTreeNode[NodeData], Dict[str, Any]]
            The other node or dictionary to combine with
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new node combining both trees
            
        Examples
        --------
        >>> node1 = NamedTreeNode[str]("node1", "data1")
        >>> node2 = NamedTreeNode[str]("node2", "data2")
        >>> combined = node1 | node2
        >>> print(combined.name)
        'node2'
        """
        if isinstance(other, dict):
            other = self.from_dict(other)
        elif not isinstance(other, NamedTreeNode):
            raise TypeError("Can only combine with another NamedTreeNode or dict")
            
        new_node = self.create(self._name, self._data)
        new_node.update(self)
        new_node.update(other)
        return new_node

    def __ior__(self, other: Union[NamedTreeNode[NodeData], Dict[str, Any]]) -> NamedTreeNode[NodeData]:
        """
        Update this node with another node or dictionary in-place.
        
        Parameters
        ----------
        other : Union[NamedTreeNode[NodeData], Dict[str, Any]]
            The other node or dictionary to update with
            
        Returns
        -------
        NamedTreeNode[NodeData]
            This node, updated
            
        Examples
        --------
        >>> node = NamedTreeNode[str]("node", "old_data")
        >>> node |= {"name": "node", "data": "new_data"}
        >>> print(node.data)
        'new_data'
        """
        self.update(other)
        return self

    def __ror__(self, other: Dict[str, Any]) -> NamedTreeNode[NodeData]:
        """
        Combine a dictionary with this node.
        
        Parameters
        ----------
        other : Dict[str, Any]
            The dictionary to combine with
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new node combining both
        """
        new_node = self.from_dict(other)
        return new_node | self

    def __contains__(self, domain: str) -> bool:
        """
        Check if a domain exists in the tree.
        
        Parameters
        ----------
        domain : str
            The domain to check for
            
        Returns
        -------
        bool
            True if the domain exists
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child"] = "data"
        >>> print("child" in root)
        True
        """
        try:
            return self.traverse_domain(domain, create=False) is not None
        except DomainError:
            return False

    def __copy__(self) -> NamedTreeNode[NodeData]:
        """Create a shallow copy."""
        new_node = self.create(self._name, self._data)
        new_node._children = self._children.copy()
        return new_node

    def __deepcopy__(self, memo: Dict[int, Any]) -> NamedTreeNode[NodeData]:
        """Create a deep copy."""
        new_node = self.create(self._name, copy.deepcopy(self._data, memo))
        new_node._children = {
            name: copy.deepcopy(child, memo) 
            for name, child in self._children.items()
        }
        return new_node

    def __repr__(self, level: int = 0) -> str:
        """
        Create a string representation of the tree.
        
        Parameters
        ----------
        level : int, default 0
            The current indentation level
            
        Returns
        -------
        str
            A formatted string representation
        """
        indent = "  " * level
        data_str = "" if self._data is NOTSET else repr(self._data)
        result = [f"{indent}{self._name}: {data_str}"]
        
        for child in self._children.values():
            result.append(child.__repr__(level + 1))
            
        return "\n".join(result)

    def __iter__(self) -> Iterator[NamedTreeNode[NodeData]]:
        """
        Iterate over child nodes.
        
        Yields
        ------
        NamedTreeNode[NodeData]
            Each child node
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child1"] = "data1"
        >>> root["child2"] = "data2"
        >>> for child in root:
        ...     print(child.name)
        child1
        child2
        """
        return iter(self._children.values())

    def __len__(self) -> int:
        """Return number of direct children."""
        return len(self._children)

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ) -> NamedTreeNode[NodeData]:
        """
        Create a new tree from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing node data and children
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new tree node
            
        Examples
        --------
        >>> data = {
        ...     "name": "root",
        ...     "data": "root_data",
        ...     "children": {
        ...         "child1": {
        ...             "name": "child1",
        ...             "data": "child1_data"
        ...         }
        ...     }
        ... }
        >>> root = NamedTreeNode[str].from_dict(data)
        """
        if not isinstance(data, dict):
            raise TypeError("Expected dictionary input")
            
        name = data.get('name', 'root')
        node_data = data.get('data', NOTSET)
        node = cls(name, node_data)
        
        children = data.get('children', {})
        if not isinstance(children, dict):
            raise TypeError("Children must be a dictionary")
            
        for child_name, child_data in children.items():
            child_node = cls.from_dict(child_data)
            child_node._parent = node
            node.add_child(child_node)
            
        return node

    @classmethod
    def from_mapping(
        cls,
        data: Mapping[str, NodeData]
    ) -> NamedTreeNode[NodeData]:
        """
        Create a new tree from a mapping.
        
        Parameters
        ----------
        data : Mapping[str, NodeData]
            Mapping containing node data
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new tree node
            
        Examples
        --------
        >>> data = {
        ...     None: "root_data",
        ...     "child1": "child1_data",
        ...     "child2": "child2_data"
        ... }
        >>> root = NamedTreeNode[str].from_mapping(data)
        """
        node = cls()
        node.set(data.get(None, NOTSET))
        
        for name, value in data.items():
            if name is not None:
                node[name] = value
                
        return node

    @classmethod
    def create(
        cls,
        name: str,
        data: NodeData = NOTSET
    ) -> NamedTreeNode[NodeData]:
        """
        Create a new tree node.
        
        Parameters
        ----------
        name : str
            Name for the node
        data : NodeData, default = NOTSET
            Data for the node
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A new tree node
        """
        return cls(name, data)

    @property
    def name(self) -> str:
        """Get the node's name."""
        return self._name

    @property
    def data(self) -> Optional[NodeData]:
        """
        Get the node's data.
        
        Returns
        -------
        Optional[NodeData]
            The data value or None if unset
        
        Notes
        -----
        This property returns None for both uninitialized nodes and nodes with
        an explicit None value. To distinguish between them, check self._data is NOTSET.
        """
        return self._data if self._data is not NOTSET else None

    @data.setter
    def data(self, value: NodeData) -> None:
        """Set the node's data."""
        self._data = self._validate_data(value)

    @property
    def separator(self) -> str:
        return self._separator

    @property
    def data_type(self) -> Type[NodeData]:
        """
        Concrete generic parameter or ``Any`` when the node was created
        without one (``TreeData()``).
        """
        if self._data_type is None:
            type_args = generic_args(self)
            self._data_type = type_args[0] if type_args else Any
        return self._data_type

    @property
    def parent(self) -> Optional[NamedTreeNode]:
        """
        Get the node's parent.
        
        Returns
        -------
        Optional[NamedTreeNode]
            The parent node or None if root
        """
        return self._parent

    @property
    def children(self) -> Dict[str, NamedTreeNode[NodeData]]:
        """
        Get the node's children.
        
        Returns
        -------
        Dict[str, NamedTreeNode[NodeData]]
            Dictionary of child nodes
        """
        return self._children.copy()

    @property
    def is_root(self) -> bool:
        """
        Check if node is a root node.
        
        Returns
        -------
        bool
            True if node has no parent
        """
        return self._parent is None

    @property
    def is_leaf(self) -> bool:
        """
        Check if node is a leaf node.
        
        Returns
        -------
        bool
            True if node has no children
        """
        return len(self._children) == 0

    @property
    def depth(self) -> int:
        """
        Get the depth of the node in the tree.
        
        Returns
        -------
        int
            Depth of the node (0 for root)
        """
        if self.is_root:
            return 0
        return 1 + self.parent.depth

    @property
    def height(self) -> int:
        """
        Get the height of the subtree rooted at this node.
        
        Returns
        -------
        int
            Height of the subtree (0 for leaf nodes)
        """
        if not self._children:
            return 0
        return 1 + max(child.height for child in self._children.values())

    @property
    def size(self) -> int:
        """
        Get the total number of nodes in the subtree.
        
        Returns
        -------
        int
            Number of nodes (1 for leaf nodes)
        """
        return 1 + sum(child.size for child in self._children.values())

    @property
    def namespaces(self) -> List[str]:
        """
        Get list of immediate child names.
        
        Returns
        -------
        List[str]
            List of child names
        """
        return list(self._children.keys())

    @property
    def domains(self) -> List[str]:
        """
        Get list of all domain paths in the tree.
        
        Returns
        -------
        List[str]
            List of domain paths
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["a.b"] = "data1"
        >>> root["a.c"] = "data2"
        >>> print(root.domains)
        ['a.b', 'a.c']
        """
        result = []
        for namespace, node in self._children.items():
            subdomains = node.domains
            if node._data is not NOTSET:
                result.append(namespace)
            # Add any subdomains
            if subdomains:
                result.extend([
                    self.format(namespace, subdomain)
                    for subdomain in subdomains
                ])
        return result

    def format(self, *components: Optional[str]) -> str:
        """
        Format domain components into a domain string.
        
        Parameters
        ----------
        *components : Optional[str]
            Domain components
            
        Returns
        -------
        str
            Formatted domain string
            
        Examples
        --------
        >>> root = NamedTreeNode("root")
        >>> print(root.format("a", "b", "c"))
        'a.b.c'
        """
        return self._separator.join(comp for comp in components if comp)

    @property
    def path(self) -> str:
        """
        Get the full path from root to this node.
        
        Returns
        -------
        str
            Full path from root
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> child = root.traverse_domain("a.b.c", create=True)
        >>> print(child.path)
        'root.a.b.c'
        """
        if self.is_root:
            return self.name
        
        path_components = []
        current = self
        while current is not None:
            path_components.append(current.name)
            current = current.parent
            
        return self.format(*reversed(path_components))

    def copy(self, deep: bool = False) -> NamedTreeNode[NodeData]:
        """
        Create a copy of the tree.
        
        Parameters
        ----------
        deep : bool, default False
            If True, creates a deep copy
            
        Returns
        -------
        NamedTreeNode[NodeData]
            A copy of the tree
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root", "data")
        >>> root["child"] = "child_data"
        >>> copy1 = root.copy()  # Shallow copy
        >>> copy2 = root.copy(deep=True)  # Deep copy
        """
        return self.__deepcopy__({}) if deep else self.__copy__()

    def add_child(self, child_node: NamedTreeNode[NodeData]) -> None:
        """
        Add a child node to the tree.
        
        Parameters
        ----------
        child_node : NamedTreeNode[NodeData]
            The child node to add
            
        Raises
        ------
        TypeError
            If child_node is not a NamedTreeNode
        ValidationError
            If child node validation fails
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> child = NamedTreeNode("child", "data")
        >>> root.add_child(child)
        """
        if not isinstance(child_node, NamedTreeNode):
            raise TypeError("Child must be a NamedTreeNode instance")
            
        self._validate_child(child_node)
        self._children[child_node.name] = child_node
        child_node._parent = self

    def _validate_child(self, child: NamedTreeNode[NodeData]) -> None:
        """
        Validate a child node before adding.
        
        Parameters
        ----------
        child : NamedTreeNode[NodeData]
            Child node to validate
            
        Raises
        ------
        ValidationError
            If validation fails
        """
        if child.name in self._children:
            raise ValidationError(f"Child name '{child.name}' already exists")

    def get_child(
        self, 
        name: str, 
        default: Optional[NamedTreeNode[NodeData]] = None
    ) -> Optional[NamedTreeNode[NodeData]]:
        """
        Get a child node by name.
        
        Parameters
        ----------
        name : str
            Name of the child node
        default : Optional[NamedTreeNode[NodeData]], default None
            Value to return if child doesn't exist
            
        Returns
        -------
        Optional[NamedTreeNode[NodeData]]
            The child node or default value
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child"] = "data"
        >>> child = root.get_child("child")
        >>> print(child.data)
        'data'
        """
        return self._children.get(name, default)

    def remove_child(self, name: str) -> Optional[NamedTreeNode[NodeData]]:
        """
        Remove and return a child node.
        
        Parameters
        ----------
        name : str
            Name of the child to remove
            
        Returns
        -------
        Optional[NamedTreeNode[NodeData]]
            The removed child node, or None if not found
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["child"] = "data"
        >>> removed = root.remove_child("child")
        >>> print(removed.data)
        'data'
        """
        child = self._children.pop(name, None)
        if child is not None:
            child._parent = None
        return child

    def find(
        self, 
        predicate: Callable[[NamedTreeNode[NodeData]], bool]
    ) -> Optional[NamedTreeNode[NodeData]]:
        """
        Find first node that matches a predicate.
        
        Parameters
        ----------
        predicate : Callable[[NamedTreeNode[NodeData]], bool]
            Function that tests each node
            
        Returns
        -------
        Optional[NamedTreeNode[NodeData]]
            First node that matches or None
            
        Examples
        --------
        >>> root = NamedTreeNode[int]("root", 0)
        >>> root["a.b"] = 10
        >>> root["a.c"] = 20
        >>> node = root.find(lambda n: n.data == 10)
        >>> print(node.path)
        'root.a.b'
        """
        if predicate(self):
            return self
            
        for child in self._children.values():
            found = child.find(predicate)
            if found is not None:
                return found
                
        return None

    def find_all(
        self, 
        predicate: Callable[[NamedTreeNode[NodeData]], bool]
    ) -> List[NamedTreeNode[NodeData]]:
        """
        Find all nodes that match a predicate.
        
        Parameters
        ----------
        predicate : Callable[[NamedTreeNode[NodeData]], bool]
            Function that tests each node
            
        Returns
        -------
        List[NamedTreeNode[NodeData]]
            All nodes that match
            
        Examples
        --------
        >>> root = NamedTreeNode[int]("root", 0)
        >>> root["a.b"] = 10
        >>> root["a.c"] = 10
        >>> nodes = root.find_all(lambda n: n.data == 10)
        >>> print(len(nodes))
        2
        """
        result = []
        
        if predicate(self):
            result.append(self)
            
        for child in self._children.values():
            result.extend(child.find_all(predicate))
            
        return result

    def get_leaf_nodes(self) -> List[NamedTreeNode[NodeData]]:
        """
        Get all leaf nodes in the tree.
        
        Returns
        -------
        List[NamedTreeNode[NodeData]]
            List of leaf nodes
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["a.b"] = "data1"
        >>> root["a.c"] = "data2"
        >>> leaves = root.get_leaf_nodes()
        >>> print(len(leaves))
        2
        """
        return self.find_all(lambda n: n.is_leaf)

    def traverse(
        self, 
        *namespaces: str,
        create: bool = False
    ) -> Optional[NamedTreeNode[NodeData]]:
        """
        Traverse the tree through multiple namespaces.
        
        Parameters
        ----------
        *namespaces : str
            Sequence of namespace names to traverse
        create : bool, default False
            Whether to create missing nodes during traversal
            
        Returns
        -------
        Optional[NamedTreeNode[NodeData]]
            The final node or None if not found
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> node = root.traverse("a", "b", "c", create=True)
        >>> node.data = "data"
        >>> print(root["a.b.c"])
        'data'
        """
        node = self
        for namespace in namespaces:
            if not namespace:
                continue
                
            subnode = node._children.get(namespace)
            if subnode is None:
                if create:
                    subnode = self.create(namespace)
                    node.add_child(subnode)
                else:
                    return None
            node = subnode
        return node

    def traverse_domain(
        self, 
        domain: Optional[str] = None,
        create: bool = False
    ) -> Optional[NamedTreeNode[NodeData]]:
        """
        Traverse the tree using a domain string.
        
        Parameters
        ----------
        domain : Optional[str]
            Domain path (e.g., "parent.child.grandchild")
        create : bool, default False
            Whether to create missing nodes during traversal
            
        Returns
        -------
        Optional[NamedTreeNode[NodeData]]
            The final node or None if not found
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> node = root.traverse_domain("a.b.c", create=True)
        >>> node.data = "data"
        >>> print(root.get("a.b.c"))
        'data'
        """
        components = self._split_domain(domain)
        return self.traverse(*components, create=create)

    def iter_subtree(
        self, 
        mode: str = TraversalMode.PRE_ORDER
    ) -> Iterator[NamedTreeNode[NodeData]]:
        """
        Iterate through all nodes in the subtree.
        
        Parameters
        ----------
        mode : str
            Traversal mode (pre_order, post_order, breadth_first)
            
        Yields
        ------
        NamedTreeNode[NodeData]
            Each node in the subtree
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["a.b"] = "data1"
        >>> root["a.c"] = "data2"
        >>> for node in root.iter_subtree():
        ...     print(node.name)
        root
        a
        b
        c
        """
        mode = TraversalMode.parse(mode)
        if mode == TraversalMode.PRE_ORDER:
            yield self
            for child in self._children.values():
                yield from child.iter_subtree(mode)
        elif mode == TraversalMode.POST_ORDER:
            for child in self._children.values():
                yield from child.iter_subtree(mode)
            yield self
        elif mode == TraversalMode.BREADTH_FIRST:
            queue = [self]
            while queue:
                node = queue.pop(0)
                yield node
                queue.extend(node._children.values())
        else:
            raise ValueError(f"Invalid traversal mode: {mode}")

    def extract_subtree(self) -> NamedTreeNode[NodeData]:
        """
        Extract this node and its descendants as a new tree.
        
        Returns
        -------
        NamedTreeNode[NodeData]
            A new tree with this node as the root
        """
        new_tree = self.copy(deep=True)
        new_tree._parent = None
        return new_tree            

    def get_ancestor(self, levels: int = 1) -> Optional[NamedTreeNode[NodeData]]:
        """Get ancestor node n levels up."""
        if levels <= 0:
            return self
        
        current = self.parent
        for _ in range(1, levels):
            if current is None:
                return None
            current = current.parent
        
        return current

    def get_root(self) -> NamedTreeNode[NodeData]:
        """Get the root node of this tree."""
        current = self
        while current.parent is not None:
            current = current.parent
        return current

    def get(
        self,
        domain: Optional[str] = None,
        default: Any = None,
        strict: bool = False
    ) -> Optional[NodeData]:
        """
        Get data from a node at the specified domain.
        
        Parameters
        ----------
        domain : Optional[str]
            Domain path to the node
        default : Any, default None
            Value to return if node not found or node has no data
        strict : bool, default False
            If True, raises KeyError for missing nodes
            
        Returns
        -------
        Optional[NodeData]
            The node's data or default value
            
        Raises
        ------
        KeyError
            If strict=True and node not found
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["a.b"] = "data"
        >>> print(root.get("a.b"))
        'data'
        >>> print(root.get("x.y", default="not found"))
        'not found'
        """
        node = self.traverse_domain(domain)
        if strict and node is None:
            raise KeyError(f"Domain not found: '{domain}'")
        if (node is None) or (node._data is NOTSET):
            return default
        return node.data

    def set(
        self,
        data: NodeData,
        domain: Optional[str] = None
    ) -> None:
        """
        Set data for a node at the specified domain.
        
        Parameters
        ----------
        data : NodeData
            The data to set
        domain : Optional[str]
            Domain path to the node
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root.set("data", "a.b.c")
        >>> print(root.get("a.b.c"))
        'data'
        """
        node = self.traverse_domain(domain, create=True)
        if node is not None:
            node._data = self._validate_data(data)

    def update(
        self,
        other: Union[NamedTreeNode[NodeData], Dict[str, Any]]
    ) -> None:
        """
        Update the tree with another tree or dictionary.
        
        Parameters
        ----------
        other : Union[NamedTreeNode[NodeData], Dict[str, Any]]
            The source to update from
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root.update({
        ...     "name": "root",
        ...     "data": "new_data",
        ...     "children": {
        ...         "child": {"name": "child", "data": "child_data"}
        ...     }
        ... })
        """
        if isinstance(other, dict):
            other = self.from_dict(other)
        elif not isinstance(other, NamedTreeNode):
            raise TypeError(
                "Expected NamedTreeNode or dict, "
                f"got {type(other).__name__}"
            )

        # Update name and data
        self._name = other.name
        self._data = self._validate_data(other.data)

        # Update children
        for name, child in other._children.items():
            if name in self._children:
                self._children[name].update(child)
            else:
                new_child = child.copy(deep=True)
                new_child._parent = self
                self._children[name] = new_child

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tree to a dictionary representation.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the tree
            
        Examples
        --------
        >>> root = NamedTreeNode[str]("root", "data")
        >>> root["child"] = "child_data"
        >>> dict_repr = root.to_dict()
        >>> print(dict_repr['children']['child']['data'])
        'child_data'
        """
        result = {
            'name': self._name
        }
        if (self._data is not NOTSET):
            result['data'] = self._data
        result['children'] = {
            name: child.to_dict()
            for name, child in self._children.items()
        }
        return result

    def clear(self) -> None:
        """
        Remove all children from the tree.
        
        Examples
        --------
        >>> root = NamedTreeNode[str]("root")
        >>> root["a"] = "data1"
        >>> root["b"] = "data2"
        >>> root.clear()
        >>> print(len(root.children))
        0
        """
        for child in self._children.values():
            child._parent = None
        self._children.clear()

    def merge(
        self,
        other: NamedTreeNode[NodeData],
        strategy: str = 'replace'
    ) -> None:
        """
        Merge another tree into this one.
        
        Parameters
        ----------
        other : NamedTreeNode[NodeData]
            The tree to merge from
        strategy : str, default 'replace'
            Merge strategy ('replace' or 'keep')
            
        Examples
        --------
        >>> tree1 = NamedTreeNode[str]("root")
        >>> tree1["a"] = "data1"
        >>> tree2 = NamedTreeNode[str]("root")
        >>> tree2["b"] = "data2"
        >>> tree1.merge(tree2)
        """
        if not isinstance(other, NamedTreeNode):
            raise TypeError("Can only merge with another NamedTreeNode")
            
        if strategy not in {'replace', 'keep'}:
            raise ValueError(
                "Invalid merge strategy. Must be 'replace' or 'keep'"
            )
            
        # Merge data if needed
        if strategy == 'replace' or self._data is NOTSET:
            self._data = self._validate_data(other.data)
            
        # Merge children
        for name, other_child in other._children.items():
            if name in self._children:
                self._children[name].merge(other_child, strategy)
            else:
                new_child = other_child.copy(deep=True)
                new_child._parent = self
                self._children[name] = new_child