"""Unit tests for core.trees module."""

import unittest
from typing import Optional, Any

from quickstats.core.trees import (
    NodeConfig,
    NamedTreeNode,
    TreeError,
    InvalidNodeError,
    DomainError,
    ValidationError
)

class TestNodeConfig(unittest.TestCase):
    """Test NodeConfig functionality."""

    def test_default_config(self):
        """Test default configuration values."""
        config = NodeConfig()
        
        self.assertEqual(config.separator, '.')
        self.assertTrue(config.allow_none_data)
        self.assertFalse(config.validate_names)
        self.assertFalse(config.validate_data_type)
        self.assertEqual(config.name_pattern, r'^[a-zA-Z][a-zA-Z0-9_]*$')

class TestNamedTreeNode(unittest.TestCase):
    """Test NamedTreeNode functionality."""

    def setUp(self):
        self.root = NamedTreeNode[str]("root", "root_data")

    def test_basic_operations(self):
        """Test basic node operations."""
        # Add child
        child = NamedTreeNode("child1", "child1_data")
        self.root.add_child(child)
        
        self.assertEqual(self.root.get("child1"), "child1_data")
        self.assertEqual(len(list(self.root)), 1)

        # Remove child
        removed = self.root.remove_child("child1")
        self.assertEqual(removed.data, "child1_data")
        self.assertEqual(len(list(self.root)), 0)

    def test_domain_operations(self):
        """Test domain-style operations."""
        # Set with domain
        self.root.set("data1", "child1.grandchild1")
        self.root.set("data2", "child1.grandchild2")
        
        # Get with domain
        self.assertEqual(self.root.get("child1.grandchild1"), "data1")
        self.assertEqual(self.root.get("child1.grandchild2"), "data2")

        # Check domain exists
        self.assertTrue("child1.grandchild1" in self.root)
        self.assertFalse("invalid.path" in self.root)

    def test_traversal(self):
        """Test tree traversal."""
        # Setup tree
        self.root["a.b.c"] = "data1"
        self.root["a.b.d"] = "data2"
        
        # Test traverse method
        node = self.root.traverse("a", "b")
        self.assertIsNotNone(node)
        self.assertEqual(node.get("c"), "data1")
        self.assertEqual(node.get("d"), "data2")

        # Test traverse_domain method
        node = self.root.traverse_domain("a.b")
        self.assertIsNotNone(node)
        self.assertEqual(node.get("c"), "data1")

    def test_dict_operations(self):
        """Test dictionary-style operations."""
        # Dictionary update
        self.root |= {
            "name": "child1",
            "data": "child1_data",
            "children": {
                "grandchild1": {
                    "name": "grandchild1",
                    "data": "gc1_data"
                }
            }
        }
        
        self.assertEqual(self.root.get("child1.grandchild1"), "gc1_data")

    def test_validation(self):
        """Test node validation."""
        # Enable validation
        self.root.config.validate_names = True
        
        # Valid name
        valid_node = NamedTreeNode("valid_name", "data")
        self.root.add_child(valid_node)
        
        # Invalid name
        with self.assertRaises(ValidationError):
            invalid_node = NamedTreeNode("123invalid", "data")
            self.root.add_child(invalid_node)

    def test_type_validation(self):
        """Test data type validation."""
        typed_node = NamedTreeNode[int]("numbers")
        typed_node.config.validate_data_type = True
        
        # Valid type
        typed_node.set(42, "valid")
        
        # Invalid type
        with self.assertRaises(ValidationError):
            typed_node.set("not a number", "invalid")

    def test_copy_operations(self):
        """Test copy operations."""
        # Setup original
        self.root["a.b.c"] = "data1"
        
        # Shallow copy
        shallow = self.root.copy()
        shallow["a.b.c"] = "changed"
        self.assertEqual(self.root["a.b.c"], "data1")
        
        # Deep copy
        deep = self.root.copy(deep=True)
        deep["a.b.c"] = "changed"
        self.assertEqual(self.root["a.b.c"], "data1")

    def test_merge_operations(self):
        """Test merge operations."""
        # Setup trees
        tree1 = NamedTreeNode[str]("root")
        tree1["a.b"] = "data1"
        
        tree2 = NamedTreeNode[str]("root")
        tree2["a.c"] = "data2"
        
        # Test merge
        tree1.merge(tree2)
        self.assertEqual(tree1["a.b"], "data1")
        self.assertEqual(tree1["a.c"], "data2")

    def test_error_handling(self):
        """Test error handling."""
        # Invalid node type
        with self.assertRaises(TypeError):
            self.root.add_child("not a node")

        # Domain not found
        with self.assertRaises(KeyError):
            _ = self.root["invalid.path"]

        # Duplicate child name
        child = NamedTreeNode("child", "data")
        self.root.add_child(child)
        with self.assertRaises(ValidationError):
            self.root.add_child(child)

class TestTreeDataTypes(unittest.TestCase):
    """Test tree with different data types."""

    def test_int_tree(self):
        """Test tree with integer data."""
        tree = NamedTreeNode[int]("numbers")
        tree["a"] = 1
        tree["b"] = 2
        
        self.assertEqual(tree["a"], 1)
        self.assertIsInstance(tree["a"], int)

    def test_optional_data(self):
        """Test tree with optional data."""
        tree = NamedTreeNode[Optional[str]]("optional")
        tree["a"] = "data"
        tree["b"] = None
        
        self.assertEqual(tree["a"], "data")
        self.assertIsNone(tree["b"])

    def test_any_data(self):
        """Test tree with Any data type."""
        tree = NamedTreeNode[Any]("any")
        tree["a"] = 1
        tree["b"] = "string"
        tree["c"] = [1, 2, 3]
        
        self.assertEqual(tree["a"], 1)
        self.assertEqual(tree["b"], "string")
        self.assertEqual(tree["c"], [1, 2, 3])

if __name__ == '__main__':
    unittest.main()
