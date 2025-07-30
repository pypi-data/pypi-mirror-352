from __future__ import annotations

import math
from numbers import Real
from typing import Any, Generic, TypeVar, Union

import numpy as np
from numpy.typing import ArrayLike

T = TypeVar('T', bound=Real)

def parse_range(
    value: Union[Range, list, tuple, np.ndarray]
) -> Tuple[float, float, bool, bool]:
    if isinstance(value, Range):
        return value.min, value.max, value.lbound, value.rbound
    elif isinstance(value, (tuple, list, np.ndarray)):
        if isinstance(value, np.ndarray) and value.ndim != 1:
            raise ValueError(f"Invalid array format. Expected 1D array, but got {value.ndim}D array.")
        if len(value) == 2:
            return value[0], value[1], True, True
        elif len(value) == 4:
            return value[0], value[1], bool(value[2]), bool(value[3])
        else:
            if isinstance(value, list):
                raise ValueError(f"Invalid list format. Expected a 2-element or 4-element list, but got: {value}")
            elif isinstance(value, tuple):
                raise ValueError(f"Invalid tuple format. Expected a 2-tuple or 4-tuple, but got: {value}")
            else:
                raise ValueError(f"Invalid array format. Expected 2 or 4 elements, but got: {value}")
    else:
        raise ValueError(f"Invalid range format. Expected a Range object, tuple, list, or array, but got: {type(value)}")
        
def validate_ranges(
    min_values: ArrayLike,
    max_values: ArrayLike,
    lbounds: Union[bool, ArrayLike] = True,
    rbounds: Union[bool, ArrayLike] = True,
    min_size: int = 1,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Validate and standardize ranges with their inclusivity bounds.
    """
    min_values = np.asarray(min_values, dtype=float)
    max_values = np.asarray(max_values, dtype=float)

    if isinstance(lbounds, bool):
        lbounds = np.full_like(min_values, lbounds, dtype=bool)
    else:
        lbounds = np.asarray(lbounds, dtype=bool)

    if isinstance(rbounds, bool):
        rbounds = np.full_like(max_values, rbounds, dtype=bool)
    else:
        rbounds = np.asarray(rbounds, dtype=bool)

    if not (
        (min_values.ndim == 1) and
        (min_values.size == max_values.size == lbounds.size == rbounds.size)
    ):
        raise ValueError("All input arrays must have the same size and be one-dimensional.")
    if len(min_values) < min_size:
        raise ValueError(f"All input arrays must have at least {min_size} elements.")
    if np.any(min_values > max_values):
        raise ValueError("Each min value must be less than or equal to its corresponding max value.")

    if np.any(np.isnan(min_values)) or np.any(np.isnan(max_values)):
        raise ValueError("Range values cannot be NaN.")

    return min_values, max_values, lbounds, rbounds

def sort_ranges(
    min_values: ArrayLike,
    max_values: ArrayLike,
    lbounds: Union[bool, ArrayLike] = True,
    rbounds: Union[bool, ArrayLike] = True,
    validate: bool = True,
    sort_by_max: bool = False,
    sort_by_bounds: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Sort ranges by `min_values` and optionally by `max_values`, `lbounds`, and `rbounds`.
    """
    if validate:
        min_values, max_values, lbounds, rbounds = validate_ranges(min_values, max_values, lbounds, rbounds)

    keys = [min_values]
    if sort_by_max:
        keys.append(max_values)
    if sort_by_bounds:
        keys.extend([lbounds, rbounds])

    sorted_indices = np.lexsort(tuple(reversed(keys)))

    return (
        min_values[sorted_indices],
        max_values[sorted_indices],
        lbounds[sorted_indices],
        rbounds[sorted_indices],
    )


def overlapped_ranges(
    min_values: ArrayLike,
    max_values: ArrayLike,
    lbounds: Union[bool, ArrayLike] = True,
    rbounds: Union[bool, ArrayLike] = True
) -> bool:
    """
    Check if any ranges overlap, considering inclusivity of bounds.
    """
    min_values, max_values, lbounds, rbounds = validate_ranges(min_values, max_values, lbounds, rbounds, min_size=2)

    if len(min_values) == 2:
        return _check_overlap(
            min_values[0], max_values[0], lbounds[0], rbounds[0],
            min_values[1], max_values[1], lbounds[1], rbounds[1]
        )

    min_values, max_values, lbounds, rbounds = sort_ranges(min_values, max_values, lbounds, rbounds, validate=False)

    diff = max_values[:-1] - min_values[1:]
    return np.any((diff > 0) | ((diff == 0) & rbounds[:-1] & lbounds[1:]))


def _check_overlap(
    min1: T, max1: T, lbound1: bool, rbound1: bool,
    min2: T, max2: T, lbound2: bool, rbound2: bool
) -> bool:
    """
    Check if two ranges overlap, considering inclusivity of bounds.
    """
    if max1 < min2:
        return False
    if max1 == min2:
        return rbound1 and lbound2
    if min1 > max2:
        return False
    if min1 == max2:
        return lbound1 and rbound2
    return True

def _get_indices(
    indices: Union[int, slice, Sequence[int], np.ndarray], size: int
) -> np.ndarray:
    """
    Handle indexing logic for both single and multiple indices.

    Parameters
    ----------
    indices : Union[int, slice, Sequence[int], np.ndarray]
        Indices to retrieve.
    size : int
        Size of the array.

    Returns
    -------
    np.ndarray
        Array of indices to retrieve.
    """
    if isinstance(indices, int):
        if indices < 0:
            indices += size
        if indices < 0 or indices >= size:
            raise IndexError(f"Index {indices} is out of range for array of size {size}.")
        return np.array([indices])
    elif isinstance(indices, slice):
        # Use np.arange to handle slice indices automatically, including negatives
        return np.arange(size)[indices]
    elif isinstance(indices, (Sequence, np.ndarray)):
        indices = np.asarray(indices)
        # Convert negative indices to positive equivalents
        indices = np.where(indices < 0, indices + size, indices)
        if np.any(indices < 0) or np.any(indices >= size):
            raise IndexError("Some indices are out of range.")
        return indices
    else:
        raise TypeError("Indices must be an integer, slice, or sequence of integers.")


class Range:
    """
    A class representing a range with named attributes `min` and `max`,
    along with options to indicate whether the bounds are inclusive.

    Attributes
    ----------
    min : Real
        The lower bound of the range.
    max : Real
        The upper bound of the range.
    lbound : bool
        Indicates if the lower bound is inclusive. Defaults to True.
    rbound : bool
        Indicates if the upper bound is inclusive. Defaults to True.

    Raises
    ------
    ValueError
        If min is greater than max during initialization.
    """

    __slots__ = ('_min', '_max', '_lbound', '_rbound')

    def __init__(self, min: T, max: T, lbound: bool = True, rbound: bool = True) -> None:
        if min > max:
            raise ValueError("`min` must be less than or equal to `max`")
        self._min = min
        self._max = max
        self._lbound = lbound
        self._rbound = rbound

    @property
    def min(self) -> Real:
        """The lower bound of the range."""
        return self._min

    @property
    def max(self) -> Real:
        """The upper bound of the range."""
        return self._max

    @property
    def lbound(self) -> bool:
        """Whether the lower bound is inclusive."""
        return self._lbound

    @property
    def rbound(self) -> bool:
        """Whether the upper bound is inclusive."""
        return self._rbound

    def __getitem__(self, index: int) -> Real:
        """
        Access range values by index.

        Parameters
        ----------
        index : int
            The index to access (0 for min, 1 for max).

        Returns
        -------
        Real
            The value at the specified index.

        Raises
        ------
        IndexError
            If the index is out of range.
        """
        if index == 0:
            return self._min
        elif index == 1:
            return self._max
        raise IndexError("Range index out of range. Valid indices are 0 and 1.")

    def __len__(self) -> int:
        """
        Return the length of the range (always 2).

        Returns
        -------
        int
            The length of the range.
        """
        return 2

    def __iter__(self):
        """
        Allow unpacking of the range as a tuple (min, max).

        Returns
        -------
        iterator
            An iterator over (min, max).
        """
        return iter((self._min, self._max))

    def __lt__(self, other):
        if not isinstance(other, Range):
            return NotImplemented
        return (self._min, self._max, self._lbound, self._rbound) < (other._min, other._max, other._lbound, other._rbound)

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Range.

        Parameters
        ----------
        other : object
            The object to compare.

        Returns
        -------
        bool
            True if the other object is a Range with the same min, max,
            lbound, and rbound.
        """
        if not isinstance(other, Range):
            return False
        return (
            self._min == other._min and
            self._max == other._max and
            self._lbound == other._lbound and
            self._rbound == other._rbound
        )

    def __repr__(self) -> str:
        """
        String representation of the Range.

        Returns
        -------
        str
            A string representation of the Range.
        """
        return f"{self.__class__.__name__}(min={self._min!r}, max={self._max!r}, lbound={self._lbound!r}, rbound={self._rbound!r})"

    def __contains__(self, value: Real) -> bool:
        """
        Check if a value is within the range, considering the inclusivity
        of the bounds.

        Parameters
        ----------
        value : Real
            The value to check.

        Returns
        -------
        bool
            True if the value is within the range, False otherwise.
        """
        if self._lbound and self._rbound:
            return self._min <= value <= self._max
        if self._lbound:
            return self._min <= value < self._max
        if self._rbound:
            return self._min < value <= self._max
        return self._min < value < self._max

    @classmethod
    def create(cls, data: Any) -> Range:
        if data is None:
            return cls(-math.inf, math.inf)
        if isinstance(data, Range):
            return cls(data._min, data._max, data._lbound, data._rbound)
        if isinstance(data, (list, tuple, np.ndarray)):
            return cls(*data)
        if isinstance(data, dict):
            return cls(**data)
        raise TypeError(
            f"Unsupported input type: {type(data)}"
        )

    def is_finite_min(self) -> bool:
        return math.isfinite(self._min)

    def is_finite_max(self) -> bool:
        return math.isfinite(self._max)

    def is_finite(self) -> bool:
        return self.is_finite_min() and self.is_finite_max()
        
    def overlap_with(self, other: Range, ignore_boundary: bool = False) -> bool:
        """
        Check whether this range overlaps with another range.

        Parameters
        ----------
        other : Range
            Another Range object to check for overlap.
        ignore_boundary : bool, optional
            If True, boundaries are ignored when checking for overlap.
            Defaults to False.

        Returns
        -------
        bool
            True if the ranges overlap, False otherwise.
        """
        if not isinstance(other, Range):
            raise TypeError("`other` must be an instance of Range")
        if ignore_boundary:
            return self._min < other._max and other._min < self._max
        return _check_overlap(
            self._min, self._max, self._lbound, self._rbound,
            other._min, other._max, other._lbound, other._rbound,
        )

class MultiRange:
    """
    A class to represent multiple ranges with inclusivity options for bounds.
    """

    def __init__(
        self,
        min_values: ArrayLike,
        max_values: ArrayLike,
        lbounds: Union[bool, ArrayLike] = True,
        rbounds: Union[bool, ArrayLike] = True,
    ):
        self.min_values, self.max_values, self.lbounds, self.rbounds = validate_ranges(
            min_values, max_values, lbounds, rbounds, min_size=0
        )

    def __len__(self) -> int:
        return len(self.min_values)

    def __getitem__(self, indices: Union[int, slice, Sequence[int], np.ndarray]) -> Union[Range, MultiRange]:
        """
        Access a range or a slice of ranges.

        Parameters
        ----------
        indices : Union[int, slice, Sequence[int], np.ndarray]
            Indices to access.

        Returns
        -------
        Union[Range, MultiRange]
            A `Range` object if a single index is requested, or a `MultiRange` for multiple indices.
        """
        indices = _get_indices(indices, len(self.min_values))
        if not len(indices):
            raise ValueError('`indices` can not be empty.')
        elif len(indices) == 1:
            idx = indices[0]
            return Range(
                self.min_values[idx],
                self.max_values[idx],
                self.lbounds[idx],
                self.rbounds[idx],
            )
        return MultiRange(
            self.min_values[indices],
            self.max_values[indices],
            self.lbounds[indices],
            self.rbounds[indices],
        )

    def __iter__(self) -> Iterable[Range]:
        """
        Make MultiRange iterable.

        Yields
        ------
        Range
            Each range as a `Range` object.
        """
        for i in range(len(self.min_values)):
            yield Range(
                self.min_values[i],
                self.max_values[i],
                self.lbounds[i],
                self.rbounds[i],
            )

    def __repr__(self) -> str:
        return (
            f"MultiRange("
            f"min_values={self.min_values}, max_values={self.max_values}, "
            f"lbounds={self.lbounds}, rbounds={self.rbounds})"
        )

    @classmethod
    def from_list(cls, ranges: Iterable[Union[Tuple, List, np.ndarray, Range]]) -> MultiRange:
        """
        Create a MultiRange instance from an iterable of ranges.
    
        Parameters
        ----------
        ranges : Iterable[Union[Tuple, List, np.ndarray, Range]]
            An iterable where each element can be:
            - A `Range` object
            - A 2-tuple, 2-list, or 1D NumPy array [min, max]
            - A 4-tuple, 4-list, or 1D NumPy array [min, max, lbound, rbound]
    
        Returns
        -------
        MultiRange
            A new MultiRange instance containing the specified ranges.
    
        Raises
        ------
        ValueError
            If any input is invalid or does not match the expected format.
    
        Examples
        --------
        >>> MultiRange.from_list([(1, 2), [3, 4, False, True]])
        MultiRange(min_values=[1. 3.], max_values=[2. 4.], lbounds=[True, False], rbounds=[True, True])
    
        >>> MultiRange.from_list([Range(1, 2), [3, 4]])
        MultiRange(min_values=[1. 3.], max_values=[2. 4.], lbounds=[True, True], rbounds=[True, True])
    
        >>> MultiRange.from_list([[1, 2, True]])  # Invalid input
        Traceback (most recent call last):
            ...
        ValueError: Invalid list format. Expected a 2-element or 4-element list, but got: [1, 2, True]
        """
        min_values, max_values, lbounds, rbounds = [], [], [], []
    
        for value in ranges:
            min_val, max_val, lbound, rbound = parse_range(value)
            min_values.append(min_val)
            max_values.append(max_val)
            lbounds.append(lbound)
            rbounds.append(rbound)
            
        return cls(min_values, max_values, lbounds, rbounds)

    @classmethod
    def create(cls, data: Any=None) -> MultiRange:
        data = data or []
        if isinstance(data, (list, tuple)):
            return cls.from_list(data)
        if isinstance(data, MultiRange):
            return cls(data.min_values, data.max_values, data.lbounds, data.rbounds)
        raise TypeError(
            f"Unsupported input type: {type(data)}"
        )

    def to_list(self, orient: str = "tuple") -> List[Union[Tuple, Range]]:
        """
        Convert the MultiRange instance to a list.

        Parameters
        ----------
        orient : str, optional
            Specifies the format of the list entries. Can be either "tuple" or "range".
            Defaults to "tuple".

        Returns
        -------
        List[Union[Tuple, Range]]
            A list of ranges in the specified format.
        """
        if orient == "tuple":
            return [
                (self.min_values[i], self.max_values[i], self.lbounds[i], self.rbounds[i])
                for i in range(len(self.min_values))
            ]
        elif orient == "range":
            return [
                Range(self.min_values[i], self.max_values[i], self.lbounds[i], self.rbounds[i])
                for i in range(len(self.min_values))
            ]
        else:
            raise ValueError("Invalid orient value. Must be 'tuple' or 'range'.")

    def sort(self, sort_by_max: bool = False, sort_by_bounds: bool = False):
        """
        Sort ranges by `min_values` and optionally by `max_values`, `lbounds`, and `rbounds`.

        Parameters
        ----------
        sort_by_max : bool, optional
            Whether to sort by `max_values` in case of ties in `min_values`. Defaults to False.
        sort_by_bounds : bool, optional
            Whether to sort by `lbounds` and `rbounds` in case of further ties. Defaults to False.
        """
        self.min_values, self.max_values, self.lbounds, self.rbounds = sort_ranges(
            self.min_values, 
            self.max_values, 
            self.lbounds, 
            self.rbounds,
            validate=False
        )
        return self

    def select(self, indices: Union[int, slice, Sequence[int], np.ndarray]) -> Union[Range, MultiRange]:
        """
        Select specific ranges by indices.

        Parameters
        ----------
        indices : Union[int, Sequence[int]]
            An integer or sequence of integers representing the indices to select.

        Returns
        -------
        MultiRange
            A new MultiRange instance with the selected ranges.
        """
        return self[indices]

    def delete(self, index: int = -1) -> None:
        """
        Delete a range at the specified index.
    
        Parameters
        ----------
        index : int, optional
            The index of the range to delete. Defaults to -1 (last range).
    
        Raises
        ------
        IndexError
            If the MultiRange is empty or the index is out of range.
        """
        if not self.min_values.size:
            raise IndexError("Cannot delete from an empty MultiRange.")
        
        if index < 0:
            index += len(self.min_values)
        
        if index < 0 or index >= len(self.min_values):
            raise IndexError(f"Index {index} is out of range for MultiRange with size {len(self.min_values)}.")
        
        self.min_values = np.delete(self.min_values, index)
        self.max_values = np.delete(self.max_values, index)
        self.lbounds = np.delete(self.lbounds, index)
        self.rbounds = np.delete(self.rbounds, index)

    def pop(self, index: int = -1) -> Range:
        """
        Remove and return a range at the specified index.

        Parameters
        ----------
        index : int, optional
            The index of the range to pop. Defaults to -1 (last range).

        Returns
        -------
        Range
            The removed range.
        """
        if not self.min_values.size:
            raise IndexError("Cannot pop from an empty MultiRange.")

        result = self[index]
        self.delete(index)
        return result

    def append(self, value: Union[Range, tuple, list, np.ndarray]) -> None:
        """
        Append a new range to the MultiRange.

        Parameters
        ----------
        range_obj : Union[Tuple, Range]
            The range to append. Can be a Range object or a tuple.

        Raises
        ------
        ValueError
            If the input range is invalid.
        """
        min_val, max_val, lbound, rbound = parse_range(value)

        self.min_values = np.append(self.min_values, min_val)
        self.max_values = np.append(self.max_values, max_val)
        self.lbounds = np.append(self.lbounds, lbound)
        self.rbounds = np.append(self.rbounds, rbound)

    def clear(self) -> None:
        self.min_values = np.array([])
        self.max_values = np.array([])
        self.lbounds = np.array([])
        self.rbounds = np.array([])

    def to_list(self) -> List[Tuple[float, float]]:
        return [v for v in zip(self.min_values, self.max_values)]

    def is_overlapping(self, ignore_boundary: bool = False) -> bool:
        """
        Check if any ranges in the MultiRange overlap.
    
        Parameters
        ----------
        ignore_boundary : bool, optional
            If True, overlap is determined without considering inclusivity of range boundaries.
            For example, ranges [1, 2] and [2, 3] would be considered overlapping if
            `ignore_boundary` is True, even though they meet at a single point.
            Defaults to False.
    
        Returns
        -------
        bool
            True if any ranges overlap, False otherwise.
    
        Examples
        --------
        >>> mr = MultiRange([1, 3, 5], [2, 4, 6])
        >>> mr.is_overlapping()
        False
    
        >>> mr = MultiRange([1, 2], [2, 3])
        >>> mr.is_overlapping()
        True
        >>> mr.is_overlapping(ignore_boundary=True)
        False
        """
        if ignore_boundary:
            return overlapped_ranges(self.min_values, self.max_values, False, False)
        return overlapped_ranges(self.min_values, self.max_values, self.lbounds, self.rbounds)

    def is_contiguous(
        self,
        ignore_boundary: bool = False,
        allow_double_boundary: bool = False,
    ) -> bool:
        """
        Check if ranges form a continuous sequence without gaps.
        
        A sequence of ranges is considered contiguous if:
        1. There are no gaps between ranges
        2. There are no overlaps between ranges
        3. A point where two ranges meet has compatible boundary conditions
           (depending on ignore_boundary and allow_double_boundary parameters)
        
        Parameters
        ----------
        ignore_boundary : bool, optional
            If True, skip checking boundary conditions between ranges.
            Defaults to False.
        allow_double_boundary : bool, optional
            If True, allows both bounds to be inclusive at meeting points.
            Ignored if ignore_boundary is True.
            Defaults to False.
        
        Returns
        -------
        bool
            True if ranges form a continuous sequence, False otherwise.
    
        Examples
        --------
        >>> mr = MultiRange([1, 3, 5], [2, 4, 6])  # Gaps between ranges
        >>> mr.is_contiguous()
        False
        
        >>> mr = MultiRange([1, 2, 3], [2, 3, 4])  # Contiguous ranges
        >>> mr.is_contiguous()
        True
        
        >>> mr = MultiRange([1, 2], [2, 3], [True, True], [True, True])
        >>> mr.is_contiguous()  # Double counting point 2
        False
        >>> mr.is_contiguous(allow_double_boundary=True)  # Allowing double boundary
        True
        >>> mr.is_contiguous(ignore_boundary=True)  # Ignoring boundary conditions
        True
        """
        if len(self) <= 1:
            return True
            
        min_values, max_values, lbounds, rbounds = sort_ranges(
            self.min_values, 
            self.max_values, 
            self.lbounds, 
            self.rbounds,
            validate=False
        )
        
        diff = min_values[1:] - max_values[:-1]
        
        if np.any(diff != 0):
            return False

        if not ignore_boundary:
            if allow_double_boundary:
                # At least one bound must be inclusive at meeting points
                boundary_valid = rbounds[:-1] | lbounds[1:]
            else:
                # Only one bound should be inclusive at meeting points
                boundary_valid = rbounds[:-1] ^ lbounds[1:]
    
            return np.all(boundary_valid)
            
        return True

class NamedRanges(MultiRange):
    """
    A class to represent multiple named ranges with inclusivity options for bounds.
    Inherits from MultiRange and adds the capability to associate ranges with unique names.
    """

    def __init__(
        self,
        names: ArrayLike,
        min_values: ArrayLike,
        max_values: ArrayLike,
        lbounds: Union[bool, ArrayLike] = True,
        rbounds: Union[bool, ArrayLike] = True,
    ):
        super().__init__(min_values, max_values, lbounds, rbounds)
        self.names = np.asarray(names, dtype=str)

        if len(self.names) != len(self.min_values):
            raise ValueError("Names array must have the same size as the ranges.")
        if len(set(self.names)) != len(self.names):
            raise ValueError("Names must be unique.")

        self._name_to_index = {name: idx for idx, name in enumerate(self.names)}
    
    def __iter__(self) -> Iterable[Tuple[str, Range]]:
        """
        Make NamedRanges iterable.
    
        Yields
        ------
        Tuple[str, Range]
            Each range as a tuple of (name, Range object).
        """
        for name, min_val, max_val, lbound, rbound in zip(
            self.names, self.min_values, self.max_values, self.lbounds, self.rbounds
        ):
            yield name, Range(min_val, max_val, lbound, rbound)

    def __getitem__(self, names: Union[str, Sequence[str], np.ndarray]) -> Union[Range, NamedRanges]:
        """
        Access a named range or a selection of named ranges.

        Parameters
        ----------
        names : Union[str, Sequence[str], np.ndarray]
            The name(s) of the range(s) to access.

        Returns
        -------
        Union[Range, NamedRanges]
            A `Range` object if a single name is requested, or a `NamedRanges` for multiple names.
        """
        if isinstance(names, str):
            names = [names]
        if not len(names):
            raise ValueError('`names` can not be empty.')
        indices = []
        for name in names:
            if name not in self._name_to_index:
                raise KeyError(f"Range with name '{name}' not found. Available names: {list(self._name_to_index.keys())}")
            indices.append(self._name_to_index[name])

        indices = np.asarray(indices)
        if len(indices) == 1:
            idx = indices[0]
            return Range(
                self.min_values[idx],
                self.max_values[idx],
                self.lbounds[idx],
                self.rbounds[idx],
            )
        return NamedRanges(
            self.names[indices],
            self.min_values[indices],
            self.max_values[indices],
            self.lbounds[indices],
            self.rbounds[indices],
        )

    def __setitem__(self, key: str, value: Any):
        self.update({key: value})

    def __repr__(self) -> str:
        """
        String representation of the NamedRanges object.

        Returns
        -------
        str
            A string representation of the NamedRanges object.
        """
        ranges = [
            f"{self.names[i]}: ({self.min_values[i]}, {self.max_values[i]}, "
            f"lbound={self.lbounds[i]}, rbound={self.rbounds[i]})"
            for i in range(len(self))
        ]
        return f"NamedRanges({', '.join(ranges)})"

    @classmethod
    def from_dict(cls, ranges_dict: Dict[str, Union[Tuple, List, np.ndarray, Range]]) -> NamedRanges:
        """
        Create a NamedRanges instance from a dictionary.

        Parameters
        ----------
        ranges_dict : Dict[str, Union[Tuple, Range]]
            A dictionary where the keys are names of the ranges and the values
            are tuples/list/array or Range objects defining the range.

        Returns
        -------
        NamedRanges
            A new NamedRanges instance.
        """
        result = cls(
            names=[],
            min_values=[],
            max_values=[],
            lbounds = [],
            rbounds = []
        )
        result.update(ranges_dict)
        return result

    @classmethod
    def create(cls, data: Any=None) -> NamedRanges:
        data = data or {}
        if isinstance(data, dict):
            return cls.from_dict(data)
        if isinstance(data, NamedRanges):
            return cls(data.names, data.min_values, data.max_values, data.lbounds, data.rbounds)
        raise TypeError(
            f"Unsupported input type: {type(data)}"
        )

    def to_dict(self, orient: str = "tuple") -> Dict[str, Union[Tuple, Range]]:
        """
        Convert the NamedRanges instance to a dictionary.
    
        Parameters
        ----------
        orient : str, optional
            Specifies the format of the dictionary values. Can be either "tuple" or "range".
            Defaults to "tuple".
    
        Returns
        -------
        Dict[str, Union[Tuple, Range]]
            A dictionary of ranges in the specified format.
        """
        if orient not in {"tuple", "range"}:
            raise ValueError("Invalid orient value. Must be 'tuple' or 'range'.")
    
        if orient == "tuple":
            return {
                name: (min_val, max_val, lbound, rbound)
                for name, min_val, max_val, lbound, rbound in zip(
                    self.names, self.min_values, self.max_values, self.lbounds, self.rbounds
                )
            }
        elif orient == "range":
            return {
                name: Range(min_val, max_val, lbound, rbound)
                for name, min_val, max_val, lbound, rbound in zip(
                    self.names, self.min_values, self.max_values, self.lbounds, self.rbounds
                )
            }

    def select(self, names: Union[str, Sequence[str], np.ndarray]) -> NamedRanges:
        """
        Select specific ranges by names.

        Parameters
        ----------
        names : Union[str, Sequence[str]]
            A string (comma-delimited) or sequence of strings representing the names to select.

        Returns
        -------
        NamedRanges
            A new NamedRanges instance with the selected ranges.
        """
        names = np.asarray(names)
        if len(np.unique(names)) != len(names):
            raise ValueError("Duplicate names are not allowed in select.")
        return self.__getitem__(names)

    def delete(self, name: str) -> None:
        """
        Delete a range with the specified name.

        Parameters
        ----------
        name : str
            The name of the range to delete.

        Raises
        ------
        KeyError
            If the name is not found.
        """
        if name not in self._name_to_index:
            raise KeyError(f"range with name '{name}' not found.")
        index = self._name_to_index[name]
        super().delete(index)
        self.names = np.delete(self.names, index)
        self._name_to_index = {name: idx for idx, name in enumerate(self.names)}

    def pop(self, name: str) -> Range:
        """
        Remove and return the range with the specified name.

        Parameters
        ----------
        name : str
            The name of the range to pop.

        Returns
        -------
        Range
            The removed range.

        Raises
        ------
        KeyError
            If the name is not found.

        Examples
        --------
        >>> nr = NamedRanges(["a", "b"], [1, 3], [2, 4])
        >>> nr.pop("a")
        Range(min=1, max=2, lbound=True, rbound=True)
        >>> nr.to_dict()
        {'b': (3, 4, True, True)}
        """
        range_obj = self[name]
        self.delete(name)
        return range_obj

    def update(self, ranges_dict: Dict[str, Union[Tuple, List, np.ndarray, Range]]) -> None:
        """
        Update or add ranges based on the provided dictionary.

        Parameters
        ----------
        ranges_dict : Dict[str, Union[Tuple, Range]]
            A dictionary where the keys are names of the ranges and the values
            are tuples or Range objects defining the range.

        Raises
        ------
        ValueError
            If the input ranges are invalid or if duplicate names are provided.

        Examples
        --------
        >>> nr = NamedRanges(["a"], [1], [2])
        >>> nr.update({"b": (3, 4), "a": (0, 1)})
        >>> nr.to_dict()
        {'a': (0, 1, True, True), 'b': (3, 4, True, True)}
        """
        if not ranges_dict:
            return

        if len(ranges_dict) != len(set(ranges_dict)):
            raise ValueError("Duplicate names found in input.")

        names = []
        min_values = []
        max_values = []
        lbounds = []
        rbounds = []
        for name, range_obj in ranges_dict.items():
            min_val, max_val, lbound, rbound = parse_range(range_obj)

            if name in self._name_to_index:
                index = self._name_to_index[name]
                self.min_values[index] = min_val
                self.max_values[index] = max_val
                self.lbounds[index] = lbound
                self.rbounds[index] = rbound
            else:
                names.append(name)
                min_values.append(min_val)
                max_values.append(max_val)
                lbounds.append(lbound)
                rbounds.append(rbound)

        if names:
            self.names = np.append(self.names, names)
            self.min_values = np.append(self.min_values, min_values)
            self.max_values = np.append(self.max_values, max_values)
            self.lbounds = np.append(self.lbounds, lbounds)
            self.rbounds = np.append(self.rbounds, rbounds)
            self._name_to_index = {name: idx for idx, name in enumerate(self.names)}

    def clear(self) -> None:
        """
        Remove all ranges and clear the NamedRanges object.

        Examples
        --------
        >>> nr = NamedRanges(["a", "b"], [1, 3], [2, 4])
        >>> nr.clear()
        >>> nr.to_dict()
        {}
        """
        super().clear()
        self.names = np.array([], dtype=str)
        self._name_to_index = {}

    def append(self, range_obj: Union[Tuple, Range]) -> None:
        """
        Overridden append method to prevent appending to NamedRanges.

        Raises
        ------
        NotImplementedError
            Always raised to indicate the method is not supported.

        Examples
        --------
        >>> nr = NamedRanges(["a"], [1], [2])
        >>> nr.append((3, 4))
        Traceback (most recent call last):
            ...
        NotImplementedError: `append` is not supported for NamedRanges. Use `update` instead.
        """
        raise NotImplementedError("`append` is not supported for NamedRanges. Use `update` instead.")