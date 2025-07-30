from typing import Union, Any, List, Dict, Optional, Tuple, Callable
from fractions import Fraction
import decimal
import math
from numbers import Real

import numpy as np

ctx = decimal.Context()
ctx.prec = 20

# taken from https://stackoverflow.com/questions/38847690
def float_to_str(f):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    # fix issues with f being special float types such
    # as np.float64 which does not have numeric proper repr
    f = float(f)
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')

def pretty_float(val:Union[str, float])->Union[int, float]:
    if float(val).is_integer():
        return int(float(val))
    return float(val)

def to_bool(val:Any):
    if not isinstance(val, str):
        return bool(val)
    else:
        if val.isdigit():
            return bool(int(val))
        else:
            if val.lower() == "true":
                return True
            elif val.lower() == "false":
                return False
            else:
                raise ValueError(f"invalid boolean expression: {val}")
                
def to_string(val:Any, precision:int=8) -> str:
    if isinstance(val, float):
        val = round(val, precision)
    return str(val)

def to_rounded_float(val:Any, precision:int=8) -> float:
    return round(float(Fraction(val)), precision)

def pretty_value(val:Union[int, float], precision:int=8)->Union[int, float]:
    if isinstance(val, float):
        val = round(val, precision)
        if val.is_integer():
            return int(val)
    return val

def is_integer(s:str):
    if not s:
        return False
    if len(s) == 1:
        return s.isdigit()
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def is_float(element: Any) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False

def array_swap(arr1:np.ndarray, arr2:np.ndarray, indices):
    arr1[indices], arr2[indices] = arr2[indices], arr1[indices]

def df_array_swap(df, col1:str, col2:str, indices=None):
    if indices is None:
        df.loc[:, col1], df.loc[:, col2] = df[col2], df[col1]
    else:
        df.loc[indices, col1], df.loc[indices, col2] = df[indices][col2], df[indices][col1]
        
def reorder_arrays(*arrays, descending:bool=True):
    if descending:
        if (arrays[0].dtype.type not in [np.string_, np.str_]):
            indices = np.argsort(-arrays[0])
        else:
            indices = np.argsort(arrays[0])[::-1]
    else:
        indices = np.argsort(arrays[0])
    for arr in arrays:
        arr[:] = arr[indices]    

def reverse_arrays(*arrays):
    for arr in arrays:
        arr[:] = arr[::-1] 
        
def ceildiv(a, b):
    return -(-a // b)

def approx_n_digit(val:float, default=5):
    s = str(val)
    if not s.replace('.','',1).isdigit():
        return default
    elif '.' in s:
        return len(s.split('.')[1])
    else:
        return 0

def str_encode_value(val:float, n_digit=None, formatted=True):
    if n_digit is not None:
        val_str = '{{:.{}f}}'.format(n_digit).format(val)
        #if val_str == '-{{:.{}f}}'.format(n_digit).format(0):
        #    val_str = '{{:.{}f}}'.format(n_digit).format(0)
    else:
        val_str = float_to_str(val)
    # edge case of negative zero
    if val_str == '-0.0':
        val_str = '0p0'
    
    if formatted:
        val_str = val_str.replace('.', 'p').replace('-', 'n')
    return val_str

def str_decode_value(val_str):
    val = float(val_str.replace('p','.').replace('n','-'))
    return val

def is_nan_or_inf(value):
    return np.isnan(value) or np.isinf(value)

def get_bins_given_edges(low_edge:float, high_edge:float, nbins:int, decimals:int=8):
    bin_width = (high_edge - low_edge) / nbins
    low_bin_center  = low_edge + bin_width / 2
    high_bin_center = high_edge - bin_width /2
    bins = np.around(np.linspace(low_bin_center, high_bin_center, nbins), decimals)
    return bins

def array_issubset(a:np.ndarray, b:np.ndarray):
    """
    Check if array b is a subset of array a
    """
    a = np.unique(a)
    b = np.unique(b)
    c = np.intersect1d(a, b)
    return c.size == b.size

def get_proper_ranges(ranges:Union[List[float], List[List[float]]],
                      reference_value:Optional[float]=None,
                      no_overlap:bool=True):
    try:
        ranges = np.array(ranges)
    except Exception:
        ranges = None
        
    if (ranges is None) or ranges.dtype == np.dtype('O'):
        raise ValueError("invalid range format")
    # single interval
    if ranges.ndim == 1:
        if ranges.shape == (2,):
            ranges = ranges.reshape([1, 2])
        else:
            raise ValueError("range must be array of size 2")
    if ranges.ndim != 2:
        raise ValueError("ranges must be a 2 dimensional array")
    if ranges.shape[1] != 2:
        raise ValueError("individual range must be array of size 2")
        
    ranges = ranges[ranges[:,0].argsort()]
    
    if not np.all(ranges[:, 0] <= ranges[:, 1]):
        raise ValueError("minimum range can not be greater than maximum range")
    if reference_value is not None:
        if not np.all(ranges[:, 0] <= reference_value):
            raise ValueError("minimum range is greater than the nominal value")
        if not np.all(ranges[:, 1] >= reference_value):
            raise ValueError("maximum range is smaller than the nominal value")
    if no_overlap:
        if not np.all(np.diff(ranges.flatten()) >= 0):
            raise ValueError("found overlap ranges")
    return ranges

def get_rmin_rmax(range:Tuple[float], require_finite:bool=True):
    try:
        rmin, rmax = range
    except Exception:
        raise RuntimeError('range must be convertible to a 2-tuple of the form (rmin, rmax)')
    if rmin > rmax:
        raise ValueError('max range must be larger than min range')
    if require_finite and (not (np.isfinite(rmin) and np.isfinite(rmax))):
        raise ValueError(f'supplied range of [{rmin}, {rmax}] is not finite')
    return rmin, rmax

def get_batch_slice_indices(totalsize: int, batchsize: int, drop_remainder: bool = False):
    """
    Generates start and end indices for batch slicing.

    Parameters
    ----------
    totalsize : int
        Total size of the data.
    batchsize : int
        Size of each batch.
    drop_remainder : bool, optional
        Whether to drop the last batch if it is smaller than the batch size.

    Yields
    ------
    tuple of int
        Start and end indices for each batch.
    """
    if not ((totalsize > 0) and (batchsize > 0)):
        raise ValueError("Total size and batch size must be greater than zero")
    for i in range(0, totalsize, batchsize):
        end = min(i + batchsize, totalsize)
        if drop_remainder and (end - i) < batchsize:
            break
        yield (i, min(i + batchsize, totalsize))

def get_split_sizes(totalsize:int, nsplits: int):
    split_sizes = np.full(nsplits, totalsize // nsplits, dtype=int)
    split_sizes[: totalsize % nsplits] += 1
    return split_sizes

def get_split_slice_indices(totalsize: int, nsplits: int):
    """
    Generates start and end indices for splitting.

    Parameters
    ----------
    totalsize : int
        Total size of the data.
    nsplits : int
        Number of splits.

    Yields
    ------
    tuple of int
        Start and end indices for each split.
    """
    if not ((totalsize > 0) and (nsplits > 0)):
        raise ValueError("Total size and number of partitions must be greater than zero")
    split_sizes = get_split_sizes(totalsize, nsplits)
    
    start_idx = 0
    for size in split_sizes:
        end_idx = start_idx + size
        yield (start_idx, end_idx)
        start_idx = end_idx
        
def get_nbatch(totalsize: int, batchsize: int) -> int:
    """
    Calculate the number of batches needed to cover the total size with the given batch size.

    Parameters
    ----------
    totalsize : int
        Total size of the data.
    batchsize : int
        Size of each batch.

    Returns
    -------
    int
        The number of batches required to cover the total size.
    """
    if totalsize <= 0:
        raise ValueError("Total size must be greater than zero.")
    if batchsize <= 0:
        raise ValueError("Batch size must be greater than zero.")
    
    return math.ceil(totalsize / batchsize)
        
def safe_div(dividend, divisor, usenan:bool=False):
    out = np.full(dividend.shape, np.nan) if usenan else np.zeros_like(dividend)
    return np.divide(dividend, divisor, out=out, where=divisor!=0)

# taken from https://stackoverflow.com/questions/11144513/
def cartesian_product(*arrays):
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[..., i] = a
    return arr.reshape(-1, la)

def get_subsequences(arr, mask, min_length=1):
    """
    Finds and returns continuous subsequences of an array where the mask is True.
    
    Parameters:
    - arr (np.array): The array from which to extract subsequences.
    - mask (np.array): A boolean array where True indicates the elements of `arr` to consider for forming subsequences.
    - min_length (int): The minimum length of the subsequence to be returned. Default is 2.
    
    Returns:
    - list of np.array: A list containing the subsequences from `arr` that meet the criteria of continuous True values in `mask` and are at least `min_length` elements long.
    
    Example:
    >>> arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    >>> mask = np.array([False, True, True, False, False, True, True, True, False, True])
    >>> get_subsequences(arr, mask, min_length=3)
    [array([6, 7, 8])]
    """
    
    # Ensure mask is a boolean array
    mask = np.asarray(mask, dtype=bool)
    
    # Calculate changes in the mask
    changes = np.diff(mask.astype(int))
    # Identify where sequences start (False to True transition)
    start_indices = np.where(changes == 1)[0] + 1
    # Identify where sequences end (True to False transition)
    end_indices = np.where(changes == -1)[0] + 1
    
    # Handle case where mask starts with True
    if mask[0]:
        start_indices = np.insert(start_indices, 0, 0)
    # Handle case where mask ends with True
    if mask[-1]:
        end_indices = np.append(end_indices, len(mask))
    
    # Gather and return sequences that meet the minimum length requirement
    sequences = [arr[start:end] for start, end in zip(start_indices, end_indices) if end - start >= min_length]
    
    return sequences


def get_max_sizes_from_fraction(size1: int, size2: int, fraction: float) -> Tuple[int, int]:
    """
    Calculate the maximum size from each sample such that their total size 
    is distributed according to the given fraction.

    Args:
        size1 (int): Size of the first sample.
        size2 (int): Size of the second sample.
        fraction (float): Desired fraction of the total size to be assigned to size1.

    Returns:
        Tuple[int, int]: Maximum sizes from each sample that maintain the desired fraction.
    """

    if size1 <= 0 or size2 <= 0:
        raise ValueError("sizes must be positive integers.")
    if not (0 <= fraction <= 1):
        raise ValueError("fraction must be a number between 0 and 1.")

    total_size = size1 + size2
    
    max_size1 = int(total_size * fraction)
    max_size2 = total_size - max_size1
    
    if max_size1 > size1:
        max_size1 = size1
        max_size2 = int(size1 * (1 - fraction) / fraction)
    elif max_size2 > size2:
        max_size2 = size2
        max_size1 = int(size2 * fraction / (1 - fraction))
    
    return max_size1, max_size2

def sliced_sum(data: np.ndarray, slices: np.ndarray) -> np.ndarray:
    return np.add.reduceat(np.pad(data, (0, 1)), slices.flatten())[::2]

def all_integers(data: np.ndarray):
    fractional_part, _ = np.modf(data)
    return np.all(fractional_part == 0)

def is_integer(x: Real) -> bool:
    """
    Check if a real value is an integer.

    Parameters
    ----------
    x : Real
        A real number that can be of type int, float, np.float32, np.int32, np.uint32, etc.

    Returns
    -------
    bool
        True if the value represents an integer (i.e., has no fractional part), otherwise False.

    Examples
    --------
    >>> is_integer(5)
    True

    >>> is_integer(5.0)
    True

    >>> is_integer(3.14)
    False

    >>> import numpy as np
    >>> is_integer(np.float32(7))
    True

    >>> is_integer(np.uint32(10))
    True
    """
    return x == int(x)

def min_max_to_range(min_val:Optional[float]=None, max_val:Optional[float]=None):
    if (min_val is None) and (max_val is None):
        return None
    if (min_val is not None) and (max_val is not None):
        return (min_val, max_val)
    raise ValueError("min and max values must be all None or all float")

def pivot_table(x: np.ndarray, y: np.ndarray, z: np.ndarray, missing: Any = np.nan) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Creates a pivot table from x, y, and z arrays by aggregating z values 
    based on the unique pairs of x and y coordinates.

    Parameters
    ----------
    x : np.ndarray
        1D array of x coordinates (row labels). Duplicates are allowed.
    y : np.ndarray
        1D array of y coordinates (column labels). Duplicates are allowed.
    z : np.ndarray
        1D array of values associated with each (x, y) pair.
    missing : Any, optional
        The value to use for missing entries in the pivot table, by default np.nan.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        A tuple containing:
        - `X`: A 2D array where rows correspond to unique sorted values of `x`.
        - `Y`: A 2D array where columns correspond to unique sorted values of `y`.
        - `Z`: A 2D array (pivot table) where values are taken from `z`.
               If there are no values for certain (x, y) pairs, the cell will be filled with `missing`.

    Raises
    ------
    ValueError
        If the lengths of `x`, `y`, and `z` do not match.
    
    Examples
    --------
    >>> x = np.array([1, 2, 1, 2])
    >>> y = np.array(['A', 'B', 'A', 'B'])
    >>> z = np.array([10, 20, 30, 40])
    >>> X, Y, Z = pivot_table(x, y, z)
    >>> Z
    array([[10., 20.],
           [30., 40.]])
    """
    if len(x) != len(y) or len(y) != len(z):
        raise ValueError("x, y, and z must have the same size")

    X_unique, X_inv = np.unique(x, return_inverse=True)
    Y_unique, Y_inv = np.unique(y, return_inverse=True)
    X, Y = np.meshgrid(X_unique, Y_unique)

    Z = np.full((X_unique.size, Y_unique.size), missing)
    Z[X_inv, Y_inv] = z
    
    return X, Y, Z

def get_nan_shapes(x: np.ndarray, y: np.ndarray, z: np.ndarray, alpha: float = 0.) -> List["Polygon"]:
    """
    Generates alpha shapes (concave hulls) for points where `z` is NaN, using the provided `x` and `y` coordinates.

    Parameters
    ----------
    x : np.ndarray
        1D array of x coordinates.
    y : np.ndarray
        1D array of y coordinates.
    z : np.ndarray
        1D array of values associated with the (x, y) points. NaN values indicate where the shape should be generated.
    alpha : float, optional
        Alpha parameter for the alpha shape algorithm. Smaller values create more detailed shapes, by default 0.

    Returns
    -------
    List[Polygon]
        A list of Shapely Polygon objects representing the alpha shapes of the regions where `z` is NaN.
        If only one shape is generated, it will still be returned as a list.

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4])
    >>> y = np.array([1, 2, 3, 4])
    >>> z = np.array([1, np.nan, np.nan, 4])
    >>> shapes = get_nan_shapes(x, y, z)
    >>> len(shapes)
    1
    """
    from alphashape import alphashape
    from shapely.geometry import Polygon, MultiPolygon

    # Mask NaN values in z and stack corresponding x and y coordinates
    mask = np.isnan(z)
    xy = np.column_stack((x[mask], y[mask]))

    # Generate the alpha shape for the masked points
    shape = alphashape(xy, alpha=alpha)

    # Return the shape(s) as a list of Polygons
    if isinstance(shape, MultiPolygon):
        return list(shape.geoms)
    elif isinstance(shape, Polygon):
        return [shape]
    else:
        return []

def square_matrix_to_dataframe(array: np.ndarray, labels: list) -> "pd.DataFrame":
    """
    Convert a square numpy array into a labeled DataFrame.

    Parameters
    ----------
    array : np.ndarray
        A square 2D NumPy array of shape (N, N) representing a square matrix.
    labels : list
        A list of labels to use for the rows and columns of the DataFrame.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame representing the square matrix with labeled rows and columns.
    """
    if array.shape[0] != array.shape[1]:
        raise ValueError("Input array must be square (shape (N, N)).")

    if len(labels) != array.shape[0]:
        raise ValueError("Number of labels must match the dimensions of the array.")
    import pandas as pd
    return pd.DataFrame(array, index=labels, columns=labels)

def generate_symmetric_positive_definite_matrix(n):
    """
    Generate a random symmetric positive definite matrix of size n x n.
    
    Parameters
    ----------
    n : int
        The size of the matrix.
        
    Returns
    -------
    C : numpy.ndarray
        A symmetric positive definite matrix of size n x n.
    """
    # Generate a random matrix
    A = np.random.rand(n, n)
    
    # Make the matrix symmetric
    A_symmetric = (A + A.T) / 2
    
    # Add n * I to ensure positive definiteness
    C = A_symmetric + n * np.eye(n)
    
    return C


def round_to_significant(number, significant_digits=2, direction='nearest'):
    """
    Round a number to a specified number of significant digits.
    
    Parameters:
    number (float): The number to round
    significant_digits (int): Number of significant digits to keep
    direction (str): Direction to round ('up', 'down', or 'nearest')
    
    Returns:
    float: Rounded number
    """
    import math
    
    if number == 0:
        return 0
    
    # Determine the scale factor
    magnitude = math.floor(math.log10(abs(number)))
    scale = 10 ** (magnitude - significant_digits + 1)
    
    # Perform the rounding based on the direction
    if direction == 'up':
        return math.ceil(number / scale) * scale
    elif direction == 'down':
        return math.floor(number / scale) * scale
    else:  # 'nearest' as default
        return round(number / scale) * scale