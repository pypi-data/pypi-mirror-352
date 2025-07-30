"""
Enhanced histogram utilities for numerical data analysis.
"""

from __future__ import annotations

from typing import (
    Union, Optional, List, Tuple, Sequence, Callable, 
    TypeVar, Any, cast
)
from numbers import Real
from dataclasses import dataclass

import numpy as np

from quickstats import DescriptiveEnum
from quickstats.core.typing import ArrayLike
from quickstats.maths.numerics import all_integers
from .numerics import array_issubset, safe_div
from .statistics import poisson_interval

BinType = Union[int, ArrayLike]
RangeType = Optional[Union[Tuple[Real, Real], List[Real]]]
HistoMaskType = Union[ArrayLike, Callable]

class HistogramError(Exception):
    """Base exception for histogram-related errors."""
    pass

class BinError(HistogramError):
    """Exception for bin-related errors."""
    pass
    
class BinErrorMode(DescriptiveEnum):
    AUTO    = (0, "Determine bin error method from data weights")
    SUMW2   = (1, "Errors with Wald approximation: sqrt(sum of weight^2)")
    POISSON = (2, "Errors from Poisson interval at 68.3% (1 sigma)")
    
class HistComparisonMode(DescriptiveEnum):
    RATIO      = (0, "Ratio of data (target / reference)")
    DIFFERENCE = (1, "Difference of data (target - reference)")

@dataclass
class HistogramConfig:
    """Configuration for histogram operations."""
    bin_precision: int = 8
    ghost_threshold: float = 1e-8
    ghost_weight : float = 1e-9
    rtol: float = 1e-5
    atol: float = 1e-8

# Global configuration
CONFIG = HistogramConfig()

def bin_edge_to_bin_center(bin_edges: ArrayLike) -> np.ndarray:
    """
    Calculate bin centers from bin edges.

    Parameters
    ----------
    bin_edges : ArrayLike
        The edges of the bins

    Returns
    -------
    np.ndarray
        The centers of the bins

    Examples
    --------
    >>> bin_edges = [0, 1, 2, 3]
    >>> bin_edge_to_bin_center(bin_edges)
    array([0.5, 1.5, 2.5])
    """
    bin_edges = np.asarray(bin_edges)
    return (bin_edges[:-1] + bin_edges[1:]) / 2

def bin_center_to_bin_edge(
    bin_centers: ArrayLike, 
    allow_uneven: bool = False
) -> np.ndarray:
    """
    Calculate bin edges from bin centers, optionally allowing uneven bin widths.
    Uses vectorized operations for improved performance.
    
    Parameters
    ----------
    bin_centers : ArrayLike
        The centers of the bins
    allow_uneven : bool, default=False
        If True, allows uneven bin widths. If False, raises an error for uneven bins.
    
    Returns
    -------
    np.ndarray
        The edges of the bins
    
    Raises
    ------
    BinError
        If bin centers have irregular widths and allow_uneven is False
        
    Examples
    --------
    >>> # Even bins
    >>> bin_centers = [0.5, 1.5, 2.5]
    >>> bin_center_to_bin_edge(bin_centers)
    array([0., 1., 2., 3.])
    
    >>> # Uneven bins
    >>> bin_centers = [0.5, 2.0, 4.5]
    >>> bin_center_to_bin_edge(bin_centers, allow_uneven=True)
    array([-0.25, 1.25, 2.75, 6.25])
    """
    try:
        bin_centers = np.asarray(bin_centers)
        if len(bin_centers) < 2:
            raise BinError("Need at least two bin centers to determine edges")
            
        bin_widths = np.round(np.diff(bin_centers), CONFIG.bin_precision)
        
        # Check for even bins
        is_even = np.allclose(
            bin_widths, 
            bin_widths[0], 
            rtol=CONFIG.rtol, 
            atol=CONFIG.atol
        )
        
        if is_even:
            # Simple case - even bins
            bin_width = bin_widths[0]
            return np.concatenate([
                bin_centers - bin_width / 2,
                [bin_centers[-1] + bin_width / 2]
            ])
        
        elif not allow_uneven:
            raise BinError(
                "Cannot deduce edges from centers with irregular widths "
                "when allow_uneven=False"
            )
        
        else:
            # Uneven bins case
            # Calculate internal edges
            internal_edges = (bin_centers[1:] + bin_centers[:-1]) / 2
            
            # First and last edges using same width as nearest neighbor
            first_edge = bin_centers[0] - (internal_edges[0] - bin_centers[0])
            last_edge = bin_centers[-1] + (bin_centers[-1] - internal_edges[-1])
            
            return np.concatenate([[first_edge], internal_edges, [last_edge]])
        
    except Exception as e:
        raise BinError(f"Failed to convert centers to edges: {str(e)}") from e

def bin_edge_to_bin_width(bin_edges: ArrayLike) -> np.ndarray:
    """
    Calculate bin widths from bin edges.

    Parameters
    ----------
    bin_edges : ArrayLike
        The edges of the bins

    Returns
    -------
    np.ndarray
        The widths of the bins

    Examples
    --------
    >>> bin_edges = [0, 1, 2, 3]
    >>> bin_edge_to_bin_width(bin_edges)
    array([1, 1, 1])
    """
    bin_edges = np.asarray(bin_edges)
    return np.diff(bin_edges)

def get_clipped_data(
    x: np.ndarray,
    bin_range: Optional[Sequence] = None,
    clip_lower: bool = True,
    clip_upper: bool = True
) -> np.ndarray:
    """
    Clip data within specified range.

    Parameters
    ----------
    x : np.ndarray
        Data to be clipped
    bin_range : Optional[Sequence], default None
        Range (min, max) for clipping
    clip_lower : bool, default True
        Whether to clip at lower bound
    clip_upper : bool, default True
        Whether to clip at upper bound

    Returns
    -------
    np.ndarray
        Clipped array

    Examples
    --------
    >>> x = np.array([1, 5, 10, 15, 20])
    >>> get_clipped_data(x, (5, 15))
    array([ 5,  5, 10, 15, 15])
    """
    if bin_range is None or (not clip_lower and not clip_upper):
        return np.array(x)
        
    xmin = bin_range[0] if clip_lower else None
    xmax = bin_range[1] if clip_upper else None
    return np.clip(x, xmin, xmax)
    
def normalize_range(
    bin_range: Optional[Tuple[Optional[float], ...]] = None,
    dimension: int = 1
) -> Tuple[Optional[float], ...]:
    """
    Normalize range for each dimension.

    Parameters
    ----------
    bin_range : Optional[Tuple[Optional[float], ...]], default None
        Range for each dimension
    dimension : int, default 1
        Number of dimensions

    Returns
    -------
    Tuple[Optional[float], ...]
        Normalized range

    Raises
    ------
    BinError
        If range doesn't match dimensions

    Examples
    --------
    >>> normalize_range((0, 1), dimension=2)
    (0, 1)
    """
    try:
        if bin_range is None:
            return tuple(None for _ in range(dimension))
            
        if len(bin_range) != dimension:
            raise BinError(
                f"Range must have {dimension} entries, got {len(bin_range)}"
            )
            
        return tuple(bin_range)
        
    except Exception as e:
        raise BinError(f"Failed to normalize range: {str(e)}") from e

def get_histogram_bins(
    sample: ArrayLike,
    bins: BinType = 10,
    bin_range: RangeType = None,
    dimensions: int = 1
) -> Tuple[np.ndarray, ...]:
    """
    Calculate histogram bins for given sample.

    Parameters
    ----------
    sample : ArrayLike
        Input sample data (array or sequence of arrays)
    bins : BinType, default 10
        Number of bins or bin edges for each dimension
    bin_range : RangeType, default None
        Range for each dimension
    dimensions : int, default 1
        Number of dimensions

    Returns
    -------
    Tuple[np.ndarray, ...]
        Bin edges for each dimension

    Raises
    ------
    BinError
        For invalid bin specifications or dimensions
        
    Examples
    --------
    >>> sample = np.array([[1, 2], [3, 4], [5, 6]])
    >>> edges = get_histogram_bins(sample, bins=[3, 2], dimensions=2)
    >>> [e.shape for e in edges]
    [(4,), (3,)]
    """
    try:
        # Convert sample to ND array
        try:
            num_samples, sample_dimensions = np.atleast_2d(sample).shape
        except ValueError as e:
            raise BinError("Invalid sample shape") from e

        if sample_dimensions != dimensions:
            raise BinError(
                f"Sample has {sample_dimensions} dimensions, expected {dimensions}"
            )

        # Initialize arrays
        num_bins = np.empty(sample_dimensions, dtype=np.intp)
        bin_edges_list = [None] * sample_dimensions
        bin_values = _normalize_bins(bins, sample_dimensions)
        bin_range = normalize_range(bin_range, dimension=sample_dimensions)

        # Calculate edges for each dimension
        for i in range(sample_dimensions):
            bin_edges_list[i] = _get_dimension_edges(
                sample[:, i],
                bin_values[i],
                bin_range[i],
                dimension_idx=i
            )
            num_bins[i] = len(bin_edges_list[i]) + 1

        return tuple(bin_edges_list)

    except Exception as e:
        if not isinstance(e, BinError):
            e = BinError(f"Failed to calculate histogram bins: {str(e)}")
        raise e

def _normalize_bins(
    bins: BinType,
    dimensions: int
) -> List[Union[int, Sequence[float]]]:
    """Normalize bin specification to list form."""
    try:
        if isinstance(bins, (Sequence, np.ndarray)) and len(bins) == dimensions:
            return list(bins)
        if isinstance(bins, int):
            return [bins] * dimensions
        raise BinError(
            f"Bins must be integer or sequence of length {dimensions}"
        )
    except TypeError as e:
        raise BinError("Invalid bin specification") from e

def _get_dimension_edges(
    data: np.ndarray,
    bins: Union[int, Sequence[float]],
    bin_range: Optional[Sequence[float]],
    dimension_idx: int
) -> np.ndarray:
    """Calculate bin edges for one dimension."""
    from numpy.lib.histograms import _get_outer_edges
    
    if np.ndim(bins) == 0:
        if bins < 1:
            raise BinError(
                f"Number of bins must be positive, got {bins} for dimension {dimension_idx}"
            )
        
        min_val, max_val = _get_outer_edges(data, bin_range)
        return np.linspace(min_val, max_val, bins + 1)
        
    if np.ndim(bins) == 1:
        edges = np.asarray(bins)
        if not np.all(np.diff(edges) > 0):
            raise BinError(
                f"Bin edges must be monotonically increasing in dimension {dimension_idx}"
            )
        return edges
        
    raise BinError(
        f"Invalid bin specification for dimension {dimension_idx}"
    )        

def _calculate_bin_errors(
    bin_content: np.ndarray,
    x: np.ndarray,
    y: Optional[np.ndarray],
    weights: Optional[np.ndarray],
    bins: BinType,
    bin_range: RangeType,
    error_mode: Union[BinErrorMode, str],
    unweighted: bool,
    norm_factor: float,
    is_2d: bool = False
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """Calculate bin errors for histogram."""
    error_mode = BinErrorMode.parse(error_mode)
    
    if error_mode == BinErrorMode.AUTO:
        unweighted = unweighted or np.allclose(weights, np.ones_like(x))
        error_mode = (
            BinErrorMode.POISSON if unweighted
            else BinErrorMode.SUMW2
        )
    
    if error_mode == BinErrorMode.POISSON:
        if is_2d:
            errlo, errhi = poisson_interval(bin_content.flatten())
            errors = (
                errlo.reshape(bin_content.shape),
                errhi.reshape(bin_content.shape)
            )
        else:
            errors = poisson_interval(bin_content)
    else:  # SUMW2
        assert weights is not None
        if is_2d:
            bin_content_weight2, _, _ = np.histogram2d(
                x, y,  # type: ignore
                bins=bins,
                range=bin_range,
                weights=weights**2
            )
        else:
            bin_content_weight2, edges = np.histogram(
                x,
                bins=bins,
                range=bin_range,
                weights=weights**2
            )
            xlow, xhigh = edges[0], edges[-1]
            nbins = len(edges) - 1
            binned_dataset = dataset_is_binned(
                x, weights, xlow, xhigh, nbins,
            )
            if binned_dataset:
                bin_content_weight2 = weights
        errors = np.sqrt(bin_content_weight2)

    if norm_factor != 1:
        if isinstance(errors, tuple):
            errors = tuple(err / norm_factor for err in errors)
        else:
            errors /= norm_factor

    return errors

def histogram(
    x: np.ndarray,
    weights: Optional[np.ndarray] = None,
    bins: BinType = 10,
    bin_range: RangeType = None,
    underflow: bool = False,
    overflow: bool = False,
    divide_bin_width: bool = False,
    normalize: bool = False,
    clip_weight: bool = False,
    evaluate_error: bool = False,
    error_mode: Union[BinErrorMode, str] = "auto"
) -> Tuple[np.ndarray, np.ndarray, Optional[Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]]]:
    """
    Compute histogram of data.

    Parameters
    ----------
    x : np.ndarray
        Input data array
    weights : Optional[np.ndarray], default None
        Weights with the same shape as the input data. If not given,
        the input data is assumed to have unit weights.
    bins : BinType, default 10
        Bin specification
        If integer, defines the number of equal-width bins in the given range.
        If sequence, defines a monotonically increasing array of bin edges,
        including the rightmost edge. Default is 10.
    bin_range : RangeType, default None
        Data range for binning
    underflow : bool, default False
        Include underflow in first bin
    overflow : bool, default False
        Include overflow in last bin
    divide_bin_width : bool, default False
        Normalize by bin width; only used when normalize is True
    normalize : bool, default False
        Normalize total to unity
    clip_weight : bool, default False
        Ignore out-of-range data for normalization
    evaluate_error : bool, default False
        Calculate bin errors
    error_mode : Union[BinErrorMode, str], default "auto"
        Error calculation method;
        If "sumw2", symmetric errors from the Wald approximation are
        used (square root of sum of squares of weights). If "poisson",
        asymmetric errors from Poisson interval at one sigma are used.
        If "auto", it will use "sumw2" error if data has unit weights,
        else "poisson" error will be used.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, Optional[Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]]]
        Tuple of (bin_content, bin_edges, bin_errors)
    """
    try:
        x = get_clipped_data(
            x, 
            bin_range=bin_range,
            clip_lower=underflow,
            clip_upper=overflow
        )

        unweighted = weights is None
        if unweighted:
            weights = np.ones_like(x)
        else:
            # fix overflow bugs
            weights = np.asarray(weights, dtype=float)

        if normalize:
            if clip_weight and bin_range is not None:
                first_edge, last_edge = bin_range
                mask = (x >= first_edge) & (x <= last_edge)
                norm_factor = weights[mask].sum()
            else:
                norm_factor = weights.sum()
        else:
            norm_factor = 1

        # make sure bin_content has int type when no weights are given
        if unweighted:
            bin_content, bin_edges = np.histogram(x, bins=bins, range=bin_range)
        else:
            bin_content, bin_edges = np.histogram(
                x, bins=bins, range=bin_range, weights=weights
            )

        if divide_bin_width:
            bin_widths = bin_edge_to_bin_width(bin_edges)
            norm_factor *= bin_widths

        bin_errors = None
        if evaluate_error:
            bin_errors = _calculate_bin_errors(
                bin_content, x, None, weights, bins, bin_range,
                error_mode, unweighted, norm_factor
            )

        if np.any(norm_factor != 1):
            bin_content = bin_content.astype(float, copy=False)
            bin_content /= norm_factor

        return bin_content, bin_edges, bin_errors

    except Exception as e:
        raise HistogramError(f"Failed to compute histogram: {str(e)}") from e

def histogram2d(
    x: np.ndarray,
    y: np.ndarray,
    weights: Optional[np.ndarray] = None,
    bins: Union[BinType, Sequence[BinType]] = 10,
    bin_range: Union[RangeType, Sequence[RangeType]] = None,
    underflow: bool = False,
    overflow: bool = False,
    divide_bin_width: bool = False,
    normalize: bool = False,
    clip_weight: bool = False,
    evaluate_error: bool = False,
    error_mode: Union[BinErrorMode, str] = "auto"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Optional[Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]]]:
    """
    Compute 2D histogram of data.

    Parameters
    ----------
    x : np.ndarray
        X-coordinates of data points
    y : np.ndarray
        Y-coordinates of data points
    weights : Optional[np.ndarray], default None
        Weights with the same shape as input data. If not given, the
        input data is assumed to have unit weights.
    bins : BinType, default 10
        Bin specification for both axes
        - If int, the number of bins for the two dimensions (nx=ny=bins).
        - If array_like, the bin edges for the two dimensions (x_edges=y_edges=bins).
        - If [int, int], the number of bins in each dimension (nx, ny = bins).
        - If [array, array], the bin edges in each dimension (x_edges, y_edges = bins).
        - A combination [int, array] or [array, int], where int is the number of bins and array is the bin edges.
    bin_range : RangeType, default None
        The leftmost and rightmost edges of the bins along each dimension: [[xmin, xmax], [ymin, ymax]].
        Values outside of this range will be considered outliers and not tallied in the histogram.
    underflow : bool, default False
        Include underflow in first bins
    overflow : bool, default False
        Include overflow in last bins
    divide_bin_width : bool, default False
        Normalize by bin area; only used when normalize is True
    normalize : bool, default False
        Normalize the sum of weights to one
    clip_weight : bool, default False
        Ignore out-of-range data for normalization
    evaluate_error : bool, default False
        Calculate bin errors
    error_mode : Union[BinErrorMode, str], default "auto"
        Error calculation method;
        If "sumw2", symmetric errors from the Wald approximation are
        used (square root of sum of squares of weights). If "poisson",
        asymmetric errors from Poisson interval at one sigma are used.
        If "auto", it will use "sumw2" error if data has unit weights,
        else "poisson" error will be used.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray, Optional[Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]]]
        Tuple of (bin_content, x_edges, y_edges, bin_errors)
    """
    try:
        if len(x) != len(y):
            raise ValueError("x and y must have same length")

        bin_range = normalize_range(bin_range, dimension=2)
        x = get_clipped_data(x, bin_range[0], underflow, overflow)
        y = get_clipped_data(y, bin_range[1], underflow, overflow)

        unweighted = weights is None
        if weights is None:
            weights = np.ones_like(x)
        else:
            # fix overflow bugs
            weights = np.asarray(weights, dtype=float)

        if normalize:
            if clip_weight:
                mask = np.ones_like(x, dtype=bool)
                if bin_range[0] is not None:
                    first_edge, last_edge = bin_range[0]
                    mask &= (x >= first_edge) & (x <= last_edge)
                if bin_range[1] is not None:
                    first_edge, last_edge = bin_range[1]
                    mask &= (y >= first_edge) & (y <= last_edge)
                norm_factor = weights[mask].sum()
            else:
                norm_factor = weights.sum()
        else:
            norm_factor = 1

        if unweighted:
            bin_content, x_edges, y_edges = np.histogram2d(
                x, y, bins=bins, range=bin_range
            )
        else:
            bin_content, x_edges, y_edges = np.histogram2d(
                x, y, bins=bins, range=bin_range, weights=weights
            )

        if divide_bin_width:
            x_widths = np.diff(x_edges)[:, np.newaxis]
            y_widths = np.diff(y_edges)[np.newaxis, :]
            norm_factor *= (x_widths * y_widths)

        bin_errors = None
        if evaluate_error:
            bin_errors = _calculate_bin_errors(
                bin_content, x, y, weights, bins, bin_range,
                error_mode, unweighted, norm_factor, is_2d=True
            )

        if norm_factor != 1:
            bin_content = bin_content.astype(float, copy=False)
            bin_content /= norm_factor

        return bin_content, x_edges, y_edges, bin_errors

    except Exception as e:
        raise HistogramError(f"Failed to compute 2D histogram: {str(e)}") from e
        
def get_sumw2(weights: np.ndarray) -> float:
    """
    Calculate the sum of squared weights.

    Parameters
    ----------
    weights : np.ndarray
        The weights to be squared and summed

    Returns
    -------
    float
        Square root of the sum of squared weights

    Examples
    --------
    >>> weights = np.array([1, 2, 3])
    >>> get_sumw2(weights)
    3.7416573867739413
    """
    return np.sqrt(np.sum(weights ** 2))

def get_hist_mean(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate mean value of a histogram.

    Parameters
    ----------
    x : np.ndarray
        Bin centers
    y : np.ndarray
        Bin contents

    Returns
    -------
    float
        Mean value of histogram

    Examples
    --------
    >>> x = np.array([0.5, 1.5, 2.5])
    >>> y = np.array([1, 2, 1])
    >>> get_hist_mean(x, y)
    1.5
    """
    return np.sum(x * y) / np.sum(y)

def get_hist_std(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate standard deviation of a histogram.

    Parameters
    ----------
    x : np.ndarray
        Bin centers
    y : np.ndarray
        Bin contents

    Returns
    -------
    float
        Standard deviation of histogram

    Examples
    --------
    >>> x = np.array([0.5, 1.5, 2.5])
    >>> y = np.array([1, 2, 1])
    >>> get_hist_std(x, y)
    0.7071067811865476
    """
    mean = get_hist_mean(x, y)
    count = np.sum(y)
    if count == 0.0:
        return 0.0
    # for negative stddev (e.g. when having negative weights) - return std=0
    std2 = np.max([np.sum(y * (x - mean) ** 2) / count, 0.0])
    return np.sqrt(std2)

def get_hist_effective_entries(y: np.ndarray, yerr: np.ndarray) -> float:
    """
    Calculate effective number of entries in histogram.

    Parameters
    ----------
    y : np.ndarray
        Bin contents
    yerr : np.ndarray
        Bin uncertainties

    Returns
    -------
    float
        Number of effective entries

    Examples
    --------
    >>> y = np.array([1, 2, 1])
    >>> yerr = np.array([0.5, 0.5, 0.5])
    >>> get_hist_effective_entries(y, yerr)
    21.333333333333332
    """
    sumw2 = np.sum(yerr ** 2)
    if sumw2 != 0.0:
        return (np.sum(y) ** 2) / sumw2
    return 0.0

def get_hist_mean_error(
    x: np.ndarray,
    y: np.ndarray,
    yerr: np.ndarray
) -> float:
    """
    Calculate error on histogram mean.

    Parameters
    ----------
    x : np.ndarray
        Bin centers
    y : np.ndarray
        Bin contents
    yerr : np.ndarray
        Bin uncertainties

    Returns
    -------
    float
        Error on mean

    Examples
    --------
    >>> x = np.array([0.5, 1.5, 2.5])
    >>> y = np.array([1, 2, 1])
    >>> yerr = np.array([0.5, 0.5, 0.5])
    >>> get_hist_mean_error(x, y, yerr)
    0.15309310892394865
    """
    neff = get_hist_effective_entries(y, yerr)
    if neff > 0.0:
        std = get_hist_std(x, y)
        return std / np.sqrt(neff)
    return 0.0

def get_cumul_hist(
    y: np.ndarray,
    yerr: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate cumulative histogram and uncertainties.

    Parameters
    ----------
    y : np.ndarray
        Bin contents
    yerr : np.ndarray
        Bin uncertainties

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Cumulative contents and uncertainties

    Examples
    --------
    >>> y = np.array([1, 2, 1])
    >>> yerr = np.array([0.5, 0.5, 0.5])
    >>> get_cumul_hist(y, yerr)
    (array([1, 3, 4]), array([0.5, 0.70710678, 0.8660254]))
    """
    y_cum = np.cumsum(y)
    yerr_cum = np.sqrt(np.cumsum(yerr ** 2))
    return y_cum, yerr_cum

def get_bin_centers_from_range(
    xlow: Real,
    xhigh: Real,
    nbins: int,
    bin_precision: Optional[int] = None
) -> np.ndarray:
    """
    Calculate bin centers for given range and number of bins.

    Parameters
    ----------
    xlow : Real
        Lower bound of range
    xhigh : Real
        Upper bound of range
    nbins : int
        Number of bins
    bin_precision : Optional[int], default None
        Precision for rounding bin centers

    Returns
    -------
    np.ndarray
        Array of bin centers

    Examples
    --------
    >>> get_bin_centers_from_range(0, 10, 5)
    array([1., 3., 5., 7., 9.])
    """
    if nbins <= 0:
        raise ValueError("Number of bins must be positive")
    if xlow >= xhigh:
        raise ValueError("Upper bound must be greater than lower bound")

    bin_width = (xhigh - xlow) / nbins
    low_center = xlow + bin_width / 2
    high_center = xhigh - bin_width / 2
    centers = np.linspace(low_center, high_center, nbins)
    
    bin_precision = bin_precision or CONFIG.bin_precision
    centers = np.around(centers, bin_precision)
    return centers

def get_histogram_mask(
    x: np.ndarray,
    condition: HistoMaskType,
    y: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Create mask for histogram data based on condition.

    Parameters
    ----------
    x : np.ndarray
        Primary data array
    condition : HistoMaskType
        Condition for masking (array of bounds or callable)
    y : Optional[np.ndarray], default None
        Secondary data array for 2D conditions

    Returns
    -------
    np.ndarray
        Boolean mask array

    Raises
    ------
    ValueError
        If data arrays have incompatible shapes or condition is invalid
    TypeError
        If condition type is unsupported

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> mask = get_histogram_mask(x, (2, 4))
    >>> x[mask]
    array([3])
    """
    try:
        if y is not None and len(x) != len(y):
            raise ValueError("x and y arrays must have same length")

        mask = np.full(x.shape[:1], False)

        if callable(condition):
            return _apply_callable_mask(x, y, condition)
        
        return _apply_range_mask(x, y, condition)

    except Exception as e:
        if isinstance(e, (ValueError, TypeError)):
            raise
        raise TypeError(f"Invalid mask condition: {condition}") from e

def _apply_callable_mask(
    x: np.ndarray,
    y: Optional[np.ndarray],
    condition: Callable
) -> np.ndarray:
    """Apply callable condition to create mask."""
    if y is None:
        return np.asarray(condition(x))
    return np.asarray(condition(x, y))

def _apply_range_mask(
    x: np.ndarray,
    y: Optional[np.ndarray],
    condition: ArrayLike
) -> np.ndarray:
    """Apply range condition to create mask."""
    condition = np.asarray(condition)
    
    if len(condition) == 2:
        xmin, xmax = condition
        return (x > xmin) & (x < xmax)
        
    if len(condition) == 4 and y is not None:
        xmin, xmax, ymin, ymax = condition
        return (x > xmin) & (x < xmax) & (y > ymin) & (y < ymax)
        
    raise ValueError(
        "Range condition must be (xmin, xmax) or (xmin, xmax, ymin, ymax)"
    )

def select_binned_data(
    mask: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    xerr: Optional[ArrayLike] = None,
    yerr: Optional[ArrayLike] = None
) -> Tuple[np.ndarray, np.ndarray, Optional[ArrayLike], Optional[ArrayLike]]:
    """
    Select data points from binned data using mask.

    Parameters
    ----------
    mask : np.ndarray
        Boolean mask array
    x : np.ndarray
        Bin centers or x-coordinates
    y : np.ndarray
        Bin contents or y-values
    xerr : Optional[ArrayLike], default None
        X-axis uncertainties
    yerr : Optional[ArrayLike], default None
        Y-axis uncertainties

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, Optional[ArrayLike], Optional[ArrayLike]]
        Selected data points and uncertainties

    Examples
    --------
    >>> x = np.array([1, 2, 3])
    >>> y = np.array([10, 20, 30])
    >>> mask = np.array([True, False, True])
    >>> select_binned_data(mask, x, y)
    (array([1, 3]), array([10, 30]), None, None)
    """
    try:
        x_sel, y_sel = np.asarray(x)[mask], np.asarray(y)[mask]
        xerr_sel = _select_errors(xerr, mask)
        yerr_sel = _select_errors(yerr, mask)
        return x_sel, y_sel, xerr_sel, yerr_sel
    except Exception as e:
        raise HistogramError(f"Failed to select binned data: {str(e)}") from e

def _select_errors(
    err: Optional[ArrayLike],
    mask: np.ndarray
) -> Optional[Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]]:
    """Select error values based on mask."""
    if err is None:
        return None
        
    if isinstance(err, (list, tuple, np.ndarray)):
        if np.ndim(err) == 2 and np.shape(err)[0] == 2:
            return (_select_errors(err[0], mask),
                    _select_errors(err[1], mask))
        return np.asarray(err)[mask]
        
    return err

def dataset_is_binned(
    x: np.ndarray,
    y: np.ndarray,
    xlow: float,
    xhigh: float,
    nbins: int,
    ghost_threshold: Optional[float] = None,
    bin_precision: Optional[int] = None
) -> bool:
    """
    Check if dataset matches expected binning.

    Parameters
    ----------
    x : np.ndarray
        Data x-coordinates or bin centers
    y : np.ndarray
        Data y-values or bin contents
    xlow : float
        Lower bound of range
    xhigh : float
        Upper bound of range
    nbins : int
        Number of bins
    ghost_threshold : Optional[float], default None
        Threshold for identifying ghost bins
    bin_precision : Optional[int], default None
        Precision for bin center comparison

    Returns
    -------
    bool
        True if dataset matches expected binning

    Raises
    ------
    HistogramError
        If binning validation fails

    Examples
    --------
    >>> x = np.array([1., 3., 5.])
    >>> y = np.array([1, 1, 1])
    >>> dataset_is_binned(x, y, 0, 6, 3)
    True
    """
    try:

        # more data than number of bins
        if len(x) > nbins:
            return False
            
        bin_precision = bin_precision or CONFIG.bin_precision
        
        bin_centers = get_bin_centers_from_range(
            xlow, xhigh, nbins, bin_precision
        )
        x = np.around(x, bin_precision)
            
        # Check for matching bins
        if (len(x) == nbins) and np.allclose(
            bin_centers, x, rtol=CONFIG.rtol, atol=CONFIG.atol
        ):
            return True

        # Check for unit weights
        if np.allclose(
            y, 1.0, rtol=CONFIG.rtol, atol=CONFIG.atol
        ):
            return False

         # Check for subset relationship
        if array_issubset(bin_centers, x):
            return True

        """
        # Check for ghost bins
        ghost_threshold = ghost_threshold or CONFIG.ghost_threshold
        y_no_ghost = y[y > ghost_threshold]
        # First check if all events have unit weight (i.e. unbinned data)
        # Second check if all events have the same scaled weight (in case of lumi scaling)
        if (np.allclose(y_no_ghost, 1.0) or 
            np.allclose(y_no_ghost, y_no_ghost[0])):
            return False
        """

        return False

    except Exception as e:
        if isinstance(e, HistogramError):
            raise
        raise HistogramError(f"Failed to validate binning: {str(e)}") from e

def is_poisson_data(y: np.ndarray, ghost_threshold: Optional[float] = None) -> bool:
    """
    Determine whether the input histogram data is consistent with Poisson statistics.

    By default, this function returns True if all elements in `y` are integer-valued 
    (within a tolerance) and the array is not entirely zero. Optionally, if a 
    ghost_threshold is provided, then even if the data are not exactly integers, 
    they will be considered Poisson-like if all entries are less than or equal to 
    the ghost_threshold.

    Parameters
    ----------
    y : np.ndarray
        Array of histogram bin contents.
    ghost_threshold : Optional[float], default None
        A threshold value below which all bin counts are considered to be ghost values.
        If provided and all entries in `y` are less than or equal to this threshold,
        the data is treated as Poisson-like.

    Returns
    -------
    bool
        True if the data is considered to be Poisson-distributed, False otherwise.

    Examples
    --------
    >>> import numpy as np
    >>> # Example 1: Data with integer values is considered Poisson-like.
    >>> is_poisson_data(np.array([1, 2, 3]))
    True
    >>> # Example 2: Data with small float values below the ghost threshold is considered Poisson-like.
    >>> is_poisson_data(np.array([0.001, 0.002, 0.003]), ghost_threshold=0.01)
    True
    >>> # Example 3: Data with float values above the ghost threshold is not considered Poisson-like.
    >>> is_poisson_data(np.array([1.1, 2.2, 3.3]), ghost_threshold=0.01)
    False
    """
    if ghost_threshold is not None and np.all(y <= ghost_threshold):
        return True
    return all_integers(y) and not np.all(y == 0)


def deduce_error_mode(y: np.ndarray, ghost_threshold: Optional[float] = None) -> BinErrorMode:
    """
    Deduce the appropriate error mode for histogram data.

    This function inspects the data to determine whether to use Poisson-based errors or
    errors based on the sum of squared weights (SUMW2). Data is considered Poisson-like
    if it is integer-valued (within tolerance) or if all entries are below or equal to a provided
    ghost threshold. In these cases, the function returns BinErrorMode.POISSON; otherwise,
    it returns BinErrorMode.SUMW2.

    Parameters
    ----------
    y : np.ndarray
        Array of histogram bin contents.
    ghost_threshold : Optional[float], default None
        A threshold value below which all bin entries are considered ghost counts.
        If provided and all values in `y` are ≤ ghost_threshold, the data is treated as Poisson-like.

    Returns
    -------
    BinErrorMode
        BinErrorMode.POISSON if the data is considered Poisson-like;
        otherwise, BinErrorMode.SUMW2.

    Examples
    --------
    >>> import numpy as np
    >>> from your_module import deduce_error_mode, BinErrorMode
    >>> # Data with integer counts is Poisson-like:
    >>> deduce_error_mode(np.array([1, 2, 3]))
    BinErrorMode.POISSON
    >>> # Data with small values below the ghost threshold is treated as Poisson-like:
    >>> deduce_error_mode(np.array([0.001, 0.002, 0.003]), ghost_threshold=0.01)
    BinErrorMode.POISSON
    >>> # Data with values above the ghost threshold is not considered Poisson-like:
    >>> deduce_error_mode(np.array([1.1, 2.2, 3.3]), ghost_threshold=0.01)
    BinErrorMode.SUMW2
    """
    if is_poisson_data(y, ghost_threshold=ghost_threshold):
        return BinErrorMode.POISSON
    else:
        return BinErrorMode.SUMW2

def fill_missing_bins(
    x: np.ndarray,
    y: np.ndarray,
    xlow: float,
    xhigh: float,
    nbins: int,
    value: float = 0,
    bin_precision: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fill missing bins in histogram data.

    Parameters
    ----------
    x : np.ndarray
        Bin centers or x-coordinates
    y : np.ndarray
        Bin contents or y-values
    xlow : float
        Lower bound of range
    xhigh : float
        Upper bound of range
    nbins : int
        Number of bins
    value : float, default 0
        Value to fill in missing bins
    bin_precision : Optional[int], default None
        Precision for bin center comparison

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Complete arrays with filled missing bins

    Examples
    --------
    >>> x = np.array([1., 3.])
    >>> y = np.array([10, 30])
    >>> fill_missing_bins(x, y, 0, 4, 3)
    (array([1., 2., 3.]), array([10.,  0., 30.]))
    """
    try:
        bin_precision = bin_precision or CONFIG.bin_precision
        bin_centers = get_bin_centers_from_range(
            xlow, xhigh, nbins, bin_precision
        )
        x_rounded = np.around(x, bin_precision)
        
        missing_bins = np.setdiff1d(bin_centers, x_rounded)
        missing_values = np.full_like(missing_bins, value)
        
        x_filled = np.concatenate([x, missing_bins])
        y_filled = np.concatenate([y, missing_values])
        
        sort_idx = np.argsort(x_filled)
        return x_filled[sort_idx], y_filled[sort_idx]
        
    except Exception as e:
        raise HistogramError(
            f"Failed to fill missing bins: {str(e)}"
        ) from e


def remove_ghost(y: np.ndarray, ghost_threshold: Optional[float] = None) -> np.ndarray:
    """
    Remove ghost bins from histogram data.

    Ghost bins are defined as bins whose content is less than or equal to a specified threshold.
    This function returns a new array where such bins are set to zero.

    Parameters
    ----------
    y : np.ndarray
        Array of histogram bin contents.
    ghost_threshold : Optional[float], default None
        Threshold value below which a bin is considered a ghost bin.
        If None, the value from CONFIG.ghost_threshold is used.

    Returns
    -------
    np.ndarray
        A new array with ghost bins removed (set to 0).

    Examples
    --------
    >>> import numpy as np
    >>> from your_module import CONFIG  # Replace with your actual module name
    >>> y = np.array([1e-9, 0.5, 1e-10, 2.0])
    >>> # Assuming CONFIG.ghost_threshold is 1e-8, the first and third bins are ghosts.
    >>> remove_ghost(y)
    array([0. , 0.5, 0. , 2. ])
    """
    ghost_threshold = ghost_threshold if ghost_threshold is not None else CONFIG.ghost_threshold
    return np.where(y <= ghost_threshold, 0, y)


def apply_ghost(y: np.ndarray, ghost_weight: Optional[float] = None) -> np.ndarray:
    """
    Apply ghost weights to histogram data.

    This function replaces zero-valued bins in the input array with a small ghost weight.
    This is useful for avoiding issues when subsequent operations (e.g. logarithms or ratios)
    require non-zero bin values.

    Parameters
    ----------
    y : np.ndarray
        Array of histogram bin contents.
    ghost_weight : Optional[float], default None
        The value to assign to bins with zero content.
        If None, the value from CONFIG.ghost_weight is used.

    Returns
    -------
    np.ndarray
        A new array with zero entries replaced by ghost_weight.

    Examples
    --------
    >>> import numpy as np
    >>> from your_module import CONFIG  # Replace with your actual module name
    >>> y = np.array([0, 0.5, 0, 2.0])
    >>> # Assuming CONFIG.ghost_weight is 1e-9, zeros will be replaced by 1e-9.
    >>> apply_ghost(y)
    array([1.e-09, 0.5, 1.e-09, 2.0])
    """
    ghost_weight = ghost_weight if ghost_weight is not None else CONFIG.ghost_weight
    return np.where(y == 0, ghost_weight, y)

def has_ghost(y: np.ndarray, ghost_threshold: Optional[float] = None) -> bool:
    """
    Check whether histogram data contains any ghost bins.

    A ghost bin is defined as a bin with a positive content that is less than or equal to a
    specified ghost threshold. This function returns True if any bin satisfies this condition,
    indicating the presence of ghost bins.

    Parameters
    ----------
    y : np.ndarray
        Array of histogram bin contents.
    ghost_threshold : Optional[float], default None
        The threshold below which a positive bin content is considered a ghost.
        If None, the value from CONFIG.ghost_threshold is used.

    Returns
    -------
    bool
        True if there is at least one bin with 0 < content <= ghost_threshold, False otherwise.

    Examples
    --------
    >>> import numpy as np
    >>> from your_module import CONFIG  # Replace with your actual module name
    >>> # Example: y contains a ghost bin if its value is positive but very small.
    >>> y = np.array([0, 1e-9, 0.5, 0, 2.0])
    >>> # Assuming CONFIG.ghost_threshold is 1e-8, the second bin is a ghost.
    >>> has_ghost(y)
    True
    >>> y = np.array([0, 0, 0.5, 0, 2.0])
    >>> has_ghost(y)
    False
    """
    ghost_threshold = ghost_threshold if ghost_threshold is not None else CONFIG.ghost_threshold
    return np.any((y > 0) & (y <= ghost_threshold))

def rebin_dataset(
    x: np.ndarray,
    y: np.ndarray,
    nbins: int,
    detect_ghost: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Rebin histogram data to new bin count.

    Parameters
    ----------
    x : np.ndarray
        Current bin centers
    y : np.ndarray
        Current bin contents
    nbins : int
        New number of bins

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Rebinned data arrays

    Raises
    ------
    HistogramError
        If rebinning fails
    """
    try:
        bin_edges = bin_center_to_bin_edge(x)
        from quickstats.interface.root import TH1
        hist = TH1.from_numpy_histogram(y, bin_edges=bin_edges)
        hist.rebin(nbins)
        return hist.bin_center, hist.bin_content
        
    except Exception as e:
        raise HistogramError(f"Failed to rebin dataset: {str(e)}") from e