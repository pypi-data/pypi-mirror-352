"""Unit tests for core.mappings module."""

import unittest
from copy import deepcopy
from typing import Dict, Any

from quickstats.core.mappings import (
    recursive_update,
    concatenate,
    merge_classattr,
    NestedDict
)

class TestRecursiveUpdate(unittest.TestCase):
    """Test recursive_update functionality."""

    def setUp(self):
        self.base_dict = {
            'a': 1,
            'b': {
                'c': 2,
                'd': {'e': 3}
            }
        }

    def test_simple_update(self):
        """Test basic dictionary update."""
        update_dict = {'a': 10, 'x': 20}
        result = recursive_update(self.base_dict.copy(), update_dict)
        
        self.assertEqual(result['a'], 10)
        self.assertEqual(result['x'], 20)
        self.assertEqual(result['b']['c'], 2)

    def test_nested_update(self):
        """Test updating nested dictionaries."""
        update_dict = {
            'b': {
                'c': 20,
                'd': {'f': 30}
            }
        }
        result = recursive_update(self.base_dict.copy(), update_dict)
        
        self.assertEqual(result['b']['c'], 20)
        self.assertEqual(result['b']['d']['e'], 3)
        self.assertEqual(result['b']['d']['f'], 30)

    def test_empty_update(self):
        """Test update with empty dictionary."""
        original = self.base_dict.copy()
        result = recursive_update(original, {})
        
        self.assertEqual(result, original)

    def test_none_values(self):
        """Test handling of None values."""
        update_dict = {'a': None, 'b': {'c': None}}
        result = recursive_update(self.base_dict.copy(), update_dict)
        
        self.assertIsNone(result['a'])
        self.assertIsNone(result['b']['c'])

    def test_new_nested_structure(self):
        """Test creating new nested structures."""
        update_dict = {'new': {'nested': {'value': 42}}}
        result = recursive_update(self.base_dict.copy(), update_dict)
        
        self.assertEqual(result['new']['nested']['value'], 42)

class TestConcatenate(unittest.TestCase):
    """Test concatenate functionality."""

    def setUp(self):
        self.dict1 = {'a': 1, 'b': {'c': 2}}
        self.dict2 = {'b': {'d': 3}, 'e': 4}

    def test_basic_concatenation(self):
        """Test basic dictionary concatenation."""
        result = concatenate([self.dict1, self.dict2])
        
        self.assertEqual(result['a'], 1)
        self.assertEqual(result['b']['c'], 2)
        self.assertEqual(result['b']['d'], 3)
        self.assertEqual(result['e'], 4)

    def test_copy_option(self):
        """Test copy parameter behavior."""
        # Without copy
        result1 = concatenate([self.dict1, self.dict2], copy=False)
        self.dict1['a'] = 100
        self.assertEqual(result1['a'], 1)  # Should not be affected

        # With copy
        result2 = concatenate([self.dict1, self.dict2], copy=True)
        self.dict1['a'] = 200
        self.assertEqual(result2['a'], 1)  # Should not be affected

    def test_none_handling(self):
        """Test handling of None values in input sequence."""
        result = concatenate([self.dict1, None, self.dict2])
        
        self.assertEqual(result['a'], 1)
        self.assertEqual(result['e'], 4)

    def test_empty_input(self):
        """Test concatenation with empty input."""
        result = concatenate([])
        self.assertEqual(result, {})

class TestNestedDict(unittest.TestCase):
    """Test NestedDict class functionality."""

    def setUp(self):
        self.nested = NestedDict({'a': 1, 'b': {'c': 2, 'd': 3}})

    def test_merge(self):
        """Test merge method."""
        self.nested.merge({'b': {'e': 4}, 'f': 5})
        
        self.assertEqual(self.nested['b']['c'], 2)
        self.assertEqual(self.nested['b']['e'], 4)
        self.assertEqual(self.nested['f'], 5)

    def test_merge_none(self):
        """Test merge with None."""
        original = deepcopy(self.nested)
        self.nested.merge(None)
        
        self.assertEqual(self.nested, original)

    def test_and_operator(self):
        """Test & operator."""
        result = self.nested & {'b': {'e': 4}}
        
        self.assertEqual(result['b']['c'], 2)
        self.assertEqual(result['b']['e'], 4)
        self.assertIsInstance(result, NestedDict)

    def test_iand_operator(self):
        """Test &= operator."""
        self.nested &= {'b': {'e': 4}}
        
        self.assertEqual(self.nested['b']['c'], 2)
        self.assertEqual(self.nested['b']['e'], 4)

    def test_ror_operator(self):
        """Test reverse or operator."""
        result = {'b': {'e': 4}} | self.nested
        
        self.assertEqual(result['b']['c'], 2)
        self.assertEqual(result['b']['e'], 4)
        self.assertIsInstance(result, NestedDict)

    def test_copy(self):
        """Test copy method."""
        # Shallow copy
        shallow = self.nested.copy()
        shallow['a'] = 100
        self.assertEqual(self.nested['a'], 1)
        shallow['b']['c'] = 200
        self.assertEqual(self.nested['b']['c'], 200)  # Nested dict is shared

        # Deep copy
        deep = self.nested.copy(deep=True)
        deep['b']['c'] = 300
        self.assertEqual(self.nested['b']['c'], 200)  # Nested dict is separate

class TestMergeClassAttr(unittest.TestCase):
    """Test merge_classattr functionality."""

    def setUp(self):
        class Base:
            data = {'a': 1}
            
        class Child(Base):
            data = {'b': 2}
            
        class GrandChild(Child):
            data = {'c': 3}
            
        self.Base = Base
        self.Child = Child
        self.GrandChild = GrandChild

    def test_basic_merge(self):
        """Test basic attribute merging."""
        result = merge_classattr(self.Child, 'data')
        
        self.assertEqual(result['a'], 1)
        self.assertEqual(result['b'], 2)

    def test_multi_level_merge(self):
        """Test multi-level inheritance merging."""
        result = merge_classattr(self.GrandChild, 'data')
        
        self.assertEqual(result['a'], 1)
        self.assertEqual(result['b'], 2)
        self.assertEqual(result['c'], 3)

    def test_copy_option(self):
        """Test copy parameter behavior."""
        result = merge_classattr(self.Child, 'data', copy=True)
        self.Base.data['a'] = 100
        
        self.assertEqual(result['a'], 1)  # Should not be affected

    def test_missing_attribute(self):
        """Test handling of missing attributes."""
        class Empty:
            pass
            
        result = merge_classattr(Empty, 'data')
        self.assertEqual(result, {})

    def test_custom_parser(self):
        """Test custom parser function."""
        def parser(data: Dict[str, Any]) -> Dict[str, Any]:
            return {k.upper(): v * 2 for k, v in data.items()}
            
        result = merge_classattr(self.Child, 'data', parse=parser)
        
        self.assertEqual(result['A'], 2)
        self.assertEqual(result['B'], 4)

if __name__ == '__main__':
    unittest.main()
