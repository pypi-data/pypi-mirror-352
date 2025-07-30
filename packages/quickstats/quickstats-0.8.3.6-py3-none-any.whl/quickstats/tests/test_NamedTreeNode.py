"""
Unit tests for the NamedTreeNode class.
"""

import unittest
from typing import Optional, Dict, Any, List
import copy

from quickstats.tree import NamedTreeNode


class TestNamedTreeNodeInit(unittest.TestCase):
    """Test NamedTreeNode initialization and basic properties."""

    def test_init_defaults(self) -> None:
        """Test default initialization."""
        node = NamedTreeNode[str]()
        self.assertEqual(node.name, "root")
        self.assertIsNone(node.data)
        self.assertEqual(len(node._children), 0)
        self.assertEqual(node._separator, ".")

    def test_init_custom(self) -> None:
        """Test initialization with custom values."""
        node = NamedTreeNode[str]("custom", "data", separator="|")
        self.assertEqual(node.name, "custom")
        self.assertEqual(node.data, "data")
        self.assertEqual(node._separator, "|")

    def test_init_validation(self) -> None:
        """Test initialization validation."""
        # Invalid name types
        with self.assertRaises(ValueError):
            NamedTreeNode[str](123)  # type: ignore
        
        # Empty name
        with self.assertRaises(ValueError):
            NamedTreeNode[str]("")
            
        # Invalid name characters
        with self.assertRaises(ValueError):
            NamedTreeNode[str]("invalid name")
        
        # Invalid separator
        with self.assertRaises(ValueError):
            NamedTreeNode[str]("valid", separator="")


class TestNamedTreeNodeProperties(unittest.TestCase):
    """Test NamedTreeNode properties and attribute access."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root", "root_data")
        self.node["child1"] = "data1"
        self.node["child2.grandchild"] = "data2"

    def test_name_property(self) -> None:
        """Test name property access."""
        self.assertEqual(self.node.name, "root")
        
        # Name should be read-only
        with self.assertRaises(AttributeError):
            self.node.name = "new_name"  # type: ignore

    def test_data_property(self) -> None:
        """Test data property access and modification."""
        self.assertEqual(self.node.data, "root_data")
        
        # Data should be read-only through property
        with self.assertRaises(AttributeError):
            self.node.data = "new_data"  # type: ignore

    def test_namespaces_property(self) -> None:
        """Test namespaces property."""
        self.assertEqual(set(self.node.namespaces), {"child1", "child2"})
        
        # Empty node
        empty_node = NamedTreeNode[str]()
        self.assertEqual(empty_node.namespaces, [])

    def test_domains_property(self) -> None:
        """Test domains property."""
        expected_domains = {"child1", "child2.grandchild"}
        self.assertEqual(set(self.node.domains), expected_domains)
        
        # Test nested domains
        self.node["a.b.c.d"] = "nested"
        self.assertIn("a.b.c.d", self.node.domains)


class TestNamedTreeNodeOperations(unittest.TestCase):
    """Test NamedTreeNode operations (add, remove, get, set)."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root")

    def test_add_child(self) -> None:
        """Test adding child nodes."""
        # Add simple child
        child = NamedTreeNode[str]("child", "data")
        self.node.add_child(child)
        self.assertEqual(self.node["child"], "data")
        
        # Add with existing name
        with self.assertRaises(ValueError):
            self.node.add_child(child)
        
        # Add invalid type
        with self.assertRaises(TypeError):
            self.node.add_child("not_a_node")  # type: ignore
            
        # Add child with invalid name
        invalid_child = NamedTreeNode[str]("invalid.name", "data")
        with self.assertRaises(ValueError):
            self.node.add_child(invalid_child)

    def test_get_child(self) -> None:
        """Test getting child nodes."""
        child = NamedTreeNode[str]("child", "data")
        self.node.add_child(child)
        
        # Get existing child
        self.assertEqual(self.node.get_child("child"), child)
        
        # Get non-existent child
        self.assertIsNone(self.node.get_child("missing"))
        
        # Get with custom default
        default = NamedTreeNode[str]("default")
        self.assertEqual(
            self.node.get_child("missing", default),
            default
        )

    def test_remove_child(self) -> None:
        """Test removing child nodes."""
        self.node["child"] = "data"
        
        # Remove existing child
        removed = self.node.remove_child("child")
        self.assertEqual(removed.data, "data")
        self.assertNotIn("child", self.node)
        
        # Remove non-existent child
        self.assertIsNone(self.node.remove_child("missing"))


class TestNamedTreeNodeTraversal(unittest.TestCase):
    """Test NamedTreeNode traversal methods."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root", "root_data")
        self.node["a.b.c"] = "abc_data"
        self.node["a.b.d"] = "abd_data"
        self.node["x.y"] = "xy_data"

    def test_traverse(self) -> None:
        """Test traverse method."""
        # Traverse existing path
        node = self.node.traverse("a", "b", "c")
        self.assertEqual(node.data, "abc_data")
        
        # Traverse non-existent path without creation
        self.assertIsNone(self.node.traverse("a", "b", "missing"))
        
        # Traverse with path creation
        node = self.node.traverse("new", "path", create=True)
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "path")
        
        # Traverse with empty components
        self.assertEqual(
            self.node.traverse("a", "", "b", "c"),
            self.node.traverse("a", "b", "c")
        )

    def test_traverse_domain(self) -> None:
        """Test domain-based traversal."""
        # Traverse existing domain
        node = self.node.traverse_domain("a.b.c")
        self.assertEqual(node.data, "abc_data")
        
        # Traverse with different separator
        node_pipe = NamedTreeNode[str]("root", separator="|")
        node_pipe["a|b|c"] = "data"
        self.assertEqual(node_pipe.traverse_domain("a|b|c").data, "data")
        
        # Invalid domain type
        with self.assertRaises(TypeError):
            self.node.traverse_domain(123)  # type: ignore


class TestNamedTreeNodeDataAccess(unittest.TestCase):
    """Test NamedTreeNode data access methods."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root", "root_data")

    def test_get(self) -> None:
        """Test get method."""
        # Get root data
        self.assertEqual(self.node.get(), "root_data")
        
        # Get with domain
        self.node["a.b"] = "ab_data"
        self.assertEqual(self.node.get("a.b"), "ab_data")
        
        # Get non-existent with default
        self.assertEqual(self.node.get("missing", default="default"), "default")
        
        # Get with strict mode
        with self.assertRaises(KeyError):
            self.node.get("missing", strict=True)

    def test_set(self) -> None:
        """Test set method."""
        # Set root data
        self.node.set("new_data")
        self.assertEqual(self.node.data, "new_data")
        
        # Set with domain
        self.node.set("domain_data", "a.b.c")
        self.assertEqual(self.node.get("a.b.c"), "domain_data")
        
        # Set with validation
        with self.assertRaises(ValueError):
            self.node.set({"invalid": "data"})  # type: ignore

    def test_item_access(self) -> None:
        """Test dictionary-style item access."""
        # Set and get
        self.node["a.b"] = "ab_data"
        self.assertEqual(self.node["a.b"], "ab_data")
        
        # Delete
        del self.node["a.b"]
        self.assertNotIn("a.b", self.node)
        
        # Get non-existent
        with self.assertRaises(KeyError):
            _ = self.node["missing"]


class TestNamedTreeNodeUpdate(unittest.TestCase):
    """Test NamedTreeNode update methods."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root", "root_data")
        self.node["a"] = "a_data"
        self.node["b.c"] = "bc_data"

    def test_update_from_dict(self) -> None:
        """Test updating from dictionary."""
        update_dict = {
            "name": "root",
            "data": "new_data",
            "children": {
                "a": {"name": "a", "data": "new_a_data"},
                "d": {"name": "d", "data": "d_data"}
            }
        }
        self.node.update(update_dict)
        
        self.assertEqual(self.node.data, "new_data")
        self.assertEqual(self.node["a"], "new_a_data")
        self.assertEqual(self.node["d"], "d_data")
        self.assertEqual(self.node["b.c"], "bc_data")  # Unchanged

    def test_update_from_node(self) -> None:
        """Test updating from another node."""
        other = NamedTreeNode[str]("root", "other_data")
        other["a"] = "other_a_data"
        other["x"] = "x_data"
        
        self.node.update(other)
        
        self.assertEqual(self.node.data, "other_data")
        self.assertEqual(self.node["a"], "other_a_data")
        self.assertEqual(self.node["x"], "x_data")
        self.assertEqual(self.node["b.c"], "bc_data")  # Unchanged

    def test_merge(self) -> None:
        """Test merge method."""
        other = NamedTreeNode[str]("root", "other_data")
        other["a"] = "other_a_data"
        other["b.d"] = "bd_data"
        
        # Test replace strategy
        self.node.merge(other, strategy='replace')
        self.assertEqual(self.node.data, "other_data")
        self.assertEqual(self.node["a"], "other_a_data")
        self.assertEqual(self.node["b.c"], "bc_data")
        self.assertEqual(self.node["b.d"], "bd_data")
        
        # Test keep strategy
        node2 = NamedTreeNode[str]("root", "keep_data")
        node2.merge(other, strategy='keep')
        self.assertEqual(node2.data, "keep_data")
        
        # Test invalid strategy
        with self.assertRaises(ValueError):
            self.node.merge(other, strategy='invalid')


class TestNamedTreeNodeSerialization(unittest.TestCase):
    """Test NamedTreeNode serialization methods."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root", "root_data")
        self.node["a"] = "a_data"
        self.node["b.c"] = "bc_data"

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        data = self.node.to_dict()
        
        self.assertEqual(data["name"], "root")
        self.assertEqual(data["data"], "root_data")
        self.assertIn("a", data["children"])
        self.assertIn("b", data["children"])
        self.assertIn("c", data["children"]["b"]["children"])

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        data = {
            "name": "root",
            "data": "root_data",
            "children": {
                "a": {
                    "name": "a",
                    "data": "a_data"
                },
                "b": {
                    "name": "b",
                    "data": None,
                    "children": {
                        "c": {
                            "name": "c",
                            "data": "bc_data"
                        }
                    }
                }
            }
        }
        
        node = NamedTreeNode[str].from_dict(data)
        self.assertEqual(node.name, "root")
        self.assertEqual(node.data, "root_data")
        self.assertEqual(node["a"], "a_data")
        self.assertEqual(node["b.c"], "bc_data")

    def test_from_mapping(self) -> None:
        """Test creation from mapping."""
        data = {
            None: "root_data",
            "a": "a_data",
            "b.c": "bc_data"
        }
        
        node = NamedTreeNode[str].from_mapping(data)
        self.assertEqual(node.data, "root_data")
        self.assertEqual(node["a"], "a_data")
        self.assertEqual(node["b.c"], "bc_data")


class TestNamedTreeNodeCopy(unittest.TestCase):
    """Test NamedTreeNode copying."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root", "root_data")
        self.node["a"] = "a_data"
        self.node["b.c"] = "bc_data"

    def test_shallow_copy(self) -> None:
        """Test shallow copy."""
        copied = self.node.copy(deep=False)
        
        # Test independence
        copied["new"] = "new_data"
        self.assertNotIn("new", self.node)
        
        # Test shared references
        copied["a"] = "modified"
        self.assertEqual(self.node["a"], "a_data")  # Original unchanged

    def test_deep_copy(self) -> None:
        """Test deep copy."""
        copied = self.node.copy(deep=True)
        
        # Test independence of structure
        copied["new"] = "new_data"
        self.assertNotIn("new", self.node)
        
        # Test independence of data
        copied.set("modified", "a")
        self.assertEqual(self.node["a"], "a_data")  # Original unchanged
        
        # Test nested structures
        copied.set("modified_nested", "b.c")
        self.assertEqual(self.node["b.c"], "bc_data")  # Original unchanged

    def test_copy_special_methods(self) -> None:
        """Test copy special methods."""
        # Test __copy__
        copied = copy.copy(self.node)
        self.assertEqual(copied.data, self.node.data)
        self.assertEqual(copied["a"], self.node["a"])
        
        # Test __deepcopy__
        deep_copied = copy.deepcopy(self.node)
        deep_copied["a"] = "modified"
        self.assertNotEqual(deep_copied["a"], self.node["a"])


class TestNamedTreeNodeOperators(unittest.TestCase):
    """Test NamedTreeNode operators and special methods."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root", "root_data")
        self.node["a"] = "a_data"
        self.node["b.c"] = "bc_data"

    def test_or_operator(self) -> None:
        """Test | operator."""
        # Test with dictionary
        result = self.node | {"name": "new", "data": "new_data"}
        self.assertEqual(result.name, "new")
        self.assertEqual(result.data, "new_data")
        self.assertEqual(result["a"], "a_data")  # Preserved original data
        
        # Test with another node
        other = NamedTreeNode[str]("other", "other_data")
        other["x"] = "x_data"
        result = self.node | other
        self.assertEqual(result.name, "other")
        self.assertEqual(result.data, "other_data")
        self.assertEqual(result["a"], "a_data")
        self.assertEqual(result["x"], "x_data")
        
        # Test with invalid type
        with self.assertRaises(TypeError):
            _ = self.node | "invalid"  # type: ignore

    def test_ior_operator(self) -> None:
        """Test |= operator."""
        # Test with dictionary
        original_node = self.node.copy(deep=True)
        self.node |= {"name": "new", "data": "new_data"}
        self.assertEqual(self.node.name, "new")
        self.assertEqual(self.node.data, "new_data")
        self.assertEqual(self.node["a"], "a_data")
        
        # Test with another node
        self.node = original_node.copy(deep=True)
        other = NamedTreeNode[str]("other", "other_data")
        other["x"] = "x_data"
        self.node |= other
        self.assertEqual(self.node.name, "other")
        self.assertEqual(self.node.data, "other_data")
        self.assertEqual(self.node["x"], "x_data")

    def test_ror_operator(self) -> None:
        """Test reverse or operator."""
        result = {"name": "dict", "data": "dict_data"} | self.node
        self.assertEqual(result.name, "root")
        self.assertEqual(result.data, "root_data")
        self.assertEqual(result["a"], "a_data")

    def test_contains(self) -> None:
        """Test membership testing."""
        self.assertTrue("a" in self.node)
        self.assertTrue("b.c" in self.node)
        self.assertFalse("missing" in self.node)
        self.assertFalse("b.missing" in self.node)
        
        # Test with invalid types
        self.assertFalse(123 in self.node)  # type: ignore
        self.assertFalse(None in self.node)

    def test_iteration(self) -> None:
        """Test iteration over nodes."""
        children = list(self.node)
        self.assertEqual(len(children), 2)  # 'a' and 'b' nodes
        
        child_names = [child.name for child in children]
        self.assertIn("a", child_names)
        self.assertIn("b", child_names)


class TestNamedTreeNodeEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root", "root_data")

    def test_empty_domain(self) -> None:
        """Test operations with empty domains."""
        # Set with empty domain
        self.node.set("data", "")
        self.assertEqual(self.node.data, "data")
        
        # Get with empty domain
        self.assertEqual(self.node.get(""), "data")
        
        # Empty domain components
        self.node.set("nested", "a..b")
        self.assertEqual(self.node.get("a.b"), "nested")

    def test_invalid_domains(self) -> None:
        """Test operations with invalid domains."""
        # None domain
        self.node.set("data", None)
        self.assertEqual(self.node.data, "data")
        
        # Invalid domain types
        with self.assertRaises(TypeError):
            self.node.set("data", 123)  # type: ignore
            
        with self.assertRaises(TypeError):
            self.node.get(["invalid"])  # type: ignore

    def test_namespace_conflicts(self) -> None:
        """Test namespace conflict handling."""
        # Try to create domain that conflicts with existing node
        self.node["a"] = "data"
        with self.assertRaises(ValueError):
            self.node["a.b"] = "conflict"
            
        # Try to create node that conflicts with existing domain
        self.node["x.y"] = "data"
        with self.assertRaises(ValueError):
            self.node["x"] = "conflict"

    def test_circular_references(self) -> None:
        """Test handling of circular references."""
        child = NamedTreeNode[str]("child", "child_data")
        self.node.add_child(child)
        
        # Attempt to add parent as child of child
        with self.assertRaises(ValueError):
            child.add_child(self.node)

    def test_data_validation(self) -> None:
        """Test data validation."""
        # Test with None data when not allowed
        strict_node = NamedTreeNode[str]("strict")
        strict_node.config.allow_none_data = False
        
        with self.assertRaises(ValueError):
            strict_node.set(None)
            
        # Test with invalid data types
        with self.assertRaises(TypeError):
            self.node.set(123)  # type: ignore


class TestNamedTreeNodePerformance(unittest.TestCase):
    """Test performance characteristics."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.node = NamedTreeNode[str]("root")
        
        # Create a deep tree
        current = self.node
        for i in range(100):
            child = NamedTreeNode[str](f"child{i}", f"data{i}")
            current.add_child(child)
            current = child

    def test_deep_traversal(self) -> None:
        """Test traversal of deep trees."""
        # This should complete quickly even with a deep tree
        path = ".".join(f"child{i}" for i in range(99))
        result = self.node.get(path)
        self.assertEqual(result, "data99")

    def test_large_breadth(self) -> None:
        """Test operations on trees with many siblings."""
        # Create many siblings
        for i in range(1000):
            self.node[f"child{i}"] = f"data{i}"
            
        # Test access time
        self.assertEqual(self.node["child999"], "data999")
        
        # Test iteration
        count = sum(1 for _ in self.node)
        self.assertEqual(count, 1100)  # 1000 new + 100 from setUp


if __name__ == '__main__':
    unittest.main(verbosity=2)