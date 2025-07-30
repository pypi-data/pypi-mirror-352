from __future__ import annotations

from typing import (
    Optional, Union, Tuple, Any, Callable, Dict, List,
    TypeVar
)
try:
    from collections.abc import Iterable
except ImportError:
    from typing import Iterable
from numbers import Real

import numpy as np

from quickstats import stdout
from quickstats.core.typing import ArrayLike, ArrayContainer
from quickstats.maths.histograms import BinErrorMode
from .binning import Binning
from .histogram1d import Histogram1D, BinErrors

T = TypeVar('T', bound='StackedHistogram')
HistKey = Union[str, int]
HistDict = Dict[HistKey, Histogram1D]
HistList = Union[Dict[str, Histogram1D], List[Histogram1D]]
ConditionType = Union[Tuple[float, ...], Callable]

def deduce_bin_range(*arrays: ArrayLike) -> Optional[Tuple[float, float]]:
    """
    Deduce the global range across multiple arrays.

    Parameters
    ----------
    *arrays : ArrayLike
        Arrays to analyze

    Returns
    -------
    Optional[Tuple[float, float]]
        (min, max) range or None if no arrays provided
    """
    if not arrays:
        return None

    min_range = min(np.min(array) for array in arrays)
    max_range = max(np.max(array) for array in arrays)
    return (min_range, max_range)

class StackedHistogram(Histogram1D):
    """
    A class for managing stacked histograms.
    
    This class provides functionality for working with multiple histograms
    that can be stacked together, supporting both named and indexed access.

    Attributes
    ----------
    histograms : Dict[HistKey, Histogram1D]
        The component histograms
    bin_content : np.ndarray
        Total stacked bin content
    bin_edges : np.ndarray
        Bin edge locations
    bin_errors : BinErrors
        Combined bin errors if available
    """

    def __init__(
        self,
        histograms: Optional[HistList] = None
    ) -> None:
        """
        Initialize StackedHistogram.

        Parameters
        ----------
        histograms : Optional[HistList], default None
            Initial histograms to stack. Can be:
            - Dictionary mapping names to histograms
            - List of histograms (accessed by index)
        """
        self.reset()
        if histograms is not None:
            self.set_histograms(histograms)

    @property
    def _ghost_weight(self):
        return self._stacked_histogram._ghost_weight

    @property
    def _bin_content(self):
        return self._stacked_histogram._bin_content

    @property
    def _binning(self):
        return self._stacked_histogram._binning

    @property
    def _bin_errors(self):
        return self._stacked_histogram._bin_errors

    @property
    def _error_mode(self):
        return self._stacked_histogram._error_mode

    @property
    def _bin_content_raw(self):
        return self._stacked_histogram._bin_content_raw

    @property
    def _bin_errors_raw(self):
        return self._stacked_histogram._bin_errors_raw

    @property
    def _mask(self):
        return self._stacked_histogram._mask

    def _ioperate(self, method: str, other: Any):
        raise RuntimeError('Method not allowed')

    def set_data(self):
        raise RuntimeError('Method not allowed')
        
    @classmethod
    def create(
        cls: type[T],
        sample: Union[Dict[str, ArrayLike], ArrayContainer],
        weights: Optional[Union[Dict[str, ArrayLike], ArrayContainer]] = None,
        bins: Union[int, ArrayLike] = 10,
        bin_range: Optional[ArrayLike] = None,
        underflow: bool = False,
        overflow: bool = False,
        divide_bin_width: bool = False,
        normalize: bool = False,
        clip_weight: bool = False,
        evaluate_error: bool = True,
        error_mode: Union[BinErrorMode, str] = "auto",
        **kwargs: Any
    ) -> T:
        """
        Create stacked histogram from unbinned data.

        Parameters
        ----------
        sample : Union[Dict[str, ArrayLike], ArrayContainer]
            Input data arrays. Can be:
            - Dictionary mapping names to arrays
            - List/tuple/array of arrays (accessed by index)
        weights : Optional[Union[Dict[str, ArrayLike], ArrayContainer]], default None
            Optional weights for each sample
        bins : Union[int, ArrayLike], default 10
            Number of bins or bin edges
        bin_range : Optional[ArrayLike], default None
            Optional (min, max) range for binning
        underflow : bool, default False
            Include underflow in first bin
        overflow : bool, default False
            Include overflow in last bin
        divide_bin_width : bool, default False
            Normalize by bin width
        normalize : bool, default False
            Normalize stacked result
        clip_weight : bool, default False
            Ignore out-of-range weights
        evaluate_error : bool, default True
            Calculate bin errors
        error_mode : Union[BinErrorMode, str], default "auto"
            Error calculation mode
        **kwargs : Any
            Additional histogram creation options

        Returns
        -------
        T
            New StackedHistogram instance

        Raises
        ------
        ValueError
            If sample is empty
            If incompatible arrays provided
        TypeError
            If invalid sample type
        """
        if not sample:
            raise ValueError('Empty sample provided')

        try:
            if isinstance(sample, dict):
                keys = list(sample.keys())
                indexed = False
            elif isinstance(sample, (tuple, list, np.ndarray)):
                keys = list(range(len(sample)))
                indexed = True
            else:
                raise TypeError(
                    'Sample must be dictionary or sequence of arrays'
                )

            if bin_range is None:
                bin_range = deduce_bin_range(
                    *(sample[key] for key in keys)
                )

            if weights is None:
                weights = {k: None for k in keys}

            histograms: Union[List[Optional[Histogram1D]], Dict[str, Histogram1D]]
            histograms = [None] * len(keys) if indexed else {}
            
            for key in keys:
                histograms[key] = Histogram1D.create(
                    x=sample[key],
                    weights=weights[key],
                    bins=bins,
                    bin_range=bin_range,
                    underflow=underflow,
                    overflow=overflow,
                    divide_bin_width=False,  # Handle later
                    normalize=False,  # Handle later
                    clip_weight=clip_weight,
                    evaluate_error=evaluate_error,
                    error_mode=error_mode,
                    **kwargs
                )

            instance = cls(histograms=histograms)
            if normalize:
                instance.normalize(
                    density=divide_bin_width,
                    inplace=True
                )
            return instance

        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                raise
            raise ValueError(f"Failed to create stacked histogram: {str(e)}") from e

    @property
    def stacked_histogram(self) -> Histogram1D:
        return self._stacked_histogram

    @property
    def histograms(self) -> HistDict:
        """Get dictionary of component histograms."""
        return self._histograms

    def offset_histograms(self) -> Iterator[Tuple[HistKey, Histogram1D]]:
        """
        Generate histograms with cumulative offsets for stacking.

        Each histogram is offset by the sum of all previous histograms,
        creating the stacked effect.

        Yields
        ------
        Tuple[HistKey, Histogram1D]
            (name/index, offset histogram) pairs

        Examples
        --------
        >>> for name, hist in stacked.offset_histograms():
        ...     plt.fill_between(hist.bin_centers, hist.bin_content)
        """
        base_histogram = Histogram1D(
            bin_content=np.zeros_like(self.bin_content),
            bin_edges=self.bin_edges
        )
        for name, histogram in self._histograms.items():
            offset_hist = histogram + base_histogram
            yield name, offset_hist
            base_histogram += histogram

    def reset(self) -> None:
        """Reset to initial empty state."""
        self._indexed = True
        self._histograms = {}
        self._stacked_histogram = Histogram1D(
            bin_content=np.array([0]),
            bin_edges=np.array([0, 1])
        )

    def add_histogram(
        self,
        histogram: Histogram1D,
        name: Optional[HistKey] = None
    ) -> None:
        """
        Add histogram to stack.

        Parameters
        ----------
        histogram : Histogram1D
            Histogram to add
        name : Optional[HistKey], default None
            Name for histogram if using named access

        Raises
        ------
        TypeError
            If histogram is not Histogram1D
        ValueError
            If name handling is inconsistent with current mode
        """
        if not isinstance(histogram, Histogram1D):
            raise TypeError('Histogram must be Histogram1D instance')

        if self.indexed:
            if name is not None and name != self.count:
                raise ValueError(
                    'Cannot specify histogram name in indexed mode'
                )
            name = self.count
        else:
            if name is None:
                raise ValueError(
                    'Must specify histogram name in named mode'
                )

        if self.is_empty():
            self._stacked_histogram = histogram.copy()
        else:
            self._stacked_histogram += histogram
        self._histograms[name] = histogram

    def set_histograms(self, histograms: HistList) -> None:
        """
        Set multiple histograms to stack.

        Parameters
        ----------
        histograms : HistList
            Dictionary or list of histograms

        Raises
        ------
        TypeError
            If histograms has invalid type
        """
        self.reset()
        if isinstance(histograms, dict):
            self._indexed = False
            for name, histogram in histograms.items():
                self.add_histogram(histogram, name=name)
        elif isinstance(histograms, (list, tuple)):
            self._indexed = True
            for histogram in histograms:
                self.add_histogram(histogram)
        else:
            raise TypeError(
                'Histograms must be dictionary or sequence'
            )

    @property
    def indexed(self) -> bool:
        """Check if using indexed access mode."""
        return self._indexed

    @property
    def count(self) -> int:
        """Get number of histograms in stack."""
        return len(self._histograms)

    def normalize(
        self,
        density: bool = False,
        inplace: bool = False
    ) -> StackedHistogram:
        """
        Normalize stacked histograms.

        Parameters
        ----------
        density : bool, default False
            Normalize by bin widths
        inplace : bool, default False
            Modify in place

        Returns
        -------
        StackedHistogram
            Normalized stack
        """
        result = self if inplace else self.copy()
        count = self.count
        if count == 0:
            return result
            
        for histogram in result._histograms.values():
            histogram.normalize(density=density, inplace=True)
            histogram /= count
            
        result._stacked_histogram.normalize(density=density, inplace=True)
        return result

    def copy(self) -> StackedHistogram:
        """
        Create deep copy of stack.

        Returns
        -------
        StackedHistogram
            New instance with copied data
        """
        histograms = {
            key: histogram.copy() 
            for key, histogram in self._histograms.items()
        }
        instance = type(self)()
        instance._indexed = self._indexed
        instance._histograms = histograms
        instance._stacked_histogram = self._stacked_histogram.copy()
        return instance

    def scale(
        self,
        val: Union[Real, ArrayLike]
    ) -> Histogram1D:
        return self.stacked_histogram.scale(val=val, inplace=False)

    def reweight(
        self,
        other: Histogram1D,
        subranges: Optional[Union[List[ArrayLike], MultiRange]] = None
    ) -> Histogram1D:
        if isinstance(other, StackedHistogram):
            other = other.stacked_histogram
        return self.stacked_histogram.reweight(other=other, subranges=subranges, inplace=False)

    def apply_ghost(
        self,
        ghost_weight: Optional[float] = None
    ) -> Histogram1D:
        return self.stacked_histogram.apply_ghost(ghost_weight=ghost_weight, inplace=False)

    def remove_ghost(
        self,
        ghost_threshold: Optional[float] = None
    ) -> Histogram1D:
        return self.stacked_histogram.remove_ghost(ghost_threshold=ghost_threshold, inplace=False)

    def rebin(
        self,
        bins: Union[ArrayLike, int],
        keep_ghost: bool = True
    ) -> Histogram1D:
        return self.stacked_histogram.rebin(bins=bins, keep_ghost=keep_ghost, inplace=False)