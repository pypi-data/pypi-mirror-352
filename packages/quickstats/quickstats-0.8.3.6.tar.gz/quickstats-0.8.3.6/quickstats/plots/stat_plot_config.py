from __future__ import annotations

from typing import Dict, List, Optional, Callable, Any, TypeVar, Union

import numpy as np
from numpy.typing import NDArray

from quickstats import GeneralEnum

T = TypeVar('T', bound=np.number)

class StatMeasure(GeneralEnum):
    """Statistical measure enumeration with associated numpy operations."""
    
    MEAN = (0, np.mean)
    STD = (1, np.std)
    MIN = (2, np.min)
    MAX = (3, np.max)
    MEDIAN = (4, np.median)
    
    def __new__(cls, value: int, operator: Callable[[NDArray[T]], T]) -> StatMeasure:
        obj = object.__new__(cls)
        obj._value_ = value
        obj.operator = operator
        return obj

class StatPlotConfig:
    """Configuration for statistical plot elements."""
    
    @property
    def stat_measures(self) -> List[StatMeasure]:
        """Get statistical measures."""
        return self._stat_measures
    
    @stat_measures.setter
    def stat_measures(self, values: List[Union[StatMeasure, str]]) -> None:
        """Set statistical measures with validation."""
        self._stat_measures = [StatMeasure.parse(value) for value in values]

    def __init__(
        self,
        stat_measures: List[Union[StatMeasure, str]],
        axis_method: str,
        options: Dict[str, Any],
        handle_options: Optional[Dict[str, Callable]] = None,
        handle_return_method: Optional[Callable] = None
    ) -> None:
        """
        Initialize statistical plot configuration.

        Parameters
        ----------
        stat_measures : List[Union[StatMeasure, str]]
            List of statistical measures to compute
        axis_method : str
            Matplotlib axes method to call
        options : Dict[str, Any]
            Options for the plot method
        handle_options : Optional[Dict[str, Callable]], default None
            Options derived from handle properties
        handle_return_method : Optional[Callable], default None
            Method to process the returned handle
        """
        self.stat_measures = stat_measures
        self.axis_method = axis_method
        self.options = options
        self.handle_options = handle_options or self.get_default_handle_options()
        self.quantities: Dict[str, float] = {}
        self.handle_return_method = handle_return_method

    def set_data(self, data: NDArray[T]) -> None:
        """
        Compute statistical measures from data.

        Parameters
        ----------
        data : numpy.ndarray
            Input data array
        """
        self.quantities = {
            measure.name.lower(): measure.operator(data)
            for measure in self.stat_measures
        }

    def get_default_handle_options(self) -> Dict[str, Callable]:
        """Get default handle options."""
        return {}

    def apply(self, ax: Any, main_handle: Optional[Any] = None) -> Any:
        """
        Apply statistical plot to axes.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Target axes
        main_handle : Optional[Any], default None
            Main plot handle for style matching

        Returns
        -------
        Any
            Plot handle or processed result

        Raises
        ------
        RuntimeError
            If method not found or data not initialized
        """
        if not hasattr(ax, self.axis_method):
            raise RuntimeError(f"Axes has no method: {self.axis_method}")
        if not self.quantities:
            raise RuntimeError("Statistical data not initialized")

        method = getattr(ax, self.axis_method)
        resolved_options = {
            name: option(self.quantities) if callable(option) else option
            for name, option in self.options.items()
        }

        if main_handle is not None and self.handle_options:
            for name, option in self.handle_options.items():
                if name not in resolved_options:
                    resolved_options[name] = option(main_handle)

        result = method(**resolved_options)
        if self.handle_return_method is not None:
            return self.handle_return_method(result)
        return result

class HandleMatchConfig(StatPlotConfig):
    """Base class for configurations with handle property matching."""

    def get_default_handle_options(self) -> Dict[str, Callable]:
        """Get default color-matching options."""
        return {"color": lambda handle: handle.get_color()}

class AverageLineH(HandleMatchConfig):
    """Horizontal average line configuration."""

    def __init__(self, **styles: Any) -> None:
        super().__init__(
            ["mean"],
            "axhline",
            options={"y": lambda x: x["mean"], **styles}
        )

class AverageLineV(HandleMatchConfig):
    """Vertical average line configuration."""

    def __init__(self, **styles: Any) -> None:
        super().__init__(
            ["mean"],
            "axvline",
            options={"x": lambda x: x["mean"], **styles}
        )

class StdBandH(HandleMatchConfig):
    """Horizontal standard deviation band configuration."""

    def __init__(self, **styles: Any) -> None:
        super().__init__(
            ["mean", "std"],
            "axhspan",
            options={
                "ymin": lambda x: x["mean"] - x["std"],
                "ymax": lambda x: x["mean"] + x["std"],
                **styles
            }
        )

class StdBandV(HandleMatchConfig):
    """Vertical standard deviation band configuration."""

    def __init__(self, **styles: Any) -> None:
        super().__init__(
            ["mean", "std"],
            "axvspan",
            options={
                "xmin": lambda x: x["mean"] - x["std"],
                "xmax": lambda x: x["mean"] + x["std"],
                **styles
            }
        )