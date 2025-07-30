from __future__ import annotations

from typing import (
    Optional, Union, Tuple, Any, Callable, Sequence,
    cast, TypeVar, Dict
)
from numbers import Real

import numpy as np

from quickstats import stdout
from quickstats.core.typing import ArrayLike, NOTSET
from quickstats.maths.numerics import all_integers, safe_div
from quickstats.maths.histograms import (
    BinErrorMode,
    HistComparisonMode,
    poisson_interval,
    deduce_error_mode,
    is_poisson_data,
    histogram,
    get_histogram_mask,
    remove_ghost,
    apply_ghost,
    has_ghost
)
from .binning import Binning
from .ranges import MultiRange, Range

# Type aliases for better type safety
H = TypeVar('H', bound='Histogram1D')
BinErrors = Optional[Tuple[np.ndarray, np.ndarray]]
ComparisonMode = Union[HistComparisonMode, str, Callable[[H, H], H]]

class Histogram1D:
    """
    A class representing a one-dimensional histogram with bin contents, edges, and errors.

    Attributes
    ----------
    bin_content : np.ndarray
        The bin content of the histogram.
    bin_errors : Optional[Tuple[np.ndarray, np.ndarray]]
        The bin errors (lower, upper) if available.
    bin_edges : np.ndarray
        The bin edges of the histogram.
    bin_centers : np.ndarray
        The bin centers of the histogram.
    bin_widths : np.ndarray
        The widths of the bins.
    nbins : int 
        The number of bins.
    error_mode : BinErrorMode
        The current error mode.
    ghost_weight : Optional[float]
        The ghost weight (if specified, must be positive and less than 1) enabling ghost-aware processing.        
    """

    def __init__(
        self,
        bin_content: np.ndarray,
        bin_edges: np.ndarray,
        bin_errors: Union[NOTSET, ArrayLike, None] = NOTSET,
        error_mode: Union[BinErrorMode, str] = "auto",
        ghost_weight: Optional[float] = None,
    ) -> None:
        """
        Initialize a Histogram1D instance.

        Parameters
        ----------
        bin_content : np.ndarray
            The bin contents.
        bin_edges : np.ndarray
            The bin edges.
        bin_errors : Optional[ArrayLike], default NOTSET
            The bin errors in a supported format.
        error_mode : Union[BinErrorMode, str], default "auto"
            The error calculation mode.
        ghost_weight : Optional[float], default None
            A positive ghost weight less than 1. If provided, ghost-aware processing is activated.
        """
        if ghost_weight is not None:
            if ghost_weight <= 0 or ghost_weight >= 1:
                raise ValueError("ghost_weight must be positive and less than 1.")
        self._ghost_weight = ghost_weight
        self.set_data(
            bin_content=bin_content,
            bin_edges=bin_edges,
            bin_errors=bin_errors,
            error_mode=error_mode,
            ghost_weight=ghost_weight,
        )

    def __add__(self, other: Union[Histogram1D, Real]) -> Histogram1D:
        """Return a new histogram that is the sum of this histogram and another histogram or scalar."""
        return self._operate("add", other)

    def __sub__(self, other: Union[Histogram1D, Real]) -> Histogram1D:
        """Return a new histogram that is the difference of this histogram and another histogram or scalar."""
        return self._operate("sub", other)

    def __mul__(self, other: Union[Real, ArrayLike]) -> Histogram1D:
        """Return a new histogram scaled by a scalar or an array."""
        return self._operate("scale", other)

    def __rmul__(self, other: Union[Real, ArrayLike]) -> Histogram1D:
        """Support right multiplication by a scalar or array."""
        return self._operate("scale", other)

    def __truediv__(self, other: Union[Histogram1D, Union[Real, ArrayLike]]) -> Histogram1D:
        """Return a new histogram that is the division of this histogram by another histogram, scalar, or array."""
        instance = self._operate("div", other)
        # Ensure that bin content is treated as weighted after division.
        instance._bin_content = instance._bin_content.astype(float)
        return instance

    def __rtruediv__(self, other: Union[Histogram1D, Union[Real, ArrayLike]]) -> Histogram1D:
        """Return a new histogram that is the division of this histogram by another histogram, scalar, or array."""
        instance = self._operate("div", other, reverse=True)
        # Ensure that bin content is treated as weighted after division.
        instance._bin_content = instance._bin_content.astype(float)
        return instance

    def __iadd__(self, other: Union[Histogram1D, Real]) -> Histogram1D:
        """Perform in-place addition with another histogram or scalar."""
        return self._ioperate("add", other)

    def __isub__(self, other: Union[Histogram1D, Real]) -> Histogram1D:
        """Perform in-place subtraction with another histogram or scalar."""
        return self._ioperate("sub", other)

    def __itruediv__(self, other: Union[Histogram1D, Real, ArrayLike]) -> Histogram1D:
        """Perform in-place division by another histogram, scalar, or array."""
        return self._ioperate("div", other)

    def __imul__(self, other: Union[Real, ArrayLike]) -> Histogram1D:
        """
        Perform in-place multiplication by a scalar or array.

        Parameters
        ----------
        other : Union[Real, ArrayLike]
            Scalar or array to multiply the histogram with.

        Returns
        -------
        Histogram1D
            Self after multiplication.
        """
        return self._ioperate("scale", other)

    def _operate(
        self,
        method: str,
        other: Any,
        **kwargs
    ) -> Histogram1D:
        """
        Perform an arithmetic operation and return a new histogram.

        Parameters
        ----------
        method : str
            The operation to perform ('add', 'sub', 'div', 'scale').
        other : Any
            The other operand (histogram, scalar, or array).

        Returns
        -------
        Histogram1D
            A new histogram resulting from the operation.

        Raises
        ------
        ValueError
            If the operation is invalid or the operands are incompatible.
        """
        operation = getattr(self, f"_{method}", None)
        if operation is None:
            raise ValueError(f'Invalid operation: "{method}"')
            
        bin_content, bin_errors = operation(other, **kwargs)
        bin_content_raw, bin_errors_raw = self._operate_masked(method, other, **kwargs)
        
        if isinstance(other, Histogram1D):
            error_mode = self._resolve_error_mode(bin_content, other._error_mode)
        else:
            error_mode = self._error_mode
            
        mask = self._combine_mask(other)
        self._apply_mask(mask, bin_content, bin_errors)
        
        instance = Histogram1D(
            bin_content=bin_content,
            bin_edges=self._binning._bin_edges,
            bin_errors=bin_errors,
            error_mode=error_mode,
        )

        instance._bin_content_raw = bin_content_raw
        instance._bin_errors_raw = bin_errors_raw
        instance._mask = mask
        return instance

    def _operate_masked(
        self,
        method: str,
        other: Any,
        **kwargs
    ) -> Tuple[Optional[np.ndarray], BinErrors]:
        """
        Handle arithmetic operations for histograms that have an active mask.

        Parameters
        ----------
        method : str
            The operation to perform.
        other : Any
            The other operand.

        Returns
        -------
        Tuple[Optional[np.ndarray], BinErrors]
            Raw bin content and errors if a mask was applied; otherwise, (None, None).
        """
        self_masked = self.is_masked()
        other_masked = isinstance(other, Histogram1D) and other.is_masked()
        
        if not (self_masked or other_masked):
            return None, None
            
        self_copy = self.copy()
        other_copy = other.copy() if isinstance(other, Histogram1D) else other
        
        if self_masked:
            self_copy.unmask()
        if other_masked:
            other_copy.unmask()
            
        operation = getattr(self_copy, f"_{method}")
        return operation(other_copy, **kwargs)
        
    def _ioperate(self, method: str, other: Any) -> Histogram1D:
        """
        Perform an in-place arithmetic operation on the histogram.

        Parameters
        ----------
        method : str
            The operation to perform ('add', 'sub', 'div', 'scale').
        other : Any
            The other operand (histogram, scalar, or array).

        Returns
        -------
        Histogram1D
            Self after applying the operation.

        Raises
        ------
        ValueError
            If the operation is invalid.
        """
        if not hasattr(self, f"_{method}"):
            raise ValueError(f'Invalid operation: "{method}"')
            
        operation = getattr(self, f"_{method}")
        bin_content, bin_errors = operation(other)
        bin_content_raw, bin_errors_raw = self._operate_masked(method, other)
        
        if isinstance(other, Histogram1D):
            self._error_mode = self._resolve_error_mode(
                bin_content, other._error_mode
            )
            
        mask = self._combine_mask(other)
        self._apply_mask(mask, bin_content, bin_errors)
        
        self._bin_content = bin_content
        self._bin_errors = bin_errors
        self._bin_content_raw = bin_content_raw
        self._bin_errors_raw = bin_errors_raw
        self._mask = mask
        
        return self

    def _combine_mask(self, other: Any) -> np.ndarray:
        """
        Combine the mask from this histogram and another, if applicable.

        Parameters
        ----------
        other : Any
            The other operand, which may be a Histogram1D instance.

        Returns
        -------
        np.ndarray
            A combined mask array, or None if no masks exist.
        """
        mask = self._mask
        if isinstance(other, Histogram1D) and other.is_masked():
            if mask is None:
                mask = other._mask.copy()
            else:
                mask = mask | other._mask
        return mask.copy() if mask is not None else None

    def _apply_mask(
        self,
        mask: np.ndarray,
        bin_content: np.ndarray,
        bin_errors: BinErrors
    ) -> None:
        """
        Apply a mask to the bin content and errors.

        Parameters
        ----------
        mask : np.ndarray
            The boolean mask array.
        bin_content : np.ndarray
            The bin content array to modify.
        bin_errors : BinErrors
            The bin errors to modify.
        """
        if mask is None:
            return
            
        bin_content[mask] = 0
        if bin_errors is not None:
            bin_errors[0][mask] = 0.0
            bin_errors[1][mask] = 0.0

    def _validate_other(self, other: Histogram1D) -> None:
        """
        Validate that another histogram is compatible for operations.

        Parameters
        ----------
        other : Histogram1D
            The histogram to validate.

        Raises
        ------
        ValueError
            If the other object is not a Histogram1D or if the binnings are incompatible.
        """
        if not isinstance(other, Histogram1D):
            raise ValueError("Operation only allowed between Histogram1D objects")
        if self.binning != other.binning:
            raise ValueError("Operations not allowed between histograms with different binning")

    def _resolve_error_mode(
        self,
        bin_content: np.ndarray,
        other_mode: BinErrorMode
    ) -> BinErrorMode:
        """
        Resolve the error mode for an operation based on bin content and another histogram's mode.

        Parameters
        ----------
        bin_content : np.ndarray
            The resulting bin content from an operation.
        other_mode : BinErrorMode
            The error mode of the other histogram.

        Returns
        -------
        BinErrorMode
            The resolved error mode, preferring POISSON if applicable.
        """
        use_poisson = (
            bin_content.dtype == np.int64 or
            self._error_mode == BinErrorMode.POISSON or
            other_mode == BinErrorMode.POISSON
        )
        return BinErrorMode.POISSON if use_poisson else BinErrorMode.SUMW2

    def _scale(
        self,
        val: Union[Real, ArrayLike]
    ) -> Tuple[np.ndarray, BinErrors]:
        """
        Scale the histogram's bin content by a scalar or array.

        Parameters
        ----------
        val : Union[Real, ArrayLike]
            The scaling factor.

        Returns
        -------
        Tuple[np.ndarray, BinErrors]
            The scaled bin content and the corresponding scaled errors.

        Raises
        ------
        ValueError
            If the scaling value has an invalid shape.
        """
        val = np.asarray(val)
        is_weighted = self.is_weighted()

        # Handle integer scaling
        if not is_weighted and all_integers(val):
            val = val.astype(np.int64)
            if not np.all(val >= 0):
                stdout.warning(
                    "Scaling unweighted histogram by negative values will make it weighted "
                    "and force sumw2 errors"
                )
                val = val.astype(float)
        else:
            val = val.astype(float)

        # Validate scaling array shape
        if val.ndim > 1:
            raise ValueError(f"Cannot scale with {val.ndim}-dimensional value")
        if val.ndim == 1 and val.size != self.nbins:
            raise ValueError(f"Scaling array size ({val.size}) doesn't match bins ({self.nbins})")

        y = self._bin_content_clean * val

        y_final = apply_ghost(y, ghost_weight=self._ghost_weight) if self.use_ghost else y
            
        if self._bin_errors is None:
            return y_final, None

        # Scale errors appropriately
        if y.dtype == np.int64:
            yerr = poisson_interval(y)
            if self.is_masked():
                yerr[0][self._mask] = 0.0
                yerr[1][self._mask] = 0.0
        else:
            errlo, errhi = self._bin_errors
            yerr = (val * errlo, val * errhi)

        return y_final, yerr

    def _add(
        self,
        other: Union[Histogram1D, Real],
        neg: bool = False
    ) -> Tuple[np.ndarray, BinErrors]:
        """
        Add or subtract another histogram or scalar from this histogram.

        Parameters
        ----------
        other : Union[Histogram1D, Real]
            The histogram or scalar to add/subtract.
        neg : bool, default False
            If True, perform subtraction instead of addition.

        Returns
        -------
        Tuple[np.ndarray, BinErrors]
            The resulting bin content and bin errors after the operation.
        """
        y_self = self._bin_content_clean
        if isinstance(other, Real):
            y_other = np.full(y_self.shape, other, dtype=y_self.dtype)
            yerr_other = (np.zeros_like(y_self), np.zeros_like(y_self))
            other = type(self)(
                bin_content=y_other,
                bin_edges=self._binning._bin_edges,
                bin_errors=yerr_other,
                ghost_weight=None
            )

        self._validate_other(other)

        y_other = other._bin_content_clean
        y = y_self - y_other if neg else y_self + y_other

        y_final = apply_ghost(y, ghost_weight=self._ghost_weight) if self.use_ghost else y

        if self._bin_errors is None and other._bin_errors is None:
            return y_final, None

        if self._bin_errors is not None and other._bin_errors is not None:
            use_poisson = False
            if y.dtype == np.int64:
                if np.all(y >= 0):
                    use_poisson = True
                else:
                    stdout.warning("Negative bin content - forcing sumw2 errors")
            if use_poisson:
                yerr = poisson_interval(y)
                if self.is_masked():
                    yerr[0][self._mask] = 0.0
                    yerr[1][self._mask] = 0.0
            else:
                errlo = np.sqrt(self._bin_errors[0] ** 2 + other._bin_errors[0] ** 2)
                errhi = np.sqrt(self._bin_errors[1] ** 2 + other._bin_errors[1] ** 2)
                yerr = (errlo, errhi)
        else:
            yerr = self._bin_errors if self._bin_errors is not None else other._bin_errors

        return y_final, yerr

    def _sub(
        self,
        other: Union[Histogram1D, Real]
    ) -> Tuple[np.ndarray, BinErrors]:
        """
        Subtract another histogram or scalar from this histogram.

        Parameters
        ----------
        other : Union[Histogram1D, Real]
            The histogram or scalar to subtract.

        Returns
        -------
        Tuple[np.ndarray, BinErrors]
            The resulting bin content and bin errors after subtraction.
        """
        return self._add(other, neg=True)
        
    def _div(
        self,
        other: Union[Histogram1D, Real, ArrayLike],
        reverse: bool = False
    ) -> Tuple[np.ndarray, BinErrors]:
        """
        Divide this histogram by another histogram, scalar, or array.

        Parameters
        ----------
        other : Union[Histogram1D, Real, ArrayLike]
            The divisor.

        Returns
        -------
        Tuple[np.ndarray, BinErrors]
            The resulting bin content and bin errors after division.

        Raises
        ------
        ValueError
            If division by zero occurs or if the histograms have incompatible binning.
        """
        if not isinstance(other, Histogram1D):
            if np.any(other == 0):
                raise ValueError("Division by zero")
            if reverse:
                return self._scale(other / self._bin_content_clean ** 2)
            return self._scale(1.0 / other)

        self._validate_other(other)
        y_self = self._bin_content_clean
        y_other = other._bin_content_clean
        if reverse:
            y_top = y_other
            y_bot = y_self
        else:
            y_top = y_self
            y_bot = y_other
        y = safe_div(y_top, y_bot, True)
        y = y.astype(float)

        y_final = apply_ghost(y, ghost_weight=self._ghost_weight) if self.use_ghost else y
        
        if self._bin_errors is None and other._bin_errors is None:
            return y_final, None
    
        err_self = self._bin_errors or (np.zeros(self.nbins), np.zeros(self.nbins))
        err_other = other._bin_errors or (np.zeros(other.nbins), np.zeros(other.nbins))
        if reverse:
            err_top = err_other
            err_bot = err_self
        else:
            err_top = err_self
            err_bot = err_other
        
        errlo, errhi = self._calculate_division_errors(y_top, y_bot, err_top, err_bot)
        
        if self.is_masked():
            errlo[self._mask] = 0.0
            errhi[self._mask] = 0.0
            
        return y_final, (errlo, errhi)

    @staticmethod
    def _calculate_division_errors(
        num: np.ndarray,
        den: np.ndarray,
        num_errs: Tuple[np.ndarray, np.ndarray],
        den_errs: Tuple[np.ndarray, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate propagated errors for histogram division using the ratio formula.

        Uses the error propagation formula:
            σ(a/b)² = (a/b)² * ( (σ_a/a)² + (σ_b/b)² )

        Parameters
        ----------
        num : np.ndarray
            Numerator bin values.
        den : np.ndarray
            Denominator bin values.
        num_errs : Tuple[np.ndarray, np.ndarray]
            Errors for the numerator (low, high).
        den_errs : Tuple[np.ndarray, np.ndarray]
            Errors for the denominator (low, high).

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            The propagated lower and upper errors.
        """
        den_sq = den * den
        errlo = safe_div(
            np.sqrt(num_errs[0]**2 * den_sq + den_errs[0]**2 * num * num),
            den_sq * den_sq,
            False
        )
        errhi = safe_div(
            np.sqrt(num_errs[1]**2 * den_sq + den_errs[1]**2 * num * num),
            den_sq * den_sq,
            False
        )
        return errlo, errhi

    @staticmethod
    def _regularize_errors(
        bin_content: np.ndarray,
        bin_errors: Optional[ArrayLike] = None
    ) -> BinErrors:
        """
        Convert various error formats into a standardized (lower, upper) tuple format.

        Parameters
        ----------
        bin_content : np.ndarray
            The histogram bin content.
        bin_errors : Optional[ArrayLike], default None
            The bin errors in one of several possible formats:
              - None: No errors.
              - Scalar: A single error value applied to all bins.
              - 1D array: Symmetric errors (length must match number of bins).
              - 2D array or Tuple[array, array]: Asymmetric errors (each array's length must match number of bins).

        Returns
        -------
        BinErrors
            A tuple (lower_errors, upper_errors) or None if no errors are provided.

        Raises
        ------
        ValueError
            If the error array's shape or size is invalid.
        """
        if bin_errors is None:
            return None

        size = bin_content.size
        
        if np.isscalar(bin_errors):
            err = np.full(size, bin_errors, dtype=float)
            return (err, err)
            
        bin_errors = np.asarray(bin_errors)
        
        if bin_errors.ndim == 1:
            if bin_errors.size != size:
                raise ValueError("Error array size must match bin content size")
            return (bin_errors, bin_errors)
            
        if bin_errors.ndim == 2:
            if bin_errors.shape != (2, size):
                raise ValueError("2D error array must have shape (2, nbins)")
            return (bin_errors[0], bin_errors[1])
            
        raise ValueError(f"Error array has invalid dimension: {bin_errors.ndim}")

    def set_data(
        self,
        bin_content: np.ndarray,
        bin_edges: np.ndarray,
        bin_errors: Optional[ArrayLike] = NOTSET,
        error_mode: Union[BinErrorMode, str] = "auto",
        ghost_weight: Optional[float] = None,
    ) -> None:
        """
        Set the histogram data.
    
        In addition to validating the input data, if ghost processing is active, the
        bin content is processed using apply_ghost immediately.
    
        Parameters
        ----------
        bin_content : np.ndarray
            The bin contents.
        bin_edges : np.ndarray
            The bin edges.
        bin_errors : Optional[ArrayLike], default NOTSET
            The bin errors.
        error_mode : Union[BinErrorMode, str], default "auto"
            The error calculation mode.
        ghost_weight : Optional[float], default None
            The ghost weight. If provided, must be positive and less than 1.
    
        Raises
        ------
        ValueError
            If bin content/edges are invalid or ghost_weight is provided but invalid.
        """

        if ghost_weight is not None:
            if ghost_weight <= 0 or ghost_weight >= 1:
                raise ValueError("ghost_weight must be positive and less than 1.")
        self._ghost_weight = ghost_weight if ghost_weight is not None else self._ghost_weight
    
        bin_content = np.asarray(bin_content)
        if bin_content.ndim != 1:
            raise ValueError("Bin content must be 1-dimensional")
        bin_edges = np.asarray(bin_edges)
        if bin_edges.ndim != 1:
            raise ValueError("Bin edges must be 1-dimensional")
        if bin_content.size != (bin_edges.size - 1):
            raise ValueError("Mismatch between bin content and bin edges.")
    
        if self.use_ghost:
            bin_content = remove_ghost(bin_content, ghost_threshold=self._ghost_weight)
    
        binning = Binning(bins=bin_edges)
        error_mode = BinErrorMode.parse(error_mode)

        if error_mode == BinErrorMode.AUTO:
            error_mode = deduce_error_mode(bin_content)
        # If Poisson error mode and data is Poisson-like, cast to int.
        if error_mode == BinErrorMode.POISSON and is_poisson_data(bin_content):
            bin_content = bin_content.astype(np.int64)
        else:
            bin_content = bin_content.astype(float)
        if bin_errors is NOTSET:
            if error_mode == BinErrorMode.POISSON:
                bin_errors = poisson_interval(bin_content)
            else:
                bin_errors = None

        bin_errors = self._regularize_errors(bin_content, bin_errors)
        # should apply the ghost here after error evaluation
        if self.use_ghost:
            bin_content = apply_ghost(bin_content, ghost_weight=self._ghost_weight)
        
        self._bin_content = bin_content
        self._binning = binning
        self._bin_errors = bin_errors
        self._error_mode = error_mode
        self._bin_content_raw = None
        self._bin_errors_raw = None
        self._mask = None

    @classmethod
    def create(
        cls,
        x: np.ndarray,
        weights: Optional[np.ndarray] = None,
        bins: Union[int, ArrayLike] = 10,
        bin_range: Optional[ArrayLike] = None,
        underflow: bool = False,
        overflow: bool = False,
        divide_bin_width: bool = False,
        normalize: bool = False,
        clip_weight: bool = False,
        evaluate_error: bool = True,
        error_mode: Union[BinErrorMode, str] = "auto",
        ghost_weight: Optional[float] = None,
    ) -> Histogram1D:
        """
        Create a Histogram1D instance from raw data.

        Parameters
        ----------
        x : np.ndarray
            The input data.
        weights : Optional[np.ndarray], default None
            Optional weights.
        bins : Union[int, ArrayLike], default 10
            Number of bins or bin edges.
        bin_range : Optional[ArrayLike], default None
            The (min, max) range.
        underflow : bool, default False
            Include underflow.
        overflow : bool, default False
            Include overflow.
        divide_bin_width : bool, default False
            Normalize by bin width.
        normalize : bool, default False
            Normalize histogram to unit area.
        clip_weight : bool, default False
            Ignore out-of-range weights.
        evaluate_error : bool, default True
            Calculate bin errors.
        error_mode : Union[BinErrorMode, str], default "auto"
            The error mode.
        ghost_weight : Optional[float], default None
            The ghost weight (must be positive and less than 1). If provided, ghost-aware
            processing is enabled.

        Returns
        -------
        Histogram1D
            A new histogram instance.
        """
        bin_content, bin_edges, bin_errors = histogram(
            x=x,
            weights=weights,
            bins=bins,
            bin_range=bin_range,
            underflow=underflow,
            overflow=overflow,
            divide_bin_width=divide_bin_width,
            normalize=normalize,
            clip_weight=clip_weight,
            evaluate_error=evaluate_error,
            error_mode=error_mode,
        )
        return cls(
            bin_content=bin_content,
            bin_edges=bin_edges,
            bin_errors=bin_errors,
            error_mode=error_mode,
            ghost_weight=ghost_weight,
        )

    @property
    def bin_content(self) -> np.ndarray:
        """Return a copy of the bin content array."""
        return self._bin_content.copy()

    @property
    def bin_content_clean(self) -> np.ndarray:
        """Return a copy of the bin content array."""
        if not self.use_ghost:
            return self.bin_content
        return self._bin_content_clean

    @property
    def binning(self) -> Binning:
        """Return the Binning object associated with this histogram."""
        return self._binning

    @property
    def bin_edges(self) -> np.ndarray:
        """Return a copy of the bin edges array."""
        return self._binning.bin_edges

    @property
    def bin_centers(self) -> np.ndarray:
        """Return a copy of the bin centers array."""
        return self._binning.bin_centers

    @property
    def bin_widths(self) -> np.ndarray:
        """Return a copy of the bin widths array."""
        return self._binning.bin_widths

    @property
    def nbins(self) -> int:
        """Return the number of bins."""
        return self._binning.nbins

    @property
    def bin_range(self) -> Tuple[float, float]:
        """Return the (min, max) range of the bins."""
        return self._binning.bin_range

    @property
    def uniform_binning(self) -> bool:
        """Return True if the histogram has uniform binning."""
        return self._binning.is_uniform()

    @property
    def bin_errors(self) -> BinErrors:
        """
        Return a copy of the bin errors.

        Returns
        -------
        BinErrors
            A tuple (lower_errors, upper_errors) or None if errors are not set.
        """
        if self._bin_errors is None:
            return None
        return (self._bin_errors[0].copy(), self._bin_errors[1].copy())

    @property
    def bin_errlo(self) -> Optional[np.ndarray]:
        """Return a copy of the lower bin errors array."""
        if self._bin_errors is None:
            return None
        return self._bin_errors[0].copy()

    @property
    def bin_errhi(self) -> Optional[np.ndarray]:
        """Return a copy of the upper bin errors array."""
        if self._bin_errors is None:
            return None
        return self._bin_errors[1].copy()

    @property
    def rel_bin_errors(self) -> BinErrors:
        """Return the relative bin errors (content minus lower error, content plus upper error)."""
        if self._bin_errors is None:
            return None
        bin_content = self._bin_content_clean
        errlo = bin_content - self._bin_errors[0]
        errhi = bin_content + self._bin_errors[1]
        return (errlo, errhi)

    @property
    def rel_bin_errlo(self) -> Optional[np.ndarray]:
        """Return the relative lower bin errors (content minus lower error)."""
        if self._bin_errors is None:
            return None
        return self._bin_content_clean - self._bin_errors[0]

    @property
    def rel_bin_errhi(self) -> Optional[np.ndarray]:
        """Return the relative upper bin errors (content plus upper error)."""
        if self._bin_errors is None:
            return None
        return self._bin_content_clean + self._bin_errors[1]

    @property
    def error_mode(self) -> BinErrorMode:
        """Return the current error mode of the histogram."""
        return self._error_mode

    @property
    def bin_mask(self) -> np.ndarray:
        """
        Return a copy of the bin mask array, if a mask is applied.

        Returns
        -------
        np.ndarray
            The mask array or None if no mask exists.
        """
        if self._mask is None:
            return None
        return self._mask.copy()

    @property
    def ghost_weight(self) -> Optional[float]:
        """Return the ghost weight if specified, else None."""
        return self._ghost_weight

    @property
    def use_ghost(self) -> bool:
        """
        Return True if ghost processing is enabled (i.e. ghost_weight is specified), False otherwise.
        """
        return self._ghost_weight is not None

    @property
    def _bin_content_clean(self) -> np.ndarray:
        """
        Return the bin content with ghost values removed and, if appropriate, cast to int.

        Returns
        -------
        np.ndarray
            The cleaned bin content.
        """
        if not self.use_ghost:
            return self._bin_content
        data = remove_ghost(self._bin_content, ghost_threshold=self._ghost_weight)
        if all_integers(data):
            return data.astype(np.int64)
        return data

    def has_errors(self) -> bool:
        """Return True if the histogram has bin errors defined, False otherwise."""
        return self._bin_errors is not None

    def is_weighted(self) -> bool:
        """
        Check if the histogram is weighted.

        Returns True if the bin content is of a non-integer type.
        """
        return self._bin_content_clean.dtype != np.int64

    def is_empty(self) -> bool:
        """Return True if the histogram is empty (i.e. sum of bin content is zero)."""
        return np.sum(self._bin_content_clean) == 0

    def sum(self) -> Union[float, int]:
        """
        Calculate the sum of bin contents.

        Returns
        -------
        Union[float, int]
            The sum of the bin contents, preserving the integer type if unweighted.
        """
        return self._bin_content_clean.sum()

    def integral(self, subranges: Optional[Union[List[ArrayLike], MultiRange]] = None) -> float:
        """
        Calculate the histogram integral.

        If subranges are provided, only bins whose centers lie within the subranges
        are included.

        Parameters
        ----------
        subranges : Optional[Union[List[ArrayLike], MultiRange]], default None
            A list of (min, max) tuples or a MultiRange instance specifying subranges.

        Returns
        -------
        float
            The integral (sum of bin contents multiplied by bin widths).
        """
        data = self._bin_content_clean
        if subranges is None:
            return np.sum(self.bin_widths * data)
        if isinstance(subranges, MultiRange):
            subranges = subranges.to_list()
        total = 0.
        centers = self.bin_centers
								  
        for (vmin, vmax) in subranges:
            mask = (vmin < centers) & (centers < vmax)
            total += np.sum(self.bin_widths[mask] * data[mask])
        return total

    def copy(self) -> Histogram1D:
        """
        Create a deep copy of the histogram.

        Returns
        -------
        Histogram1D
            A new instance with copied bin content, edges, errors, mask and ghost settings.
        """
        new_inst = type(self)(
            bin_content=self.bin_content,
            bin_edges=self.bin_edges,
            bin_errors=self._bin_errors,
            error_mode=self._error_mode,
            ghost_weight=self._ghost_weight
        )
        if self._bin_content_raw is not None:
            new_inst._bin_content_raw = self._bin_content_raw.copy()
        if self._bin_errors_raw is not None:
            new_inst._bin_errors_raw = (self._bin_errors_raw[0].copy(), self._bin_errors_raw[1].copy())
        if self._mask is not None:
            new_inst._mask = self._mask.copy()
        return new_inst

    def mask(
        self,
        condition: Union[Sequence[float], Callable]
    ) -> None:
        """
        Apply a mask to the histogram data.

        The mask is applied based on a condition provided as either a [min, max] range
        or a callable that returns a boolean array for each bin.

        Parameters
        ----------
        condition : Union[Sequence[float], Callable]
            The masking condition.
            
        Examples
        --------
        >>> hist.mask([1.0, 2.0])  # Mask bins outside the range [1, 2].
        >>> hist.mask(lambda x: x > 0)  # Mask bins where the bin center is not positive.
        """
        x = self.bin_centers
        has_errors = self.has_errors()

        # Store raw data if needed.
        if self._bin_content_raw is None:
            self._bin_content_raw = self._bin_content.copy()
            if has_errors:
                self._bin_errors_raw = (self._bin_errors[0].copy(), self._bin_errors[1].copy())
            y = self._bin_content
            yerr = self._bin_errors
        else:
            y = self._bin_content_raw
            yerr = self._bin_errors_raw

        mask = get_histogram_mask(x=x, y=y, condition=condition)
        y[mask] = 0
        if has_errors:
            yerr[0][mask] = 0.0
            yerr[1][mask] = 0.0
        self._mask = mask

    def unmask(self) -> None:
        """
        Remove any applied mask and restore the original data.
        """
        if self.is_masked():
            self._bin_content = self._bin_content_raw
            self._bin_errors = self._bin_errors_raw
            self._bin_content_raw = None
            self._bin_errors_raw = None
            self._mask = None

    def is_masked(self) -> bool:
        """
        Check if a mask is currently applied to the histogram.

        Returns
        -------
        bool
            True if a mask is applied, False otherwise.
        """
        return self._bin_content_raw is not None

    def scale(
        self,
        val: Union[Real, ArrayLike],
        inplace: bool = False
    ) -> Histogram1D:
        """
        Scale the histogram by a scalar or array.

        Parameters
        ----------
        val : Union[Real, ArrayLike]
            The scale factor(s).
        inplace : bool, default False
            If True, modify the histogram in place; otherwise, return a new histogram.

        Returns
        -------
        Histogram1D
            The scaled histogram.
        """
        if inplace:
            return self._ioperate("scale", val)
        return self._operate("scale", val)

    def normalize(
        self,
        density: bool = False,
        inplace: bool = False
    ) -> Histogram1D:
        """
        Normalize the histogram.

        The histogram is normalized by dividing by the total sum of its bin contents.
        If 'density' is True, normalization is done per unit bin width.

        Parameters
        ----------
        density : bool, default False
            If True, normalize by bin widths.
        inplace : bool, default False
            If True, modify the histogram in place; otherwise, return a new histogram.

        Returns
        -------
        Histogram1D
            The normalized histogram.
        """
        norm_factor = float(self.sum())
        if norm_factor == 0:
            return self.copy() if not inplace else self
        if density:
            norm_factor *= self.bin_widths
        if inplace:
            return self._ioperate("div", norm_factor)
        return self._operate("div", norm_factor)

    def reweight(
        self,
        other: Histogram1D,
        subranges: Optional[Union[List[ArrayLike], MultiRange]] = None,
        inplace: bool = False,
    ) -> Histogram1D:
        """
        Reweight the histogram so that its integral matches that of a reference histogram.

        The scale factor is determined by the ratio of the integrals over an optional subrange.

        Parameters
        ----------
        other : Histogram1D
            The reference histogram.
        subranges : Optional[Union[List[ArrayLike], MultiRange]], default None
            A subrange or list of subranges over which to compute the integrals.
        inplace : bool, default False
            If True, perform the operation in place; otherwise, return a new histogram.

        Returns
        -------
        Histogram1D
            The reweighted histogram.

        Raises
        ------
        ValueError
            If 'other' is not a Histogram1D instance.
        """
        if not isinstance(other, Histogram1D):
            raise ValueError("Operation only allowed between Histogram1D objects")
        if isinstance(subranges, MultiRange):
            subranges = subranges.to_list()
        scale_factor = other.integral(subranges=subranges) / self.integral(subranges=subranges)
        return self.scale(scale_factor, inplace=inplace)

    def compare(
        self,
        reference: Histogram1D,
        mode: ComparisonMode = "ratio"
    ) -> Histogram1D:
        """
        Compare the histogram with a reference histogram.

        The comparison can be done in various modes (e.g. ratio or difference).

        Parameters
        ----------
        reference : Histogram1D
            The reference histogram.
        mode : ComparisonMode, default "ratio"
            The comparison mode ("ratio", "difference", or a callable).

        Returns
        -------
        Histogram1D
            A new histogram representing the comparison result.

        Raises
        ------
        ValueError
            If an invalid comparison mode is specified.
        """
        if callable(mode):
            return mode(self, reference)
            
        mode = HistComparisonMode.parse(mode)
        if mode == HistComparisonMode.RATIO:
            return self / reference
        elif mode == HistComparisonMode.DIFFERENCE:
            return self - reference
        raise ValueError(f"Unknown comparison mode: {mode}")

    def remove_errors(self) -> None:
        """
        Remove all error information from the histogram.

        After calling this method, the histogram will no longer have associated bin errors.
        """
        self._bin_errors = None
        self._bin_errors_raw = None

    def get_bin_center(self, index: int) -> float:
        if (index < 0) or (index >= self.nbins):
            raise ValueError('Bin index out of range')
        return self.bin_centers[index]

    def get_mean(self) -> float:
        """
        Calculate the mean value of the histogram.

        The mean is computed as the weighted average of the bin centers, weighted by the bin contents.

        Returns
        -------
        float
            The mean value.
        """
        x, y = self.bin_centers, self._bin_content_clean
        return np.sum(x * y) / np.sum(y)

    def get_std(self) -> float:
        """
        Calculate the standard deviation of the histogram.

        The standard deviation is computed using the weighted variance of the bin centers.

        Returns
        -------
        float
            The standard deviation.
        """
        mean = self.get_mean()
        x, y = self.bin_centers, self._bin_content_clean
        total = np.sum(y)
        if total == 0.0:
            return 0.0
        var = np.max([np.sum(y * (x - mean) ** 2) / total, 0.0])
        return np.sqrt(var)

    def get_effective_entries(self) -> float:
        """
        Calculate the effective number of entries in the histogram.

        For Poisson errors, this is simply the sum of the bin contents.
        Otherwise, it is computed as (sum of bin contents)^2 divided by the sum of squared errors.

        Returns
        -------
        float
            The effective number of entries.
        """
        if self._error_mode == BinErrorMode.POISSON:
            return self.sum()
        if self._bin_errors is None:
            return 0.
        sumw2 = np.sum(self._bin_errors[0] ** 2)
        if sumw2 != 0:
            return (self.sum() ** 2) / sumw2
        return 0.
        
    def get_mean_error(self) -> float:
        """
        Calculate the error on the histogram mean.

        This is given by the standard deviation divided by the square root of the effective entries.

        Returns
        -------
        float
            The error on the mean.
        """
        neff = self.get_effective_entries()
        if neff > 0:
            return self.get_std() / np.sqrt(neff)
        return 0.0

    def get_cumul_hist(self) -> Histogram1D:
        """
        Compute the cumulative histogram.

        The cumulative histogram is obtained by summing the bin contents sequentially,
        with errors propagated in quadrature.

        Returns
        -------
        Histogram1D
            A new histogram representing the cumulative distribution.
        """
        bin_content = self._bin_content_clean
        cum_bin_content = np.cumsum(bin_content)
        if self._bin_errors is not None:
            cum_errors = (np.sqrt(np.cumsum(self._bin_errors[0] ** 2)),
                          np.sqrt(np.cumsum(self._bin_errors[1] ** 2)))
        else:
            cum_errors = None
        return Histogram1D(
            bin_content=cum_bin_content,
            bin_edges=self.bin_edges,
            bin_errors=cum_errors,
            error_mode=self._error_mode,
            ghost_weight=self._ghost_weight
        )

    def get_maximum(self) -> float:
        """
        Get the maximum bin content.

        Returns
        -------
        float
            The maximum value in the bin content array.
        """
        return np.max(self._bin_content_clean)

    def get_minimum(self) -> float:
        """
        Get the minimum bin content.

        Returns
        -------
        float
            The minimum value in the bin content array.
        """
        return np.min(self._bin_content_clean)

    def get_maximum_bin(self) -> int:
        """
        Get the index of the bin with the maximum content.

        Returns
        -------
        int
            The index of the maximum bin.
        """
        return int(np.argmax(self._bin_content_clean))

    def get_minimum_bin(self) -> int:
        """
        Get the index of the bin with the minimum content.

        Returns
        -------
        int
            The index of the minimum bin.
        """
        return int(np.argmin(self._bin_content_clean))

    def get_bin_content_slice(
        self,
        first_bin: Optional[int] = None,
        last_bin: Optional[int] = None,
    ) -> np.ndarray:
        """
        Return a slice of the bin content array.

        Parameters
        ----------
        first_bin : Optional[int], default None
            The starting bin index (inclusive). Defaults to 0.
        last_bin : Optional[int], default None
            The ending bin index (exclusive). Defaults to the total number of bins.

        Returns
        -------
        np.ndarray
            The sliced bin content array.
        """
        if first_bin is None:
            first_bin = 0
        if last_bin is None:
            last_bin = self.nbins
        return self._bin_content_clean[first_bin:last_bin]

    def get_first_bin_above(
        self,
        threshold: float,
        first_bin: Optional[int] = None,
        last_bin: Optional[int] = None
    ) -> Optional[int]:
        """
        Get the index of the first bin with content above a given threshold.

        Parameters
        ----------
        threshold : float
            The threshold value.
        first_bin : Optional[int], default None
            The starting index for the search.
        last_bin : Optional[int], default None
            The ending index for the search.

        Returns
        -------
        Optional[int]
            The index of the first bin above the threshold, or None if none found.
        """
        slice_data = self.get_bin_content_slice(first_bin, last_bin)
        indices = np.where(slice_data > threshold)[0]
        if indices.size:
            return int(indices[0] + (first_bin or 0))
        return None

    def get_last_bin_above(
        self,
        threshold: float,
        first_bin: Optional[int] = None,
        last_bin: Optional[int] = None
    ) -> Optional[int]:
        """
        Get the index of the last bin with content above a given threshold.

        Parameters
        ----------
        threshold : float
            The threshold value.
        first_bin : Optional[int], default None
            The starting index for the search.
        last_bin : Optional[int], default None
            The ending index for the search.

        Returns
        -------
        Optional[int]
            The index of the last bin above the threshold, or None if none found.
        """
        slice_data = self.get_bin_content_slice(first_bin, last_bin)
        indices = np.where(slice_data > threshold)[0]
        if indices.size:
            return int(indices[-1] + (first_bin or 0))
        return None

    def apply_ghost(
        self,
        ghost_weight: Optional[float] = None,
        inplace: bool = False
    ) -> Histogram1D:
        """
        Replace zero-valued bins with a small ghost weight.

        This is useful for operations (like logarithms or ratios) that cannot handle zeros.
        Note that bin errors are not modified.

        Parameters
        ----------
        ghost_weight : Optional[float], default None
            The ghost weight to apply; if None, uses the instance ghost_weight.
        inplace : bool, default False
            If True, modify the histogram in place; otherwise, return a new histogram.

        Returns
        -------
        Histogram1D
            The histogram with ghost weights applied.
        """
        h = self if inplace else self.copy()
        gw = ghost_weight if ghost_weight is not None else self._ghost_weight
        h._bin_content = apply_ghost(h._bin_content, gw)
        if h.is_masked():
            h._bin_content_raw = apply_ghost(h._bin_content_raw, gw)
        return h

    def remove_ghost(
        self,
        ghost_threshold: Optional[float] = None,
        inplace: bool = False
    ) -> Histogram1D:
        """
        Remove ghost bins by setting bins with very low content to zero.

        Bins with content less than or equal to ghost_threshold are set to zero.
        Bin errors remain unaffected.

        Parameters
        ----------
        ghost_threshold : Optional[float], default None
            The threshold value below which bins are considered ghosts; if None, uses the instance ghost_weight.
        inplace : bool, default False
            If True, modify the histogram in place; otherwise, return a new histogram.

        Returns
        -------
        Histogram1D
            The histogram with ghost bins removed.
        """
        h = self if inplace else self.copy()
        gt = ghost_threshold if ghost_threshold is not None else self._ghost_weight
        h._bin_content = remove_ghost(h._bin_content, gt)
        if h.is_masked():
            h._bin_content_raw = remove_ghost(h._bin_content_raw, gt)
        return h

    def has_ghost(
        self,
        ghost_threshold: Optional[float] = None
    ) -> bool:
        """
        Check whether the histogram contains any ghost bins.

        A ghost bin is defined as one with positive content that is less than or equal to the ghost threshold.

        Parameters
        ----------
        ghost_threshold : Optional[float], default None
            The ghost threshold to use; if None, uses the instance ghost_weight.

        Returns
        -------
        bool
            True if at least one ghost bin is present, False otherwise.
        """
        gt = ghost_threshold if ghost_threshold is not None else self._ghost_weight
        return has_ghost(self._bin_content, ghost_threshold=gt)

    def rebin(
        self,
        bins: Union[ArrayLike, int],
        keep_ghost: bool = True,
        inplace: bool = False,
    ) -> Histogram1D:
        """
        Rebin the histogram to a new binning specification.

        When rebinning, the method creates a new Binning instance and checks whether its
        bin edges are compatible with the current histogram’s binning. If not, a warning is
        issued. Optionally, ghost bins (i.e. very low values) can be removed prior to rebinning
        and then reintroduced after rebinning.

        Parameters
        ----------
        bins : Union[ArrayLike, int]
            If an integer, it defines the new number of bins. It must be positive and no larger
            than the current number of bins. If an array-like, it specifies the new bin edges.
        keep_ghost : bool, default True
            Whether to retain ghost bins. If True, ghost bins (values ≤ ghost_threshold) are
            removed before rebinning and re-applied afterward.
        inplace : bool, default False
            If True, modify the current histogram; otherwise, return a new histogram instance.

        Returns
        -------
        Histogram1D
            The rebinned histogram.
        
        Raises
        ------
        ValueError
            If the new number of bins is not positive, exceeds the current number of bins, or if
            the new binning is incompatible with the original histogram.

        Examples
        --------
        The following stand-alone example demonstrates how to rebin a histogram:
        
        >>> import numpy as np
        >>> # Create a histogram with 100 bins over [0,10]
        >>> bin_edges = np.linspace(0, 10, 101)
        >>> counts = np.random.poisson(5, size=100)
        >>> # Create the histogram instance
        >>> hist = Histogram1D(bin_content=counts, bin_edges=bin_edges)
        >>> print("Original number of bins:", hist.nbins)
        Original number of bins: 100
        >>> # Rebin the histogram to 10 bins while keeping ghost bins intact.
        >>> hist_rebinned = hist.rebin(bins=10, keep_ghost=True)
        >>> print("Rebinned number of bins:", hist_rebinned.nbins)
        Rebinned number of bins: 10
        """
        if isinstance(bins, int):
            if bins <= 0:
                raise ValueError("Number of bins in the new histogram must be positive.")
            if bins > self.nbins:
                raise ValueError("Number of bins in the new histogram cannot be larger than the original histogram.")
            if self.nbins % bins != 0:
                stdout.warning(
                    f"New binning (= {bins}) is not an exact divider of the original binning (= {self.nbins})."
                )
            binning_new = Binning(bins=bins, bin_range=self.bin_range)
        else:
            binning_new = Binning(bins=bins)
    
        if not binning_new.is_compatible(self.binning):
            incompatible_edges = sorted(set(range(binning_new.nbins)) - set(binning_new.overlapped_edges(self.binning)))
            stdout.warning(
                "The following bin edge(s) of the rebinned histogram do not match any of the original histogram. "
                "Result can be inconsistent.\n" + ", ".join(str(i) for i in incompatible_edges)
            )
    
        hnew = self if inplace else self.copy()
        if hnew.is_masked():
            stdout.warning("Mask information will be lost after histogram rebinning.")
            hnew.unmask()

        ghost_exist = self.has_ghost()

        x = hnew.bin_centers
        y = hnew._bin_content_clean
        yerr = hnew._bin_errors

        y_rebinned, _, _ = histogram(
            x=x,
            weights=y,
            bins=binning_new.bin_edges,
            evaluate_error=False
        )
        y_rebinned = y_rebinned.astype(y.dtype)
    
        if self.error_mode == BinErrorMode.POISSON:
            yerr_rebinned = poisson_interval(y_rebinned)
        elif (self.error_mode == BinErrorMode.SUMW2) and (yerr is not None):
            # Check for symmetric errors
            if np.array_equal(yerr[0], yerr[1]):
                yerr2, _, _ = histogram(
                    x=x,
                    weights=yerr[0] ** 2,
                    bins=binning_new.bin_edges,
                    evaluate_error=False
                )
                yerr_rebinned = tuple(np.tile(np.sqrt(yerr2), (2, 1)))
            else:
                nbins_new = binning_new.nbins
                yerr_rebinned = [np.zeros(nbins_new), np.zeros(nbins_new)]
                for i, yerr_i in enumerate(yerr):
                    yerr2, _, _ = histogram(
                        x=x,
                        weights=yerr_i ** 2,
                        bins=binning_new.bin_edges,
                        evaluate_error=False
                    )
                    yerr_rebinned[i] = np.sqrt(yerr2)
                yerr_rebinned = tuple(yerr_rebinned)
        else:
            yerr_rebinned = None
    
        if keep_ghost and ghost_exist:
            y_rebinned = apply_ghost(y_rebinned, ghost_weight=self.ghost_weight)

        hnew._binning = binning_new
        hnew._bin_content = y_rebinned
        hnew._bin_errors = yerr_rebinned
        hnew._error_mode = self.error_mode
    
        return hnew