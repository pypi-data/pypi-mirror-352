"""Unit tests for type validation module."""

from __future__ import annotations

import unittest
from typing import (
    List, Dict, Union, Optional, Tuple, Set,
    TypeVar, Any, Generic
)
from dataclasses import dataclass

from quickstats.core.type_validation import (
    ValidatorFactory,
    check_type,
    get_type_hint_str,
    ValidationError
)

T = TypeVar('T')

@dataclass
class MockGeneric(Generic[T]):
    value: T


class TestTypeValidation(unittest.TestCase):
    """Test suite for type validation functionality."""
    
    def test_basic_types(self) -> None:
        """Test validation of basic Python types."""
        cases = [
            (42, int, True),
            ("hello", str, True),
            (3.14, float, True),
            (True, bool, True),
            (42, str, False),
            ("42", int, False),
            (3.14, int, False),
        ]
        
        for value, type_hint, expected in cases:
            with self.subTest(value=value, type=type_hint):
                self.assertEqual(
                    check_type(value, type_hint),
                    expected,
                    f"Failed for value {value} of type {type(value)}"
                )

    def test_container_types(self) -> None:
        """Test validation of container types."""
        cases = [
            ([1, 2, 3], List[int], True),
            ([1, "2", 3], List[int], False),
            ({"a": 1, "b": 2}, Dict[str, int], True),
            ({"a": "1"}, Dict[str, int], False),
            ({1, 2, 3}, Set[int], True),
            ((1, "2", 3.0), Tuple[int, str, float], True),
            ((1, 2), Tuple[int, ...], True),
        ]
        
        for value, type_hint, expected in cases:
            with self.subTest(value=value, type=type_hint):
                self.assertEqual(check_type(value, type_hint), expected)

    def test_optional_types(self) -> None:
        """Test validation of Optional types."""
        cases = [
            (None, Optional[int], True),
            (42, Optional[int], True),
            ("hello", Optional[int], False),
            (None, Optional[List[int]], True),
            ([1, 2, 3], Optional[List[int]], True),
            ([1, "2"], Optional[List[int]], False),
        ]
        
        for value, type_hint, expected in cases:
            with self.subTest(value=value, type=type_hint):
                self.assertEqual(check_type(value, type_hint), expected)

    def test_union_types(self) -> None:
        """Test validation of Union types."""
        cases = [
            (42, Union[int, str], True),
            ("hello", Union[int, str], True),
            (3.14, Union[int, str], False),
            ([1, 2], Union[List[int], Dict[str, int]], True),
            ({"a": 1}, Union[List[int], Dict[str, int]], True),
            ({1: "a"}, Union[List[int], Dict[str, int]], False),
        ]
        
        for value, type_hint, expected in cases:
            with self.subTest(value=value, type=type_hint):
                self.assertEqual(check_type(value, type_hint), expected)

    def test_nested_types(self) -> None:
        """Test validation of nested type structures."""
        cases = [
            (
                {"a": [1, 2], "b": [3, 4]},
                Dict[str, List[int]],
                True
            ),
            (
                {"a": [1, "2"]},
                Dict[str, List[int]],
                False
            ),
            (
                [[1, 2], [3, 4]],
                List[List[int]],
                True
            ),
            (
                {"a": {"b": [1, 2]}},
                Dict[str, Dict[str, List[int]]],
                True
            ),
        ]
        
        for value, type_hint, expected in cases:
            with self.subTest(value=value, type=type_hint):
                self.assertEqual(check_type(value, type_hint), expected)

    def test_generic_types(self) -> None:
        """Test validation of generic types."""
        int_generic = MockGeneric[int](42)
        str_generic = MockGeneric[str]("hello")
        
        self.assertTrue(check_type(int_generic.value, int))
        self.assertTrue(check_type(str_generic.value, str))
        self.assertFalse(check_type(int_generic.value, str))
        self.assertFalse(check_type(str_generic.value, int))

    def test_type_hint_str(self) -> None:
        """Test string representation of type hints."""
        cases = [
            (int, "int"),
            (List[int], "List[int]"),
            (Dict[str, int], "Dict[str, int]"),
            (Optional[int], "Optional[int]"),
            (Union[int, str], "int | str"),
            (List[Dict[str, int]], "List[Dict[str, int]]"),
            (Tuple[int, ...], "Tuple[int, ...]"),
        ]
        
        for type_hint, expected in cases:
            with self.subTest(type=type_hint):
                self.assertEqual(get_type_hint_str(type_hint), expected)

    def test_validation_errors(self) -> None:
        """Test error handling during validation."""
        with self.assertRaises(ValidationError):
            check_type("hello", int, raise_error=True)
            
        with self.assertRaises(ValidationError):
            check_type([1, "2"], List[int], raise_error=True)
            
        # Test error message content
        try:
            check_type(42, str, raise_error=True)
        except ValidationError as e:
            self.assertIn("str", str(e))
            self.assertIn("int", str(e))

    def test_validator_factory_cache(self) -> None:
        """Test caching behavior of ValidatorFactory."""
        # Get validators for same type multiple times
        validator1 = ValidatorFactory.get_validator(List[int])
        validator2 = ValidatorFactory.get_validator(List[int])
        
        # Should return same cached validator
        self.assertIs(validator1, validator2)
        
        # Test with different types
        validator3 = ValidatorFactory.get_validator(Dict[str, int])
        self.assertIsNot(validator1, validator3)

    def test_any_type(self) -> None:
        """Test validation with Any type."""
        cases = [42, "hello", [1, 2], {"a": 1}, {1, 2}, (1, 2), None]
        
        for value in cases:
            with self.subTest(value=value):
                self.assertTrue(check_type(value, Any))


if __name__ == '__main__':
    unittest.main(verbosity=2)