"""Unit tests for core.enums module."""

import unittest
from quickstats.core.enums import (
    CaseInsensitiveStrEnum,
    GeneralEnum,
    DescriptiveEnum
)

class TestCaseInsensitiveStrEnum(unittest.TestCase):
    """Test CaseInsensitiveStrEnum functionality."""
    
    def setUp(self):
        class Format(CaseInsensitiveStrEnum):
            JSON = "json"
            XML = "xml"
        self.Format = Format

    def test_case_insensitive_match(self):
        """Test case-insensitive string matching."""
        self.assertEqual(self.Format("JSON"), self.Format.JSON)
        self.assertEqual(self.Format("json"), self.Format.JSON)
        self.assertEqual(self.Format("JsOn"), self.Format.JSON)

    def test_invalid_value(self):
        """Test handling of invalid values."""
        with self.assertRaises(ValueError):
            self.Format("INVALID")
        self.assertIsNone(self.Format._missing_(123))

class TestGeneralEnum(unittest.TestCase):
    """Test GeneralEnum functionality."""

    def setUp(self):
        class Status(GeneralEnum):
            ACTIVE = 1
            INACTIVE = 2
            __aliases__ = {
                "enabled": "active",
                "disabled": "inactive"
            }
        self.Status = Status

    def test_parse_methods(self):
        """Test various parsing methods."""
        self.assertEqual(self.Status.parse("active"), self.Status.ACTIVE)
        self.assertEqual(self.Status.parse("ACTIVE"), self.Status.ACTIVE)
        self.assertEqual(self.Status.parse(1), self.Status.ACTIVE)
        self.assertEqual(self.Status.parse("enabled"), self.Status.ACTIVE)
        self.assertIsNone(self.Status.parse(None))

    def test_equality(self):
        """Test equality comparisons."""
        self.assertEqual(self.Status.ACTIVE, "active")
        self.assertEqual(self.Status.ACTIVE, 1)
        self.assertNotEqual(self.Status.ACTIVE, "inactive")
        self.assertNotEqual(self.Status.ACTIVE, 2)

    def test_aliases(self):
        """Test alias functionality."""
        self.assertEqual(self.Status.parse("enabled"), self.Status.ACTIVE)
        self.assertEqual(self.Status.parse("disabled"), self.Status.INACTIVE)

    def test_member_lookup(self):
        """Test member lookup methods."""
        self.assertTrue(self.Status.has_member("active"))
        self.assertTrue(self.Status.has_member("ACTIVE"))
        self.assertFalse(self.Status.has_member("invalid"))

    def test_invalid_values(self):
        """Test handling of invalid values."""
        with self.assertRaises(ValueError):
            self.Status.parse("INVALID")
        with self.assertRaises(ValueError):
            self.Status.parse(999)

    def test_mapping_methods(self):
        """Test mapping utility methods."""
        self.assertEqual(
            set(self.Status.get_members()),
            {"active", "inactive"}
        )
        self.assertEqual(
            self.Status.get_values_map(),
            {1: self.Status.ACTIVE, 2: self.Status.INACTIVE}
        )
        self.assertEqual(
            self.Status.get_aliases_map(),
            {"enabled": "active", "disabled": "inactive"}
        )

class TestDescriptiveEnum(unittest.TestCase):
    """Test DescriptiveEnum functionality."""

    def setUp(self):
        class Level(DescriptiveEnum):
            HIGH = (1, "High priority")
            MEDIUM = (2, "Medium priority")
            LOW = (3, "Low priority")
        self.Level = Level

    def test_descriptions(self):
        """Test description attribute access."""
        self.assertEqual(self.Level.HIGH.description, "High priority")
        self.assertEqual(self.Level.MEDIUM.description, "Medium priority")
        self.assertEqual(self.Level.LOW.description, "Low priority")

    def test_parse_with_description(self):
        """Test parsing with description preservation."""
        level = self.Level.parse("HIGH")
        self.assertEqual(level.description, "High priority")
        self.assertEqual(level.value, 1)

    def test_invalid_with_descriptions(self):
        """Test error messages include descriptions."""
        with self.assertRaises(ValueError) as cm:
            self.Level.parse("INVALID")
        error_msg = str(cm.exception)
        self.assertIn("High priority", error_msg)
        self.assertIn("Medium priority", error_msg)
        self.assertIn("Low priority", error_msg)

if __name__ == '__main__':
    unittest.main()
