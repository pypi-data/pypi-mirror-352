"""
Flexible text representation generator for Python objects.

This module provides a customizable dumper for creating human-readable
text representations of nested Python data structures with support for
various formatting options and limits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Union, Sequence, Dict
from collections.abc import Mapping, Iterable


@dataclass
class DumperConfig:
    """
    Configuration settings for FlexibleDumper.

    Parameters
    ----------
    item_indent : str
        Indentation string for regular items
    list_indent : str
        Indentation string for list items
    separator : str
        Separator between keys and values
    skip_str : str
        String to indicate truncation
    indent_sequence_on_key : bool
        Whether to indent sequences under their keys
    max_depth : int
        Maximum nesting depth (-1 for unlimited)
    max_iteration : int
        Maximum number of sequence items (-1 for unlimited)
    max_item : int
        Maximum number of mapping items (-1 for unlimited)
    max_line : int
        Maximum number of output lines (-1 for unlimited)
    max_len : int
        Maximum line length (-1 for unlimited)

    Raises
    ------
    ValueError
        If item_indent and list_indent have different lengths
    """

    item_indent: str = "  "
    list_indent: str = "- "
    separator: str = ": "
    skip_str: str = "..."
    indent_sequence_on_key: bool = True
    max_depth: int = -1
    max_iteration: int = -1
    max_item: int = -1
    max_line: int = -1
    max_len: int = -1

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if len(self.item_indent) != len(self.list_indent):
            raise ValueError("Length of item_indent must equal that of list_indent")
        
        for limit_name in ('max_depth', 'max_iteration', 'max_item', 'max_line', 'max_len'):
            value = getattr(self, limit_name)
            if not isinstance(value, int):
                raise TypeError(f"{limit_name} must be an integer")
            if value < -1:
                raise ValueError(f"{limit_name} must be >= -1")


class FlexibleDumper:
    """
    A flexible dumper that creates a text representation of Python objects.

    This class provides customizable formatting for nested data structures
    with support for depth limits, iteration limits, and line length limits.

    Parameters
    ----------
    **config_kwargs
        Keyword arguments passed to DumperConfig

    Examples
    --------
    >>> dumper = FlexibleDumper(max_depth=2, max_line=50)
    >>> data = {"a": [1, 2, {"b": 3}], "c": 4}
    >>> print(dumper.dump(data))
    a:
      - 1
      - 2
      - ...
    c: 4
    """

    def __init__(self, **config_kwargs) -> None:
        self.config = DumperConfig(**config_kwargs)
        self.reset()

    def configure(self, **kwargs) -> None:
        """
        Update the dumper configuration dynamically.

        Parameters
        ----------
        **kwargs : dict
            Configuration parameters to update. The keys should match
            attributes of the DumperConfig class.

        Raises
        ------
        ValueError
            If an unknown configuration parameter is provided.
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                raise ValueError(f"Unknown configuration parameter: '{key}'")    

    def reset(self) -> None:
        """Reset the internal state of the dumper."""
        self._terminate: bool = False
        self._terminate_depth: bool = False
        self._lines: List[str] = []

    def _get_indent(self, depth: int, iteration: int = 0, list_degree: int = 0) -> str:
        """
        Generate indentation string for current context.

        Parameters
        ----------
        depth : int
            Current nesting depth
        iteration : int, optional
            Current iteration number within a sequence
        list_degree : int, optional
            Number of nested lists at current position

        Returns
        -------
        str
            Formatted indentation string
        """
        if list_degree > 0:
            if iteration == 0:
                return (
                    self.config.item_indent * (depth - list_degree) + 
                    self.config.list_indent * list_degree
                )
            return (
                self.config.item_indent * (depth - 1) + 
                self.config.list_indent
            )
        return self.config.item_indent * depth

    def _add_line(
        self,
        text: str,
        depth: int,
        iteration: int = 0,
        item: int = 0,
        list_degree: int = 0
    ) -> None:
        """
        Add a formatted line to the output buffer.

        Parameters
        ----------
        text : str
            Text content to add
        depth : int
            Current nesting depth
        iteration : int, optional
            Current iteration number
        item : int, optional
            Current item number
        list_degree : int, optional
            Number of nested lists
        """
        if self._terminate:
            return

        if self.config.max_line > 0 and len(self._lines) >= self.config.max_line:
            self._lines.append(self.config.skip_str)
            self._terminate = True
            return

        if self._terminate_depth and depth <= self.config.max_depth:
            self._terminate_depth = False

        # Handle multiline text
        if '\n' in text:
            first, *rest = text.split('\n')
            self._add_line(first, depth, iteration, item, list_degree)
            for subtext in rest:
                self._add_line(subtext, depth, iteration, item, 0)
            return

        indent = self._get_indent(depth, iteration, list_degree)
        line = indent + text

        # Apply line length limit
        if self.config.max_len > 0 and len(line) > self.config.max_len:
            line = line[:max(len(indent), self.config.max_len)] + self.config.skip_str

        # Handle depth limit
        if self.config.max_depth > 0:
            if depth > self.config.max_depth:
                if not self._terminate_depth:
                    line = indent + self.config.skip_str
                    self._terminate_depth = True
                else:
                    return

        # Handle iteration limit
        if self.config.max_iteration > 0:
            if iteration >= self.config.max_iteration:
                if iteration == self.config.max_iteration:
                    base_indent = (
                        self._get_indent(depth, iteration, 0)
                        if list_degree > 0
                        else indent
                    )
                    line = base_indent + self.config.skip_str
                return

        # Handle item limit
        if self.config.max_item > 0:
            if item >= self.config.max_item:
                if item == self.config.max_item:
                    line = indent + self.config.skip_str
                return

        self._lines.append(line)

    def dump(
        self,
        data: Any,
        depth: int = 0,
        iteration: int = 0,
        list_degree: int = 0,
        root: bool = True
    ) -> Optional[str]:
        """
        Generate a formatted string representation of the data.

        Parameters
        ----------
        data : Any
            Data structure to dump
        depth : int, optional
            Current nesting depth
        iteration : int, optional
            Current iteration number
        list_degree : int, optional
            Number of nested lists
        root : bool, optional
            Whether this is the root call

        Returns
        -------
        Optional[str]
            Formatted string representation if root call,
            None for recursive calls

        Notes
        -----
        The method handles nested data structures recursively,
        applying configured limits and formatting rules.
        """
        if root:
            self.reset()

        if self._terminate or (
            self._terminate_depth and not (depth <= self.config.max_depth)
        ):
            return None

        # Normalize list degree for nested iterations
        if iteration > 0 and list_degree > 1:
            list_degree = 1

        # Handle mappings (dict-like objects)
        if isinstance(data, Mapping) and data:
            self._dump_mapping(data, depth, iteration, list_degree)
        
        # Handle sequences (list-like objects)
        elif isinstance(data, (list, tuple)) and data:
            self._dump_sequence(data, depth, iteration, list_degree)
        
        # Handle primitive values
        else:
            self._add_line(f"{data}", depth, iteration, list_degree=list_degree)

        if root:
            return '\n'.join(self._lines)
        return None

    def _dump_mapping(
        self,
        data: Mapping[Any, Any],
        depth: int,
        iteration: int,
        list_degree: int
    ) -> None:
        """Handle dumping of mapping types."""
        for item_num, (key, value) in enumerate(data.items()):
            if self.config.max_item > 0 and item_num >= self.config.max_item:
                if item_num == self.config.max_item:
                    self._add_line(
                        '',
                        depth,
                        iteration=iteration,
                        item=item_num,
                        list_degree=list_degree
                    )
                break

            if isinstance(value, (Mapping, Sequence)) and value:
                text = f"{key}{self.config.separator}"
                self._add_line(text, depth, iteration=iteration, list_degree=list_degree)
                
                next_depth = depth + (
                    0 if isinstance(value, (list, tuple))
                    and not self.config.indent_sequence_on_key
                    else 1
                )
                self.dump(value, next_depth, iteration, 0, root=False)
            else:
                text = f"{key}{self.config.separator}{value}"
                self._add_line(text, depth, iteration=iteration, list_degree=list_degree)
            
            list_degree = 0

    def _dump_sequence(
        self,
        data: Sequence[Any],
        depth: int,
        iteration: int,
        list_degree: int
    ) -> None:
        """Handle dumping of sequence types."""
        for idx, item in enumerate(data):
            if self.config.max_iteration > 0 and idx >= self.config.max_iteration:
                if idx == self.config.max_iteration:
                    self._add_line(
                        '',
                        depth,
                        iteration=idx,
                        list_degree=list_degree
                    )
                break
            
            self.dump(
                item,
                depth + 1,
                iteration=idx,
                list_degree=list_degree + 1,
                root=False
            )