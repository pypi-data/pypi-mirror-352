"""
Base class providing output and verbosity control functionality.

This module defines the AbstractObject class, which serves as a base for
objects requiring configurable verbosity and output handling.
"""

from __future__ import annotations

from typing import Any, Optional, Union, Type
from .decorators import hybridproperty
from .logger import Verbosity, Logger, _LOGGER_


class AbstractObject:
    """
    Base class with verbosity control and standardized output management.
    
    This class provides a foundation for objects requiring configurable
    output verbosity and standardized logging. It supports both class-level
    and instance-level logging configurations.

    Parameters
    ----------
    verbosity : Optional[Union[int, str, Verbosity]], default=None
        The verbosity level for controlling output. If None, uses the
        class-level default verbosity. Must be None if logger is provided.
    logger : Optional[Logger], default=None
        A custom logger instance to use. If provided, verbosity must be None.
    **kwargs : Any
        Additional keyword arguments for subclasses.

    Attributes
    ----------
    stdout : Logger
        Logging handler with verbosity control.
    debug_mode : bool
        Indicates whether the current verbosity level is `DEBUG`.

    Examples
    --------
    >>> class MyObject(AbstractObject):
    ...     def process(self):
    ...         self.stdout.info("Processing...")
    ...
    >>> obj = MyObject(verbosity="DEBUG")
    >>> obj.stdout.debug("Debug message")
    [DEBUG] Debug message
    >>> custom_logger = Logger("INFO")
    >>> obj2 = MyObject(logger=custom_logger)
    """

    _class_stdout = _LOGGER_

    def __init__(
        self,
        verbosity: Optional[Union[int, str, Verbosity]] = None,
        logger: Optional[Logger] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize an AbstractObject with the specified verbosity or logger.

        Parameters
        ----------
        verbosity : Optional[Union[int, str, Verbosity]], default=None
            The verbosity level for controlling output. Must be None if logger is provided.
        logger : Optional[Logger], default=None
            A custom logger instance to use. If provided, verbosity must be None.
        **kwargs : Any
            Additional keyword arguments for subclasses.
            
        Raises
        ------
        ValueError
            If both verbosity and logger are provided.
        """
        self._stdout: Optional[Logger] = None
        
        if logger is not None:
            if verbosity is not None:
                raise ValueError("Cannot specify both 'verbosity' and 'logger'. When 'logger' is provided, 'verbosity' must be None.")
            self._stdout = logger
        else:
            self.set_verbosity(verbosity)
            
        super().__init__()

    @hybridproperty
    def stdout(cls) -> Logger:
        """
        Class-level logging handler.

        Returns
        -------
        Logger
            The class-level logging handler.
        """
        return cls._class_stdout

    @stdout.instance
    def stdout(self) -> Logger:
        """
        Instance-level logging handler.

        Returns
        -------
        Logger
            The instance-level logging handler.
        """
        return self._stdout

    @property
    def debug_mode(self) -> bool:
        """
        Check if the current verbosity level is `DEBUG`.

        Returns
        -------
        bool
            True if the verbosity level is `DEBUG`, otherwise False.
        """
        return self._stdout.verbosity == Verbosity.DEBUG

    @property
    def verbosity(self) -> Verbosity:
        """
        Get the current verbosity level.

        Returns
        -------
        Verbosity
            The current verbosity level.
        """
        return self._stdout.verbosity

    @property
    def init_verbosity(self) -> Optional[Verbosity]:
        """
        Get the initial verbosity level.

        If the instance uses the class-level logger, this will return None.

        Returns
        -------
        Optional[Verbosity]
            The initial verbosity level, or None if using the class-level logger.
        """
        if self._stdout == self.__class__._class_stdout:
            return None
        return self.verbosity

    def set_verbosity(
        self,
        verbosity: Optional[Union[int, str, Verbosity]] = None,
    ) -> None:
        """
        Change the verbosity level for the instance.

        This method detaches the instance from the class-level logging handler
        and creates a new instance-specific logging handler with the specified
        verbosity level.

        Parameters
        ----------
        verbosity : Optional[Union[int, str, Verbosity]], default=None
            The new verbosity level. If None, uses the class-level default.

        Raises
        ------
        ValueError
            If the verbosity level is invalid.

        Examples
        --------
        >>> obj = AbstractObject()
        >>> obj.set_verbosity("DEBUG")
        >>> obj.debug_mode
        True
        """
        if verbosity is not None:
            self._stdout = Logger(verbosity)
        else:
            self._stdout = self.__class__._class_stdout

    @classmethod
    def set_default_verbosity(
        cls,
        verbosity: Union[int, str, Verbosity],
    ) -> None:
        """
        Set the default verbosity level for the class.

        This method changes the class-level default verbosity, which affects
        all new instances that use the class-level logging handler.

        Parameters
        ----------
        verbosity : Union[int, str, Verbosity]
            The new default verbosity level.

        Examples
        --------
        >>> AbstractObject.set_default_verbosity("DEBUG")
        >>> obj = AbstractObject()  # Will use DEBUG level
        """
        cls._class_stdout = Logger(verbosity)