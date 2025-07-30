"""
Terminal output formatting and verbosity control.

This module provides utilities for formatted console output with color support,
verbosity levels, and comparison formatting. Designed for minimal overhead
in performance-critical I/O operations.
"""

from __future__ import annotations

import os
import sys
import time
import difflib
import logging
import traceback
import threading
from typing import Dict, Union, Optional, ClassVar, Generator, TypeVar
from functools import total_ordering
from contextlib import contextmanager

from .enums import DescriptiveEnum

__all__ = ['TextColors', 'Verbosity', 'Logger', 'set_default_log_format', 'switch_verbosity', 'set_verbosity']

# Type aliases
VerbosityLevel = Union[int, 'Verbosity', str]
T = TypeVar('T')

class TextColors:
    """ANSI color codes for terminal output."""
    
    CODES: ClassVar[Dict[str, str]] = {
        # Standard colors
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        # Bright colors
        'bright black': '\033[30;1m',
        'bright red': '\033[31;1m',
        'bright green': '\033[32;1m',
        'bright yellow': '\033[33;1m',
        'bright blue': '\033[34;1m',
        'bright magenta': '\033[35;1m',
        'bright cyan': '\033[36;1m',
        'bright white': '\033[37;1m',
        # Special colors
        'darkred': '\033[91m',
        'okgreen': '\033[92m',
        # Control
        'reset': '\033[0m',
    }

    @classmethod
    def colorize(cls, text: str, color: Optional[str]) -> str:
        """Apply color formatting to text."""
        if not color:
            return text
        
        color_code = cls.CODES.get(color)
        if not color_code:
            return text
            
        return f"{color_code}{text}{cls.CODES['reset']}"

    @classmethod
    def format_comparison(
        cls,
        text_left: str,
        text_right: str, 
        equal_color: Optional[str] = None,
        delete_color: str = "red",
        insert_color: str = "green"
    ) -> tuple[str, str]:
        """Format text comparison with color coding."""
        matcher = difflib.SequenceMatcher(a=text_left, b=text_right)
        left_result = []
        right_result = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                text = cls.colorize(text_left[i1:i2], equal_color)
                left_result.append(text)
                right_result.append(text)
            elif tag == "delete":
                left_result.append(cls.colorize(text_left[i1:i2], delete_color))
            elif tag == "insert":
                right_result.append(cls.colorize(text_right[j1:j2], insert_color))
            elif tag == "replace":
                left_result.append(cls.colorize(text_left[i1:i2], delete_color))
                right_result.append(cls.colorize(text_right[j1:j2], insert_color))
                
        return "".join(left_result), "".join(right_result)

@total_ordering
class Verbosity(DescriptiveEnum):
    """
    Verbosity levels for output control.
    
    Attributes
    ----------
    SILENT : Verbosity
        No output (level 100)
    CRITICAL : Verbosity
        Critical errors only (level 50)
    ERROR : Verbosity
        Errors and above (level 40)
    TIPS : Verbosity
        Tips and above (level 35)
    WARNING : Verbosity
        Warnings and above (level 30)
    INFO : Verbosity
        Information and above (level 20)
    DEBUG : Verbosity
        All output including debug (level 10)
    IGNORE : Verbosity
        Process all messages (level 0)
    """
    
    SILENT = (100, 'SILENT')
    CRITICAL = (50, 'CRITICAL')
    ERROR = (40, 'ERROR')
    TIPS = (35, 'TIPS')
    WARNING = (30, 'WARNING')
    INFO = (20, 'INFO')
    DEBUG = (10, 'DEBUG')
    IGNORE = (0, 'IGNORE')
    
    def __lt__(self, other: Union[Verbosity, int, str]) -> bool:
        if isinstance(other, type(self)):
            return self.value < other.value
        if isinstance(other, int):
            return self.value < other
        if isinstance(other, str):
            try:
                other_level = getattr(self.__class__, other.upper())
                return self.value < other_level.value
            except AttributeError:
                return NotImplemented
        return NotImplemented


class Logger:
    """
    Configurable logger with formatting support.
    
    Attributes
    ----------
    FORMATS : ClassVar[Dict[str, str]]
        Predefined format templates
    DEFAULT_FORMAT : ClassVar[str]
        Default message format
    DEFAULT_DATEFORMAT : ClassVar[str]
        Default date format
    DEFAULT_MSECFORMAT : ClassVar[str]
        Default millisecond format
    """
    
    FORMATS: ClassVar[Dict[str, str]] = {
        'basic': '[%(levelname)s] %(message)s',
        'detailed': '%(asctime)s | PID:%(process)d, TID:%(threadName)s | %(levelname)s | %(message)s'
    }
    
    DEFAULT_FORMAT: ClassVar[str] = FORMATS['basic']
    DEFAULT_DATEFORMAT: ClassVar[str] = '%Y-%m-%d %H:%M:%S'
    DEFAULT_MSECFORMAT: ClassVar[str] = '%s.%03d'

    def __init__(
        self,
        verbosity: VerbosityLevel = Verbosity.INFO,
        fmt: Optional[str] = None,
        name: str = '',
        msecfmt: Optional[str] = None,
        datefmt: Optional[str] = None
    ):
        """
        Initialize Logger with custom configuration.

        Parameters
        ----------
        verbosity : VerbosityLevel, optional
            Initial verbosity level, by default Verbosity.INFO
        fmt : str, optional
            Message format template or format name ('basic' or 'detailed')
        name : str, optional
            Logger name for message formatting
        msecfmt : str, optional
            Millisecond format string, default is '%s.%03d'
        datefmt : str, optional
            Date format string (strftime format), default is '%Y-%m-%d %H:%M:%S'
        """
        self._verbosity = Verbosity.parse(verbosity)
        self._name = name
        self.set_timefmt(datefmt, msecfmt)
        self.set_format(fmt)

    @property
    def verbosity(self) -> Verbosity:
        """Current verbosity level."""
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value: VerbosityLevel) -> None:
        """Set verbosity level."""
        self._verbosity = Verbosity.parse(value)

    def __call__(
        self,
        text: str,
        verbosity: VerbosityLevel = Verbosity.INFO,
        color: Optional[str] = None,
        bare: bool = False
    ) -> None:
        """Print text with specified verbosity and formatting."""
        level = Verbosity.parse(verbosity)
        if level < self.verbosity:
            return

        if not bare:
            text = self._format_message(text, level)
        
        if color:
            text = TextColors.colorize(text, color)
            
        sys.stdout.write(f"{text}\n")

    def _format_message(self, text: str, level: Verbosity) -> str:
        """Format message with current configuration."""
        args = {
            'name': self._name,
            'message': text,
            'levelname': level.description,
        }
        
        if self._needs_time:
            args['asctime'] = self.format_time()
        
        if self._needs_process:
            args['process'] = os.getpid() if hasattr(os, 'getpid') else None
            
        if self._needs_thread and threading:
            args['thread'] = threading.get_ident()
            args['threadName'] = threading.current_thread().name
                
        return self._formatter._fmt % args

    def format_time(self) -> str:
        """Format current time according to configuration."""
        current_time = time.time()
        time_struct = self._formatter.converter(current_time)
        base_time = time.strftime(self._datefmt, time_struct)
        
        if self._msecfmt:
            msecs = int((current_time - int(current_time)) * 1000)
            return self._msecfmt % (base_time, msecs)
        
        return base_time

    def set_format(self, fmt: Optional[str] = None) -> None:
        """
        Set message format template.

        Parameters
        ----------
        fmt : str, optional
            Format template or name ('basic' or 'detailed').
            If None, uses DEFAULT_FORMAT.
        """
        fmt = fmt or self.DEFAULT_FORMAT
        if fmt in self.FORMATS:
            fmt = self.FORMATS[fmt]
        self._formatter = logging.Formatter(fmt)
        
        self._needs_time = '%(asctime)' in fmt
        self._needs_process = '%(process)' in fmt
        self._needs_thread = any(key in fmt for key in ('%(thread)', '%(threadName)'))        

    def set_timefmt(
        self,
        datefmt: Optional[str] = None,
        msecfmt: Optional[str] = None
    ) -> None:
        """
        Set time format for timestamps.

        Parameters
        ----------
        datefmt : str, optional
            Date format string (strftime format). If None, uses DEFAULT_DATEFORMAT
        msecfmt : str, optional
            Millisecond format string. If None, uses DEFAULT_MSECFORMAT.
            Set to empty string to disable milliseconds.

        Examples
        --------
        >>> printer = Logger(fmt='detailed')
        >>> printer.set_timefmt(datefmt='%H:%M:%S')  # Time only
        >>> printer.info('Test')
        12:34:56.123 | PID:1234, TID:MainThread | INFO | Test
        
        >>> printer.set_timefmt(msecfmt='')  # Disable milliseconds
        >>> printer.info('Test')
        12:34:56 | PID:1234, TID:MainThread | INFO | Test
        """
        self._datefmt = datefmt or self.DEFAULT_DATEFORMAT
        self._msecfmt = msecfmt or self.DEFAULT_MSECFORMAT

    # Convenience methods for different verbosity levels
    def silent(self, text: str = '', color: Optional[str] = None, bare: bool = False) -> None:
        """No output."""
        pass

    def debug(self, text: str = '', color: Optional[str] = None, bare: bool = False) -> None:
        """Print debug message."""
        self(text, Verbosity.DEBUG, color, bare)

    def info(self, text: str = '', color: Optional[str] = None, bare: bool = False) -> None:
        """Print info message."""
        self(text, Verbosity.INFO, color, bare)

    def warning(self, text: str = '', color: Optional[str] = None, bare: bool = False) -> None:
        """Print warning message."""
        self(text, Verbosity.WARNING, color, bare)

    def error(self, text: str = '', color: Optional[str] = None, bare: bool = False) -> None:
        """Print error message."""
        self(text, Verbosity.ERROR, color, bare)

    def critical(self, text: str = '', color: Optional[str] = None, bare: bool = False) -> None:
        """Print critical message."""
        self(text, Verbosity.CRITICAL, color, bare)

    def tips(self, text: str = '', color: Optional[str] = None, bare: bool = False) -> None:
        """Print tip message."""
        self(text, Verbosity.TIPS, color, bare)

    def write(self, text: str = '', color: Optional[str] = None) -> None:
        """Write raw text."""
        self(text, Verbosity.SILENT, color, True)

    def copy(self) -> Logger:
        """Create a copy of this printer."""
        return self.__class__(
            verbosity=self.verbosity,
            fmt=self._formatter._fmt,
            name=self._name,
            msecfmt=self._msecfmt,
            datefmt=self._datefmt
        )

# global logger
_LOGGER_: ClassVar[Logger] = Logger(Verbosity.INFO)

@contextmanager
def switch_verbosity(target: Logger, verbosity: VerbosityLevel) -> Generator[None, None, None]:
    """
    Temporarily change verbosity level.
    
    Parameters
    ----------
    target : Logger
        Logger to modify
    verbosity : Union[int, str, Verbosity]
        New verbosity level
    """
    original = target.verbosity
    try:
        target.verbosity = verbosity
        yield
    except Exception:
        traceback.print_exc(file=sys.stdout)
    finally:
        target.verbosity = original

def set_verbosity(verbosity: Union[str, VerbosityLevel] = 'INFO'):
    _LOGGER_.verbosity = verbosity
    
def set_default_log_format(fmt: str = 'basic') -> None:
    """
    Set default format for new Logger instances.
    
    Parameters
    ----------
    fmt : str
        Format name or template
    """
    Logger.DEFAULT_FORMAT = (
        Logger.FORMATS.get(fmt, fmt)
    )