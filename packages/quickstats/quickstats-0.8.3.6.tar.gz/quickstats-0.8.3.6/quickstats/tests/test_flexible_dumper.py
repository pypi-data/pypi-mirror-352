"""Unit tests for FlexibleDumper class."""

from __future__ import annotations

import unittest
from typing import Any
import numpy as np

from quickstats import FlexibleDumper


class TestFlexibleDumper(unittest.TestCase):
    """Test suite for FlexibleDumper class."""

    def setUp(self) -> None:
        """Initialize test fixtures."""
        self.dumper = FlexibleDumper()
        self.basic_data = {
            'str': 'hello',
            'int': 42,
            'list': [1, 2, 3],
            'dict': {'a': 1, 'b': 2},
            'set': {1, 2, 3},
            'tuple': (4, 5, 6)
        }
        self.complex_data = {
            'nested': {
                'deep': {
                    'deeper': {
                        'deepest': 'value'
                    }
                }
            },
            'mixed': [
                1,
                {'a': [2, 3]},
                (4, [5, {'b': 6}])
            ],
            'array': np.arange(10),
            'multiline': 'line1\nline2\nline3'
        }

    def test_initialization(self) -> None:
        """Test initialization with different parameters."""
        # Default initialization
        self.assertEqual(self.dumper.item_indent, '  ')
        self.assertEqual(self.dumper.list_indent, '- ')
        
        # Custom initialization
        custom_dumper = FlexibleDumper(
            item_indent='    ',
            list_indent='* ',
            separator=' = ',
            skip_str='...'
        )
        self.assertEqual(custom_dumper.item_indent, '    ')
        self.assertEqual(custom_dumper.list_indent, '* ')
        self.assertEqual(custom_dumper.separator, ' = ')
        self.assertEqual(custom_dumper.skip_str, '...')

        # Invalid initialization
        with self.assertRaises(ValueError):
            FlexibleDumper(item_indent='  ', list_indent='---')

    def test_basic_types(self) -> None:
        """Test dumping of basic Python types."""
        cases = [
            (42, "42"),
            ("hello", "hello"),
            (True, "True"),
            (None, "None"),
            ([1, 2], "- 1\n- 2"),
            ((1, 2), "- 1\n- 2"),
            ({1, 2}, "{1, 2}"),
            ({'a': 1}, "a: 1")
        ]
        
        for data, expected in cases:
            with self.subTest(data=data):
                result = self.dumper.dump(data)
                self.assertEqual(result, expected)

    def test_nested_structures(self) -> None:
        """Test dumping of nested data structures."""
        data = {
            'list': [1, [2, 3], {'a': 4}],
            'dict': {'x': {'y': 'z'}},
            'mixed': [1, {'a': [2, {'b': 3}]}]
        }
        dumper = FlexibleDumper(indent_sequence_on_key=True)
        result = dumper.dump(data)
        
        expected = (
            "list: \n"
            "  - 1\n"
            "  - - 2\n"
            "    - 3\n"
            "  - a: 4\n"
            "dict: \n"
            "  x: \n"
            "    y: z\n"
            "mixed: \n"
            "  - 1\n"
            "  - a: \n"
            "      - 2\n"
            "      - b: 3"
        )
        self.assertEqual(result, expected)

    def test_limits(self) -> None:
        """Test various limiting parameters."""
        # Test max_depth
        deep_data = {'a': {'b': {'c': {'d': 'e'}}}}
        dumper = FlexibleDumper(max_depth=2)
        self.assertEqual(
            dumper.dump(deep_data),
            "a: \n  b: \n    ..."
        )

        # Test max_iteration
        long_list = list(range(10))
        dumper = FlexibleDumper(max_iteration=3)
        self.assertEqual(
            dumper.dump(long_list),
            "- 0\n- 1\n- 2\n..."
        )

        # Test max_item
        big_dict = {str(i): i for i in range(10)}
        dumper = FlexibleDumper(max_item=3)
        result = dumper.dump(big_dict)
        self.assertIn("...", result)
        self.assertTrue(len(result.split('\n')) <= 4)

        # Test max_len
        long_text = "This is a very long text string"
        dumper = FlexibleDumper(max_len=15)
        self.assertEqual(
            dumper.dump(long_text),
            "This is a ve..."
        )

    def test_multiline_handling(self) -> None:
        """Test handling of multiline strings."""
        data = {
            'text': 'line1\nline2\nline3',
            'nested': {
                'text': 'a\nb\nc'
            }
        }
        result = self.dumper.dump(data)
        expected = (
            "text: line1\n"
            "      line2\n"
            "      line3\n"
            "nested: \n"
            "  text: a\n"
            "        b\n"
            "        c"
        )
        self.assertEqual(result, expected)

    def test_numpy_array_handling(self) -> None:
        """Test handling of NumPy arrays."""
        arrays = {
            'int': np.array([1, 2, 3]),
            '2d': np.array([[1, 2], [3, 4]]),
            'float': np.array([1.5, 2.5, 3.5])
        }
        result = self.dumper.dump(arrays)
        self.assertIn("[1 2 3]", result)
        self.assertIn("[[1 2]", result)
        self.assertIn(" [3 4]]", result)
        self.assertIn("[1.5 2.5 3.5]", result)

    def test_edge_cases(self) -> None:
        """Test edge cases and potential error conditions."""
        cases = [
            ({}, ""),  # Empty dict
            ([], ""),  # Empty list
            (" ", " "),  # Whitespace
            ("", ""),  # Empty string
            (set(), "set()"),  # Empty set
            ({"": ""}, ": "),  # Empty keys/values
            ([None, None], "- None\n- None"),  # None values
        ]
        
        for data, expected in cases:
            with self.subTest(data=data):
                result = self.dumper.dump(data)
                self.assertEqual(result, expected)

    def test_configuration_changes(self) -> None:
        """Test dynamic configuration changes."""
        dumper = FlexibleDumper()
        data = {'a': [1, 2, 3]}
        
        # Default output
        default_output = dumper.dump(data)
        
        # Change configuration
        dumper.configure(
            item_indent='>>',
            list_indent='*>',
            separator=' = '
        )
        
        modified_output = dumper.dump(data)
        self.assertNotEqual(default_output, modified_output)
        self.assertIn('*>', modified_output)
        self.assertIn(' = ', modified_output)

    def test_invalid_configurations(self) -> None:
        """Test handling of invalid configurations."""
        with self.assertRaises(ValueError):
            FlexibleDumper(item_indent='', list_indent='')
        
        with self.assertRaises(ValueError):
            FlexibleDumper(item_indent='  ', list_indent='-')

        dumper = FlexibleDumper()
        with self.assertRaises(KeyError):
            dumper.configure(invalid_param='value')


if __name__ == '__main__':
    unittest.main(verbosity=2)