"""Unit tests for AbstractObject class."""

from __future__ import annotations

import pickle
import unittest
from typing import Any

from quickstats.core.abstract_object import AbstractObject
from quickstats.core.logger import Logger, Verbosity
from quickstats.core.decorators import semistaticmethod


class TestObject(AbstractObject):
    """Test class extending AbstractObject."""
    
    def __init__(self, value: Any = None, **kwargs: Any) -> None:
        self.value = value
        super().__init__(**kwargs)

    @semistaticmethod
    def log_message(self_or_cls, message: str) -> None:
        """Log message using either instance or class stdout."""
        self_or_cls.stdout.info(message)

    @semistaticmethod
    def get_verbosity(self_or_cls) -> Verbosity:
        """Get current verbosity level."""
        return self_or_cls.stdout.verbosity


class TestAbstractObject(unittest.TestCase):
    """Test suite for AbstractObject functionality."""

    def setUp(self) -> None:
        """Initialize test fixtures."""
        # Reset class-level default for each test
        TestObject._class_stdout = Logger(Verbosity.INFO)

    def test_initialization(self) -> None:
        """Test object initialization with different verbosity settings."""
        # Default initialization
        obj = TestObject()
        self.assertEqual(obj.stdout.verbosity, Verbosity.INFO)
        self.assertIsNone(obj._stdout)
        
        # Custom verbosity
        obj = TestObject(verbosity="DEBUG")
        self.assertEqual(obj.stdout.verbosity, Verbosity.DEBUG)
        self.assertIsNotNone(obj._stdout)
        
        # None verbosity
        obj = TestObject(verbosity=None)
        self.assertEqual(obj.stdout.verbosity, Verbosity.INFO)
        self.assertIsNone(obj._stdout)

    def test_stdout_property(self) -> None:
        """Test stdout property behavior at class and instance level."""
        # Class-level access
        self.assertEqual(TestObject.stdout.verbosity, Verbosity.INFO)
        
        # Instance with default
        obj1 = TestObject()
        self.assertEqual(obj1.stdout.verbosity, Verbosity.INFO)
        self.assertIs(obj1.stdout, TestObject._class_stdout)
        
        # Instance with custom
        obj2 = TestObject(verbosity="DEBUG")
        self.assertEqual(obj2.stdout.verbosity, Verbosity.DEBUG)
        self.assertIsNot(obj2.stdout, TestObject._class_stdout)

    def test_verbosity_inheritance(self) -> None:
        """Test verbosity inheritance from class to instance."""
        # Set class default
        TestObject.set_default_verbosity("DEBUG")
        
        # New instance should inherit
        obj = TestObject()
        self.assertEqual(obj.stdout.verbosity, Verbosity.DEBUG)
        self.assertTrue(obj.debug_mode)
        
        # Custom verbosity should override
        obj.set_verbosity("WARNING")
        self.assertEqual(obj.stdout.verbosity, Verbosity.WARNING)
        self.assertFalse(obj.debug_mode)

    def test_set_verbosity(self) -> None:
        """Test verbosity changes."""
        obj = TestObject()
        
        # Set custom verbosity
        obj.set_verbosity("DEBUG")
        self.assertEqual(obj.stdout.verbosity, Verbosity.DEBUG)
        self.assertIsNotNone(obj._stdout)
        
        # Reset to default
        obj.set_verbosity(None)
        self.assertEqual(obj.stdout.verbosity, Verbosity.INFO)
        self.assertIsNone(obj._stdout)
        
        # Test invalid verbosity
        with self.assertRaises(ValueError):
            obj.set_verbosity("INVALID")

    def test_copy_verbosity(self) -> None:
        """Test copying verbosity between objects."""
        # Source with custom verbosity
        source = TestObject(verbosity="DEBUG")
        
        # Copy to target
        target = TestObject()
        target.copy_verbosity_from(source)
        self.assertEqual(target.stdout.verbosity, Verbosity.DEBUG)
        self.assertIsNotNone(target._stdout)
        
        # Copy default verbosity
        source = TestObject()
        target.copy_verbosity_from(source)
        self.assertIsNone(target._stdout)
        self.assertEqual(target.stdout.verbosity, Verbosity.INFO)

    def test_semistaticmethod(self) -> None:
        """Test stdout access with semistaticmethod."""
        # Class-level access
        TestObject.log_message("class message")
        self.assertEqual(TestObject.get_verbosity(), Verbosity.INFO)
        
        # Instance with default
        obj1 = TestObject()
        obj1.log_message("default message")
        self.assertEqual(obj1.get_verbosity(), Verbosity.INFO)
        
        # Instance with custom
        obj2 = TestObject(verbosity="DEBUG")
        obj2.log_message("debug message")
        self.assertEqual(obj2.get_verbosity(), Verbosity.DEBUG)

    def test_debug_mode(self) -> None:
        """Test debug_mode property."""
        obj = TestObject()
        self.assertFalse(obj.debug_mode)
        
        obj.set_verbosity("DEBUG")
        self.assertTrue(obj.debug_mode)
        
        obj.set_verbosity("INFO")
        self.assertFalse(obj.debug_mode)

    def test_pickling(self) -> None:
        """Test serialization and deserialization."""
        # Test with custom verbosity
        original = TestObject(value="test", verbosity="DEBUG")
        pickled = pickle.dumps(original)
        unpickled = pickle.loads(pickled)
        
        self.assertEqual(unpickled.value, "test")
        self.assertEqual(unpickled.stdout.verbosity, Verbosity.DEBUG)
        self.assertIsNotNone(unpickled._stdout)
        
        # Test with default verbosity
        original = TestObject(value="test")
        pickled = pickle.dumps(original)
        unpickled = pickle.loads(pickled)
        
        self.assertEqual(unpickled.value, "test")
        self.assertEqual(unpickled.stdout.verbosity, Verbosity.INFO)
        self.assertIsNone(unpickled._stdout)

    def test_class_default_changes(self) -> None:
        """Test effect of changing class-level default verbosity."""
        # Create instances
        default_obj = TestObject()
        custom_obj = TestObject(verbosity="WARNING")
        
        # Change class default
        TestObject.set_default_verbosity("DEBUG")
        
        # Should affect instance using class default
        self.assertEqual(default_obj.stdout.verbosity, Verbosity.DEBUG)
        self.assertEqual(TestObject.stdout.verbosity, Verbosity.DEBUG)
        
        # Should not affect instance with custom verbosity
        self.assertEqual(custom_obj.stdout.verbosity, Verbosity.WARNING)

    def test_edge_cases(self) -> None:
        """Test edge cases and error conditions."""
        obj = TestObject()
        
        # Invalid verbosity values
        for invalid_value in ["INVALID", -1, None]:
            with self.subTest(value=invalid_value):
                if invalid_value is None:
                    obj.set_verbosity(invalid_value)  # Should work
                else:
                    with self.assertRaises(ValueError):
                        obj.set_verbosity(invalid_value)
        
        # Copy from invalid source
        with self.assertRaises(AttributeError):
            obj.copy_verbosity_from("not an object")


if __name__ == '__main__':
    unittest.main(verbosity=2)