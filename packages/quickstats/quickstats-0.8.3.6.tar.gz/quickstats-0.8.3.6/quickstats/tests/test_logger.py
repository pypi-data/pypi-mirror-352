"""Unit tests for core.logger module."""

import unittest
import sys
import io
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
from quickstats.core.logger import (
    TextColors,
    Verbosity,
    Logger,
    switch_verbosity,
    set_default_log_format
)

@contextmanager
def captured_output():
    """Context manager to capture stdout."""
    new_out = io.StringIO()
    old_out = sys.stdout
    try:
        sys.stdout = new_out
        yield new_out
    finally:
        sys.stdout = old_out

class TestTextColors(unittest.TestCase):
    """Test TextColors class functionality."""

    def test_colorize(self):
        """Test text colorization."""
        colored = TextColors.colorize("test", "red")
        self.assertIn("test", colored)
        self.assertIn(TextColors.CODES["red"], colored)
        self.assertIn(TextColors.CODES["reset"], colored)

    def test_invalid_color(self):
        """Test handling of invalid colors."""
        self.assertEqual(TextColors.colorize("test", None), "test")
        self.assertEqual(TextColors.colorize("test", "invalid"), "test")

    def test_format_comparison(self):
        """Test text comparison formatting."""
        left, right = TextColors.format_comparison(
            "abc", "abd",
            equal_color="blue",
            delete_color="red",
            insert_color="green"
        )
        self.assertIn(TextColors.CODES["blue"], left)
        self.assertIn(TextColors.CODES["red"], left)
        self.assertIn(TextColors.CODES["blue"], right)
        self.assertIn(TextColors.CODES["green"], right)

class TestVerbosity(unittest.TestCase):
    """Test Verbosity enum functionality."""

    def test_ordering(self):
        """Test verbosity level ordering."""
        self.assertLess(Verbosity.DEBUG, Verbosity.INFO)
        self.assertLess(Verbosity.INFO, Verbosity.WARNING)
        self.assertLess(Verbosity.WARNING, Verbosity.ERROR)
        self.assertLess(Verbosity.ERROR, Verbosity.CRITICAL)

    def test_comparison(self):
        """Test verbosity comparison with different types."""
        self.assertLess(Verbosity.DEBUG, 20)  # INFO level
        self.assertLess(Verbosity.DEBUG, "INFO")
        self.assertEqual(Verbosity.INFO, "INFO")
        self.assertEqual(Verbosity.INFO, 20)

class TestLogger(unittest.TestCase):
    """Test Logger class functionality."""

    def setUp(self):
        self.printer = Logger(
            verbosity=Verbosity.INFO,
            fmt="basic",
            name="test"
        )

    def test_verbosity_setting(self):
        """Test verbosity level setting and parsing."""
        self.printer.verbosity = "DEBUG"
        self.assertEqual(self.printer.verbosity, Verbosity.DEBUG)
        self.printer.verbosity = Verbosity.INFO
        self.assertEqual(self.printer.verbosity, Verbosity.INFO)
        self.printer.verbosity = 30  # WARNING
        self.assertEqual(self.printer.verbosity, Verbosity.WARNING)

    def test_basic_output(self):
        """Test basic message output."""
        with captured_output() as out:
            self.printer.info("test message")
            output = out.getvalue()
            self.assertIn("[INFO]", output)
            self.assertIn("test message", output)

    def test_format_switching(self):
        """Test format switching."""
        self.printer.set_format("detailed")
        with captured_output() as out:
            self.printer.info("test")
            detailed = out.getvalue()
            self.assertIn("PID:", detailed)
            self.assertIn("TID:", detailed)

        self.printer.set_format("basic")
        with captured_output() as out:
            self.printer.info("test")
            basic = out.getvalue()
            self.assertNotIn("PID:", basic)
            self.assertNotIn("TID:", basic)

    def test_time_formatting(self):
        """Test time format customization."""
        self.printer.set_format("detailed")
        self.printer.set_timefmt(datefmt="%H:%M:%S")
        
        with captured_output() as out:
            self.printer.info("test")
            output = out.getvalue()
            # Check time format (HH:MM:SS.mmm)
            self.assertRegex(output, r"\d{2}:\d{2}:\d{2}\.\d{3}")

    def test_verbosity_filtering(self):
        """Test message filtering by verbosity."""
        self.printer.verbosity = Verbosity.WARNING
        with captured_output() as out:
            self.printer.debug("debug")  # Should not print
            self.printer.info("info")    # Should not print
            self.printer.warning("warn") # Should print
            self.printer.error("error")  # Should print
            
            output = out.getvalue()
            self.assertNotIn("debug", output)
            self.assertNotIn("info", output)
            self.assertIn("warn", output)
            self.assertIn("error", output)

    def test_bare_output(self):
        """Test bare (unformatted) output."""
        with captured_output() as out:
            self.printer.info("test", bare=True)
            output = out.getvalue()
            self.assertEqual(output.strip(), "test")

    def test_color_output(self):
        """Test colored output."""
        with captured_output() as out:
            self.printer.info("test", color="red")
            output = out.getvalue()
            self.assertIn(TextColors.CODES["red"], output)
            self.assertIn(TextColors.CODES["reset"], output)

    def test_copy(self):
        """Test printer copying."""
        copy = self.printer.copy()
        self.assertEqual(copy.verbosity, self.printer.verbosity)
        self.assertEqual(copy._formatter._fmt, self.printer._formatter._fmt)
        self.assertEqual(copy._name, self.printer._name)

class TestVerbositySwitch(unittest.TestCase):
    """Test verbosity switching context manager."""

    def test_switch_verbosity(self):
        """Test temporary verbosity switching."""
        printer = Logger(verbosity=Verbosity.INFO)
        
        self.assertEqual(printer.verbosity, Verbosity.INFO)
        
        with switch_verbosity(printer, Verbosity.DEBUG):
            self.assertEqual(printer.verbosity, Verbosity.DEBUG)
            
        self.assertEqual(printer.verbosity, Verbosity.INFO)

    def test_switch_verbosity_with_exception(self):
        """Test verbosity restoration after exception."""
        printer = Logger(verbosity=Verbosity.INFO)
        
        try:
            with switch_verbosity(printer, Verbosity.DEBUG):
                raise Exception("test error")
        except Exception:
            pass
            
        self.assertEqual(printer.verbosity, Verbosity.INFO)

class TestDefaultFormat(unittest.TestCase):
    """Test default format setting."""

    def test_set_default_format(self):
        """Test setting default format."""
        set_default_log_format("detailed")
        printer = Logger()  # Should use new default
        self.assertEqual(
            printer._formatter._fmt,
            Logger.FORMATS["detailed"]
        )

        set_default_log_format("basic")  # Reset to default
        printer = Logger()
        self.assertEqual(
            printer._formatter._fmt,
            Logger.FORMATS["basic"]
        )

if __name__ == '__main__':
    unittest.main()
