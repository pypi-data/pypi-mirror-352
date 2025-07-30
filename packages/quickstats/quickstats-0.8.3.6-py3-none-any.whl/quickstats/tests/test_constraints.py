"""Unit tests for constraints module."""

from __future__ import annotations

import unittest
from typing import Any, Set

from quickstats.core.constraints import (
    BaseConstraint,
    RangeConstraint,
    MinConstraint,
    MaxConstraint,
    ChoiceConstraint
)


class TestConstraints(unittest.TestCase):
    """Test suite for constraint classes."""

    def test_base_constraint(self) -> None:
        """Test BaseConstraint functionality."""
        constraint = BaseConstraint()
        
        # Test basic functionality
        self.assertTrue(constraint(42))
        self.assertTrue(constraint("anything"))
        
        # Test representation
        self.assertEqual(repr(constraint), "BaseConstraint()")
        
        # Test equality
        other_constraint = BaseConstraint()
        self.assertEqual(constraint, other_constraint)
        
        # Test hash
        self.assertEqual(hash(constraint), hash(other_constraint))

    def test_range_constraint(self) -> None:
        """Test RangeConstraint functionality."""
        # Test inclusive bounds
        constraint = RangeConstraint(1, 10)
        
        for value in [1, 5, 10]:
            with self.subTest(value=value):
                self.assertTrue(constraint(value))
                
        for value in [0, 11]:
            with self.subTest(value=value):
                self.assertFalse(constraint(value))

        # Test exclusive bounds
        constraint = RangeConstraint(1, 10, lbound=False, rbound=False)
        
        for value in [2, 5, 9]:
            with self.subTest(value=value):
                self.assertTrue(constraint(value))
                
        for value in [1, 10]:
            with self.subTest(value=value):
                self.assertFalse(constraint(value))

        # Test error conditions
        with self.assertRaises(ValueError):
            RangeConstraint(10, 1)  # Invalid range
            
        with self.assertRaises(ValueError):
            RangeConstraint(1, 10, lbound="invalid")
            
        with self.assertRaises(ValueError):
            constraint("invalid")  # Invalid value type

        # Test equality and hash
        c1 = RangeConstraint(1, 10)
        c2 = RangeConstraint(1, 10)
        c3 = RangeConstraint(1, 10, lbound=False)
        
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)
        self.assertEqual(hash(c1), hash(c2))
        self.assertNotEqual(hash(c1), hash(c3))

    def test_min_constraint(self) -> None:
        """Test MinConstraint functionality."""
        # Test inclusive minimum
        constraint = MinConstraint(5)
        
        for value in [5, 6, 10]:
            with self.subTest(value=value):
                self.assertTrue(constraint(value))
                
        for value in [0, 4]:
            with self.subTest(value=value):
                self.assertFalse(constraint(value))

        # Test exclusive minimum
        constraint = MinConstraint(5, inclusive=False)
        
        for value in [6, 7, 10]:
            with self.subTest(value=value):
                self.assertTrue(constraint(value))
                
        for value in [4, 5]:
            with self.subTest(value=value):
                self.assertFalse(constraint(value))

        # Test error conditions
        with self.assertRaises(ValueError):
            MinConstraint(5, inclusive="invalid")
            
        with self.assertRaises(ValueError):
            constraint("invalid")

        # Test equality and hash
        c1 = MinConstraint(5)
        c2 = MinConstraint(5)
        c3 = MinConstraint(5, inclusive=False)
        
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)
        self.assertEqual(hash(c1), hash(c2))
        self.assertNotEqual(hash(c1), hash(c3))

    def test_max_constraint(self) -> None:
        """Test MaxConstraint functionality."""
        # Test inclusive maximum
        constraint = MaxConstraint(5)
        
        for value in [0, 4, 5]:
            with self.subTest(value=value):
                self.assertTrue(constraint(value))
                
        for value in [6, 10]:
            with self.subTest(value=value):
                self.assertFalse(constraint(value))

        # Test exclusive maximum
        constraint = MaxConstraint(5, inclusive=False)
        
        for value in [0, 3, 4]:
            with self.subTest(value=value):
                self.assertTrue(constraint(value))
                
        for value in [5, 6]:
            with self.subTest(value=value):
                self.assertFalse(constraint(value))

        # Test error conditions
        with self.assertRaises(ValueError):
            MaxConstraint(5, inclusive="invalid")
            
        with self.assertRaises(ValueError):
            constraint("invalid")

        # Test equality and hash
        c1 = MaxConstraint(5)
        c2 = MaxConstraint(5)
        c3 = MaxConstraint(5, inclusive=False)
        
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)
        self.assertEqual(hash(c1), hash(c2))
        self.assertNotEqual(hash(c1), hash(c3))

    def test_choice_constraint(self) -> None:
        """Test ChoiceConstraint functionality."""
        choices = {1, "test", 3.14}
        constraint = ChoiceConstraint(*choices)
        
        # Test valid choices
        for value in choices:
            with self.subTest(value=value):
                self.assertTrue(constraint(value))

        # Test invalid choices
        invalid_values = [0, "invalid", 2.71]
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    constraint(value)

        # Test with different types of choices
        constraint = ChoiceConstraint(None, True, 42)
        self.assertTrue(constraint(None))
        self.assertTrue(constraint(True))
        self.assertTrue(constraint(42))
        
        with self.assertRaises(ValueError):
            constraint(False)

        # Test equality and hash
        c1 = ChoiceConstraint(1, 2, 3)
        c2 = ChoiceConstraint(1, 2, 3)
        c3 = ChoiceConstraint(1, 2, 4)
        
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)
        self.assertEqual(hash(c1), hash(c2))
        self.assertNotEqual(hash(c1), hash(c3))

    def test_constraint_combinations(self) -> None:
        """Test using multiple constraints together."""
        range_constraint = RangeConstraint(1, 10)
        choice_constraint = ChoiceConstraint(2, 4, 6, 8)
        
        # Value should satisfy both constraints
        value = 4
        self.assertTrue(range_constraint(value))
        self.assertTrue(choice_constraint(value))
        
        # Value in range but not in choices
        value = 3
        self.assertTrue(range_constraint(value))
        with self.assertRaises(ValueError):
            choice_constraint(value)
        
        # Value in choices but not in range
        value = 12
        with self.assertRaises(ValueError):
            choice_constraint(value)
        self.assertFalse(range_constraint(value))


if __name__ == '__main__':
    unittest.main(verbosity=2)