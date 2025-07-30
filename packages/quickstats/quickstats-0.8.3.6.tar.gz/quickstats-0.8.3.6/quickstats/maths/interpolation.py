from typing import Optional, Union, Dict, Any, List, Tuple
import numpy as np

def get_intervals(
    x: np.ndarray,
    y: np.ndarray,
    level: float,
    delta: float = 0.0001
) -> np.ndarray:
    """
    Find the intervals where y(x) is above (or below) a given `level`.

    Parameters
    ----------
    x : np.ndarray
        1D array of x-values.
    y : np.ndarray
        1D array of y-values corresponding to x.
    level : float
        The reference value to find where y crosses this level.
    delta : float, optional
        The step size for interpolation, by default 0.0001.

    Returns
    -------
    np.ndarray
        A 2D array of shape (n, 2) giving the intervals (start, end)
        where y crosses the given level, or np.inf boundaries if it extends.
        May return an empty array if no intersections exist.
    """
    
    from scipy.interpolate import interp1d
    
    sort_idx = np.argsort(x)
    x = x[sort_idx]
    y = y[sort_idx]
    
    func_interp = interp1d(x, y, fill_value="extrapolate")
    x_interp = np.arange(min(x), max(x), delta)
    y_interp = func_interp(x_interp)
    
    mask = np.argwhere(~np.isnan(y_interp))
    x_interp = x_interp[mask].ravel()
    y_interp = y_interp[mask].ravel()
    
    asign = np.sign(y_interp - level)

    for i in range(1, len(asign)):
        if asign[i] == 0:
            asign[i] = - asign[i - 1]

    sign_change = (np.roll(asign, 1) - asign) != 0
    sign_change[0] = False
    
    intersections = x_interp[sign_change]
    sign_slope = asign[sign_change]

    if len(intersections) == 0:
        return np.array([])
    if len(intersections) == 1:
        if sign_slope[0] == -1:
            return np.array([[intersections[0], np.inf]])
        return np.array([[-np.inf, intersections[0]]])
    if sign_slope[0] == 1:
        intersections = np.insert(intersections, 0, -np.inf)
    if sign_slope[-1] == -1:
        intersections = np.insert(intersections, len(intersections), np.inf)
    if len(intersections) % 2 == 1:
        raise RuntimeError("number of intersections can not be odd")

    return intersections.reshape(len(intersections) // 2, 2)

def get_regular_meshgrid(*xi: np.ndarray, n: int) -> List[np.ndarray]:
    """
    Generate a regular meshgrid over the given 1D arrays.

    Parameters
    ----------
    *xi : np.ndarray
        One or more arrays of data. For each array, the min and max are used.
    n : int
        Number of points in the meshgrid along each dimension.

    Returns
    -------
    List[np.ndarray]
        A list of mesh arrays for each dimension (as returned by np.meshgrid).
    """
    reg_xi = [np.linspace(np.min(arr), np.max(arr), n) for arr in xi]
    return np.meshgrid(*reg_xi)


def get_x_intersections(
    x1: np.ndarray,
    y1: np.ndarray,
    x2: np.ndarray,
    y2: np.ndarray
) -> List[float]:
    """
    Return the x-values where the curves (x1, y1) and (x2, y2) intersect.

    Parameters
    ----------
    x1, y1 : np.ndarray
        1D arrays defining the first curve.
    x2, y2 : np.ndarray
        1D arrays defining the second curve.

    Returns
    -------
    List[float]
        A list of x-values where the curves intersect.
    """
    interp_y1 = np.interp(x2, x1, y1)
    diff = interp_y1 - y2

    idx = np.argwhere(np.diff(np.sign(diff))).flatten()
    intersections = [
        x2[i] - (x2[i + 1] - x2[i]) / (diff[i + 1] - diff[i]) * diff[i]
        for i in idx
    ]
    return np.unique(intersections)


def get_roots(
    x: np.ndarray,
    y: np.ndarray,
    y_ref: float = 0.0,
    delta: Optional[float] = None
) -> np.ndarray:
    """
    Find x-values where y crosses y_ref, given discrete (x, y) data.

    Parameters
    ----------
    x : np.ndarray
        1D array of x-values.
    y : np.ndarray
        1D array of y-values.
    y_ref : float, optional
        The reference level, by default 0.0
    delta : float, optional
        If given, create a finer grid with spacing delta for interpolation.

    Returns
    -------
    np.ndarray
        Array of x-values where y crosses y_ref.
    """
    x, y = np.asarray(x), np.asarray(y)
    sort_idx = np.argsort(x)
    x, y = x[sort_idx], y[sort_idx]

    if delta is None:
        x_interp, y_interp = x, y
    else:
        x_interp = np.arange(x.min(), x.max(), delta)
        y_interp = np.interp(x_interp, x, y)

    mask = ~np.isnan(y_interp)
    x_interp, y_interp = x_interp[mask], y_interp[mask]

    rel_sign = np.sign(y_interp - y_ref)
    sign_change = (np.roll(rel_sign, 1) - rel_sign) != 0

    sign_change[0] = False

    return x_interp[sign_change]


def get_minimum_1d(
    x: np.ndarray,
    y: np.ndarray,
    kind: str = 'cubic',
    axis: int = -1,
    **kwargs
) -> Tuple[float, float]:
    """
    Find the minimum of an interpolated 1D function defined by (x, y).

    Parameters
    ----------
    x : np.ndarray
        1D array of x-values.
    y : np.ndarray
        1D array of y-values.
    kind : str, optional
        Interpolation kind, by default 'cubic'.
    axis : int, optional
        Axis along which y is assumed, by default -1.
    **kwargs:
        Additional arguments passed to interp1d.

    Returns
    -------
    (float, float)
        The (x, y) coordinates of the minimum found by bounded search
        over [x.min(), x.max()].
    """
    from scipy.interpolate import interp1d
    from scipy.optimize import minimize_scalar

    x = np.asarray(x)
    y = np.asarray(y)

    if x.ndim != 1:
        raise ValueError("`x` must be a 1D array.")

    func = interp1d(x, y, kind=kind, axis=axis, **kwargs)
    result = minimize_scalar(func, bounds=(x.min(), x.max()), method='bounded')

    if not result.success:
        raise RuntimeError("Minimization did not converge successfully.")

    return result.x, result.fun


def get_intervals_between_curves(
    x1: np.ndarray,
    y1: np.ndarray,
    x2: np.ndarray,
    y2: np.ndarray
) -> Union[np.ndarray, List[float]]:
    """
    Get the intersection intervals between two 1D curves (x1, y1) and (x2, y2).

    Parameters
    ----------
    x1, y1 : np.ndarray
        First curve data.
    x2, y2 : np.ndarray
        Second curve data.

    Returns
    -------
    np.ndarray or List[float]
        If there are no intersections, returns an empty array.
        If there is exactly one intersection, returns a 2-element array
        with -inf or +inf on one side.
        If there are exactly two intersections, returns them as [x_left, x_right].
        Otherwise, raises RuntimeError.
    """
    interp_y1 = np.interp(x2, x1, y1)
    diff = interp_y1 - y2
    sc = np.diff(np.sign(diff))

    idx = np.argwhere(sc).flatten()
    intersections = np.array([
        x2[i] - (x2[i + 1] - x2[i]) / (diff[i + 1] - diff[i]) * diff[i]
        for i in idx
    ])

    if len(intersections) == 0:
        # No intersection
        return np.array([])
    elif len(intersections) == 1:
        # One intersection
        sign = sc[idx[0]]
        if sign < 0:
            return np.array([-np.inf, intersections[0]])
        return np.array([intersections[0], np.inf])
    elif len(intersections) == 2:
        # Exactly two intersections
        if (sc[idx[0]] + sc[idx[1]]) != 0:
            raise RuntimeError("Found discontinuous curves.")
        return intersections
    else:
        raise RuntimeError("Found multiple intervals. Unexpected behavior.")


def interpolate_2d(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    method: str = 'cubic',
    n: int = 500
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Interpolate scattered 2D data (x, y, z) onto a regular grid.

    Parameters
    ----------
    x : np.ndarray
        1D array of x-values.
    y : np.ndarray
        1D array of y-values.
    z : np.ndarray
        1D array of z-values at (x, y).
    method : str, optional
        Interpolation method for scipy.interpolate.griddata, by default 'cubic'.
    n : int, optional
        Number of points along each dimension in the output grid, by default 500.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        The regular mesh X, Y, and the interpolated Z on that grid.
    """
    from scipy import interpolate

    mask = ~np.isnan(z)
    x, y, z = x[mask], y[mask], z[mask]

    X, Y = get_regular_meshgrid(x, y, n=n)
    XY = np.stack((x, y), axis=1)
    Z = interpolate.griddata(XY, z, (X, Y), method=method)
    return X, Y, Z


# ------------------ Piecewise Functions ------------------ #

def additive_piecewise_linear(
    x: Union[float, np.ndarray],
    nominal: float,
    low: float,
    high: float,
    boundary: Optional[float] = None,
    res: Optional[float] = None
) -> Union[float, np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    mod = np.where(x > 0, x * (high - nominal), x * (nominal - low))
    return mod


def multiplicative_piecewise_exponential(
    x: Union[float, np.ndarray],
    nominal: float,
    low: float,
    high: float,
    boundary: Optional[float] = None,
    res: Optional[float] = None
) -> Union[float, np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    res = nominal if res is None else res
    mod = np.where(
        x >= 0,
        res * (np.power(high / nominal, x) - 1),
        res * (np.power(low / nominal, -x) - 1),
    )
    return mod


def additive_quadratic_linear_extrapolation(
    x: Union[float, np.ndarray],
    nominal: float,
    low: float,
    high: float,
    boundary: float,
    res: Optional[float] = None
) -> Union[float, np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    a = 0.5 * (high + low) - nominal
    b = 0.5 * (high - low)
    mod = np.where(
        x > 1,
        (2 * a + b) * (x - 1) + (high - nominal),
        np.where(
            x < -1,
            -1 * (2 * a - b) * (x + 1) + (low - nominal),
            a * x**2 + b * x
        )
    )
    return mod


def additive_polynomial_linear_extrapolation(
    x: Union[float, np.ndarray],
    nominal: float,
    low: float,
    high: float,
    boundary: float,
    res: Optional[float] = None
) -> Union[float, np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    mod = np.zeros_like(x)

    mask_hi = x >= boundary
    mask_lo = x <= -boundary
    mask_mid = ~(mask_hi | mask_lo)

    mod[mask_hi] = x[mask_hi] * (high - nominal) / boundary
    mod[mask_lo] = x[mask_lo] * (nominal - low) / boundary

    if np.any(mask_mid):
        t = x[mask_mid] / boundary
        eps_plus = (high - nominal) / boundary
        eps_minus = (nominal - low) / boundary
        S = 0.5 * (eps_plus + eps_minus)
        A = 0.0625 * (eps_plus - eps_minus)
        mod[mask_mid] = x[mask_mid] * (
            S + t * A * (15 + t**2 * (-10 + t**2 * 3))
        )

    return mod


def multiplicative_polynomial_exponential_extrapolation(
    x: Union[float, np.ndarray],
    nominal: float,
    low: float,
    high: float,
    boundary: float,
    res: Optional[float] = None
) -> Union[float, np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    if res is None:
        res = nominal

    mod = np.zeros_like(x)
    mask_hi = x >= boundary
    mask_lo = x <= -boundary
    mask_mid = ~(mask_hi | mask_lo)

    mod[mask_hi] = np.power((high / nominal), x[mask_hi])
    mod[mask_lo] = np.power((low / nominal), -x[mask_lo])

    if np.any(mask_mid):
        x0 = boundary
        high_ = high / nominal
        low_ = low / nominal

        pow_up = high_**(x0)
        pow_down = low_**(x0)
        log_hi = np.log(high_) if high_ > 0 else 0.0
        log_lo = np.log(low_) if low_ > 0 else 0.0

        pow_up_log = pow_up * log_hi
        pow_down_log = -pow_down * log_lo
        pow_up_log2 = pow_up_log * log_hi
        pow_down_log2 = pow_down_log * log_lo

        S0 = 0.5 * (pow_up + pow_down)
        A0 = 0.5 * (pow_up - pow_down)
        S1 = 0.5 * (pow_up_log + pow_down_log)
        A1 = 0.5 * (pow_up_log - pow_down_log)
        S2 = 0.5 * (pow_up_log2 + pow_down_log2)
        A2 = 0.5 * (pow_up_log2 - pow_down_log2)

        t = x[mask_mid]
        a = (15 * A0 - 7 * x0 * S1 + x0**2 * A2) / (8 * x0)
        b = (-24 + 24 * S0 - 9 * x0 * A1 + x0**2 * S2) / (8 * x0**2)
        c = (-5 * A0 + 5 * x0 * S1 - x0**2 * A2) / (4 * x0**3)
        d = (12 - 12 * S0 + 7 * x0 * A1 - x0**2 * S2) / (4 * x0**4)
        e = (3 * A0 - 3 * x0 * S1 + x0**2 * A2) / (8 * x0**5)
        f = (-8 + 8 * S0 - 5 * x0 * A1 + x0**2 * S2) / (8 * x0**6)

        value = 1.0 + t * (
            a + t * (
                b + t * (
                    c + t * (
                        d + t * (
                            e + t * f
                        )
                    )
                )
            )
        )
        mod[mask_mid] = value

    return res * (mod - 1.0)


def multiplicative_polynomial_linear_extrapolation(
    x: Union[float, np.ndarray],
    nominal: float,
    low: float,
    high: float,
    boundary: float,
    res: Optional[float] = None
) -> Union[float, np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    if res is None:
        res = nominal

    mod = np.zeros_like(x)
    high_ = high / nominal
    low_ = low / nominal

    mask_hi = x >= boundary
    mask_lo = x <= -boundary
    mask_mid = ~(mask_hi | mask_lo)

    mod[mask_hi] = x[mask_hi] * (high_ - nominal) / boundary
    mod[mask_lo] = x[mask_lo] * (nominal - low_) / boundary

    if np.any(mask_mid):
        t = x[mask_mid] / boundary
        eps_plus = (high_ - nominal) / boundary
        eps_minus = (nominal - low_) / boundary
        S = 0.5 * (eps_plus + eps_minus)
        A = 0.0625 * (eps_plus - eps_minus)
        mod[mask_mid] = x[mask_mid] * (
            S + t * A * (15.0 + t**2 * (-10.0 + t**2 * 3.0))
        )

    return mod * res


piecewise_interp_func_map: Dict[int, Any] = {
    0: additive_piecewise_linear,
    1: multiplicative_piecewise_exponential,
    2: additive_quadratic_linear_extrapolation,
    4: additive_polynomial_linear_extrapolation,
    5: multiplicative_polynomial_exponential_extrapolation,
    6: multiplicative_polynomial_linear_extrapolation
}


def piecewise_interpolate(
    x: Union[float, np.ndarray],
    nominal: float,
    low: float,
    high: float,
    boundary: float,
    code: int = 4,
    res: Optional[float] = None
) -> Union[float, np.ndarray]:
    """
    Dispatch to one of the piecewise interpolation/extrapolation
    functions according to the 'code' argument.
    """
    func = piecewise_interp_func_map[code]
    return func(x=x, nominal=nominal, low=low, high=high, boundary=boundary, res=res)
