from typing import Union, Optional, List, Dict, Tuple, Sequence, Callable

import math
import numpy as np

from .numerics import array_issubset, safe_div
from quickstats import DescriptiveEnum
from quickstats import module_exists, cached_import
from quickstats.core.typing import Numeric, Real, ArrayLike

class BinErrorMode(DescriptiveEnum):
    AUTO    = (0, "Determine bin error method from data weights")
    SUMW2   = (1, "Errors with Wald approximation: sqrt(sum of weight^2)")
    POISSON = (2, "Errors from Poisson interval at 68.3% (1 sigma)")
    
class HistComparisonMode(DescriptiveEnum):
    RATIO      = (0, "Ratio of data (target / reference)")
    DIFFERENCE = (1, "Difference of data (target - reference)")

def calculate_nll(obs:float, exp:float):
    import ROOT
    return np.log(ROOT.TMath.Poisson(obs, exp))

def calculate_chi2(data_obs, data_exp, error_obs=None, threshold:float=3, epsilon:float=1e-6):
    if np.any(data_obs < 0):
        raise RuntimeError("data observed has negative-value element(s)")
    if np.any(data_exp < 0):
        raise RuntimeError("data expected has negative-value element(s)")        
    if error_obs is None:
        error_obs = np.sqrt(data_obs)
    data_obs = np.array(data_obs, dtype=np.float64)
    data_exp = np.array(data_exp, dtype=np.float64)
    error_obs = np.array(error_obs, dtype=np.float64)
    if data_obs.shape != data_exp.shape:
        raise RuntimeError("data observed and data expected have different shapes")
    if data_obs.shape != error_obs.shape:
        raise RuntimeError("data observed and error observed have different shapes")
    if data_obs.ndim != 1:
        raise RuntimeError("only one dimensional data is supported")
    chi2, chi2_last, obs_aggregate, exp_aggregate, error2_aggregate = 0., 0., 0., 0., 0.
    nbin_chi2 = 0
    bin_last = 1
    nbins = len(data_obs)
    for i in range(nbins):
        obs_aggregate += data_obs[i]
        exp_aggregate += data_exp[i]
        error2_aggregate += error_obs[i] ** 2
        if (obs_aggregate / np.sqrt(error2_aggregate) < threshold) or \
           (abs(obs_aggregate) < epsilon):
            if i != (nbins - 1):
                continue
            else:
                chi2 -= chi2_last
                obs_aggregate = np.sum(data_obs[bin_last:])
                exp_aggregate = np.sum(data_exp[bin_last:])
                error2_aggregate = np.sum(error_obs[bin_last:] ** 2)
                chi2 += ((obs_aggregate - exp_aggregate) / np.sqrt(error2_aggregate)) ** 2
                if nbin_chi2 == 0:
                    nbin_chi2 += 1
        else:
            chi2_last = ((obs_aggregate - exp_aggregate) / np.sqrt(error2_aggregate)) ** 2
            bin_last = i
            chi2 += chi2_last
            nbin_chi2 += 1
            obs_aggregate, exp_aggregate, error2_aggregate = 0., 0., 0.
    # calculate likelihood
    nll, nll_last, nll_sat, nll_sat_last = 0., 0., 0., 0.
    obs_aggregate, exp_aggregate = 0., 0.
    nbin_nll = 0
    bin_last = 0
    for i in range(nbins):
        obs_aggregate += data_obs[i]
        exp_aggregate += data_exp[i]
        error2_aggregate += error_obs[i] ** 2
        if (obs_aggregate < 2):
            if i != (nbins - 1):
                continue
            else:
                nll -= nll_last
                nll_sat -= nll_sat_last
                obs_aggregate = np.sum(data_obs[bin_last:])
                exp_aggregate = np.sum(data_exp[bin_last:])
                nll += -1 * self.calculate_nll(obs_aggregate, exp_aggregate)
                # saturated
                nll_sat += -1 * self.calculate_nll(obs_aggregate, obs_aggregate)
                if nbin_nll == 0:
                    nbin_nll += 1
        else:
            nll_last = -1 * self.calculate_nll(obs_aggregate, exp_aggregate)
            nll_sat_last = -1 * self.calculate_nll(obs_aggregate, obs_aggregate)
            nll += nll_last
            nll_sat += nll_sat_last
            bin_last = i
            nbin_nll += 1
            obs_aggregate, exp_aggregate = 0., 0.
    result = {
        'chi2': chi2,
        'nbin_chi2': nbin_chi2,
        'nll': nll,
        'nll_sat': nll_sat,
        'nbin_nll': nbin_nll
    }
    return result

def chi2_to_pvalue(chi2_values: ArrayLike, k: int = 1) -> np.ndarray:
    chi2_values = np.asarray(chi2_values)
    
    if module_exists('scipy'):
        import scipy.special
        a = k / 2
        x = chi2_values / 2
        P = scipy.special.gammainc(a, x)
        return 1 - P
    
    ROOT = cached_import('ROOT')
    if np.ndim(chi2_values) == 0:
        return ROOT.TMath.Prob(chi2_values, k)
    return np.array([ROOT.TMath.Prob(chi2, k) for chi2 in chi2_values])

def pvalue_to_significance(pvalues: ArrayLike) -> np.ndarray:
    """
    Converts an array of p-values into significance values (Z-scores).

    The function attempts to use `scipy` if available. If `scipy` is not 
    available, it falls back on `ROOT` to compute the significance.

    Parameters
    ----------
    pvalues : ArrayLike
        Array-like object of p-values to convert into significance.

    Returns
    -------
    np.ndarray
        Array of significance values corresponding to the input p-values.
    
    Examples
    --------
    >>> pvalue_to_significance([0.05, 0.01])
    array([1.64485363, 2.32634787])
    """
    pvalues = np.asarray(pvalues)
    
    if module_exists('scipy'):
        import scipy.stats
        return scipy.stats.norm.isf(pvalues)
    
    ROOT = cached_import('ROOT')
    if np.ndim(pvalues) == 0:
        return ROOT.TMath.PValueToSignificance(pvalues)
    return np.array([ROOT.RooStats.PValueToSignificance(pvalue) for pvalue in pvalues])

def significance_to_pvalue(significances: ArrayLike) -> np.ndarray:
    """
    Converts an array of significance values (Z-scores) into p-values.

    The function attempts to use `scipy` if available. If `scipy` is not
    available, it falls back on `ROOT` to compute the p-values.

    Parameters
    ----------
    significances : ArrayLike
        Array-like object of significance values to convert into p-values.

    Returns
    -------
    np.ndarray
        Array of p-values corresponding to the input significance values.
    
    Examples
    --------
    >>> significance_to_pvalue([1.96, 2.33])
    array([0.0249979 , 0.00990308])
    """
    significances = np.asarray(significances)
    
    if module_exists('scipy'):
        import scipy.stats
        return scipy.stats.norm.sf(significances)
    
    ROOT = cached_import('ROOT')
    if np.ndim(significances) == 0:
        return 1 - ROOT.Math.normal_cdf(significances, 1, 0)
    return np.array([1 - ROOT.Math.normal_cdf(significance, 1, 0) for significance in significances])

def sigma_to_confidence_level(nsigma: float) -> float:
    """
    Convert a number of standard deviations (sigma) to a confidence level.

    This function computes the confidence level associated with a given number of 
    standard deviations (sigma) assuming a normal (Gaussian) distribution. The 
    confidence level is the cumulative probability within ±`nsigma` of the mean.

    Parameters
    ----------
    nsigma : float
        The number of standard deviations (sigma) to compute the confidence level for.

    Returns
    -------
    float
        The confidence level corresponding to the given number of sigmas. This will be 
        a value between 0 and 1 representing the probability that a measurement falls 
        within the interval defined by `nsigma` standard deviations.

    Examples
    --------
    Convert 1-sigma to a confidence level:

    >>> sigma_to_confidence_level(1)
    0.6826894921370859

    Convert 2-sigma to a confidence level:

    >>> sigma_to_confidence_level(2)
    0.9544997361036416

    """
    if module_exists('scipy'):
        import scipy.special
        return scipy.special.erf(nsigma / np.sqrt(2.))
    ROOT = cached_import('ROOT')
    return ROOT.Math.erf(nsigma / np.sqrt(2.0))

def confidence_level_to_chi2(q: float, k: int = 1) -> float:
    """
    Calculate a confidence level to a chi-squared value.
    
    Parameters
    ----------
    q : float
        Confidence level (quantile).
    k : int
        Degrees of freedom of the chi-squared distribution
    
    Returns
    -------
    float
        The chi-squared value at the given confidence level.
    """
    if module_exists('scipy'):
        import scipy.stats
        chi2 = scipy.stats.chi2.ppf(q, df=k)
    else:
        ROOT = cached_import('ROOT')
        chi2 = ROOT.Math.chisquared_quantile(q, k)
    return np.round(chi2, 8)

def sigma_to_chi2(nsigma: float, k: int = 1) -> float:
    """
    Calculate a number of standard deviation to a chi-squared value.
    
    Parameters
    ----------
    nsigma : float
         The number of standard deviations (sigma) to compute the chi-squared value for.
    k : int
        Degrees of freedom of the chi-squared distribution
    
    Returns
    -------
    float
        The chi-squared value at the given standard deviation.
    """
    q = sigma_to_confidence_level(nsigma)
    return confidence_level_to_chi2(q, k)

def poisson_interval(data: ArrayLike, nsigma: int = 1, offset: bool = True) -> ArrayLike:
    """
    Calculate the Poisson error interval for binned data.

    Parameters
    ----------
    data : ArrayLike
        Array containing the event number in each bin. Must contain non-negative integers.
    nsigma : float, optional
        Number of standard deviations (sigma) to use for the Poisson interval. 
        The default is 1-sigma, corresponding to a 68.27% confidence level.
    offset : bool, optional
        If True, returns intervals centered around the data (i.e., adjusted by subtracting the 
        data value from both the lower and upper bounds). If False, returns the direct Poisson 
        interval without adjustment. Default is True.

    Returns
    -------
    lower : ArrayLike
        Array of the lower bounds of the Poisson confidence interval for each bin.
    upper : ArrayLike
        Array of the upper bounds of the Poisson confidence interval for each bin.

    Examples
    --------
    Basic usage with default settings:
    
    >>> data = np.array([10, 20, 30])
    >>> lower, upper = poisson_interval(data)
    >>> lower
    array([3.10869444, 4.43444798, 5.44652246])
    >>> upper
    array([4.26694976, 5.54651923, 6.53804637])

    Specifying a different confidence level (2-sigma):

    >>> lower, upper = poisson_interval(data, nsigma=2)
    >>> lower
    array([5.28076628, 7.9112049 , 9.92675366])
    >>> upper
    array([ 8.57711996, 11.12559528, 13.10339964])

    Without offset:

    >>> lower, upper = poisson_interval(data, offset=False)
    >>> lower
    array([ 6.89130556, 15.56555202, 24.55347754])
    >>> upper
    array([14.26694976, 25.54651923, 36.53804637])

    """
    data = np.asarray(data)
    if module_exists('scipy'):
        data_ = (data + 0.5).astype(int)
        import scipy.stats
        beta = sigma_to_confidence_level(nsigma)
        alpha = (1 - beta)
        lower = scipy.stats.gamma.ppf(alpha / 2., data_)
        upper = scipy.stats.gamma.ppf(1. - alpha / 2., data_ + 1)
        # treatment of Poisson interval for 0 event from https://root-forum.cern.ch/t/what-should-be-the-poisson-interval-of-0-event/60438
        lower[np.isnan(lower)] = 0
        if offset:
            lower = data - lower
            upper = upper - data
        return lower, upper
    # lower = ROOT.Math.gamma_quantile(alpha / 2., data, 1.0)
    # upper = ROOT.Math.gamma_quantile_c(alpha / 2., data + 1, 1.0)
    from quickstats.interface.root import TH1
    return TH1.GetPoissonError(data, nsigma, offset)

def get_counting_significance(s: float, b: float, sigma_b: float = 0.0, leading_order: bool = False) -> float:
    """
    Calculate the median significance for a counting experiment using the Asimov approximation.

    This function computes the significance (Z-value) for a signal and background hypothesis in a counting 
    experiment. The significance quantifies how strongly the observed signal (s) stands out from the background (b),
    considering background uncertainties.

    Parameters
    ----------
    s : float
        Expected number of signal events.
    b : float
        Expected number of background events.
    sigma_b : float, optional, default=0.0
        Uncertainty in the number of background events. A value of 0 indicates that the background is 
        known exactly.
    leading_order : bool, optional, default=False
        If True, use the leading-order approximation for significance.

    Returns
    -------
    float
        The median significance (Z-value) of the signal given the background and its uncertainty.

    Examples
    --------
    Basic calculation with known background (no uncertainty):
    
    >>> get_counting_significance(s=10, b=20)
    2.0803621046562695

    Including background uncertainty:
    
    >>> get_counting_significance(s=10, b=20, sigma_b=5)
    1.3329067287155736

    Using leading-order approximation:
    
    >>> get_counting_significance(s=10, b=20, sigma_b=5, leading_order=True)
    1.4907119849998598

    """
    if sigma_b == 0:
        if leading_order:
            return s / np.sqrt(b)
        n = s + b
        return np.sqrt(2 * ((n * np.log(n / b)) - s))
    else:
        sigma_b2 = sigma_b * sigma_b
        if leading_order:
            return s / np.sqrt(b + sigma_b2)
        n = s + b
        b_plus_sigma2 = b + sigma_b2
        first_term = n * np.log((n * b_plus_sigma2) / (b * b + n * sigma_b2))
        second_term = (b * b / sigma_b2) * np.log(1 + (sigma_b2 * s) / (b * b_plus_sigma2))
        return np.sqrt(2 * (first_term - second_term))


def get_combined_counting_significance(s: np.ndarray, b: np.ndarray,
                                       sigma_b: Union[np.ndarray, float] = 0,
                                       leading_order: bool = False) -> float:
    """
    Calculate the combined significance for multiple independent counting experiments.

    This function computes the combined median significance (Z-value) for a set of 
    independent counting experiments, each with its own expected signal and background 
    events, optionally considering background uncertainties.

    Parameters
    ----------
    s : np.ndarray of float
        Array of expected number of signal events for each experiment.
    b : np.ndarray of float
        Array of expected number of background events for each experiment.
    sigma_b : Union[np.ndarray, float], optional, default=0
        Array of background uncertainties for each experiment. If a single float is provided, 
        it is assumed to apply to all experiments. A value of 0 means the background is known 
        exactly.
    leading_order : bool, optional, default=False
        If True, use the leading-order approximation for the significance calculation.

    Returns
    -------
    float
        The combined significance (Z-value) for the set of independent experiments.

    Examples
    --------
    Basic usage with known background (no uncertainty):

    >>> s = np.array([5, 10, 15])
    >>> b = np.array([10, 20, 30])
    >>> get_combined_counting_significance(s, b)
    3.60329286340558

    Including background uncertainty:

    >>> sigma_b = np.array([1, 2, 3])
    >>> get_combined_counting_significance(s, b, sigma_b=sigma_b)
    3.206386658407043

    Using leading-order approximation:

    >>> get_combined_counting_significance(s, b, sigma_b=sigma_b, leading_order=True)
    3.4940842446376
    """
    if isinstance(sigma_b, Real) and (sigma_b == 0):
        if leading_order:
            Z2 = s * s / b
        else:
            n = s + b
            Z2 = 2 * ((n * np.log(n / b)) - s)
    else:
        sigma_b2 = sigma_b * sigma_b
        if leading_order:
            Z2 = s * s / (b + sigma_b2)
        else:
            n = s + b
            b_plus_sigma2 = b + sigma_b2
            first_term = n * np.log((n * b_plus_sigma2)/(b * b + n * sigma_b2))
            second_term = b * b / sigma_b2 * np.log(1 + (sigma_b2 * s) / (b * b_plus_sigma2))
            Z2 = 2 * (first_term - second_term)
    
    if Z2.ndim > 1:
        Z_combined = np.sqrt(np.sum(Z2, axis=Z2.ndim - 1))
    else:
        Z_combined = np.sqrt(np.sum(Z2))
    
    return Z_combined

def bin_edge_to_bin_center(bin_edges: np.ndarray) -> np.ndarray:
    """
    Calculate bin centers from bin edges.

    Parameters
    ----------
    bin_edges : ArrayLike
        The edges of the bins.

    Returns
    -------
    np.ndarray
        The centers of the bins.
    """
    return (bin_edges[:-1] + bin_edges[1:]) / 2

def bin_center_to_bin_edge(bin_center:np.ndarray):
    bin_widths = np.round(np.diff(bin_center), 8)
    if len(np.unique(bin_widths)) != 1:
        raise ValueError("can not deduce bin edges from bin centers of irregular bin widths")
    bin_width = bin_widths[0]
    bin_edges = np.concatenate([bin_center - bin_width / 2, [bin_center[-1] + bin_width/2]])
    return bin_edges

def bin_edge_to_bin_width(bin_edge:np.ndarray):
    return np.diff(bin_edge)

def min_max_to_range(min_val:Optional[float]=None, max_val:Optional[float]=None):
    if (min_val is None) and (max_val is None):
        return None
    if (min_val is not None) and (max_val is not None):
        return (min_val, max_val)
    raise ValueError("min and max values must be all None or all float")

def get_clipped_data(x: np.ndarray,
                     bin_range: Optional[Sequence] = None,
                     clip_lower: bool = True,
                     clip_upper: bool = True) -> np.ndarray:
    """
    Clip an array of data within a specified range.

    This function clips the values in an array to a specified lower and/or upper bound. 
    If no bounds are provided or if both `clip_lower` and `clip_upper` are set to False, 
    the function returns the original array without modification.

    Parameters
    ----------
    x : np.ndarray
        The data to be clipped.
    bin_range : Optional[Sequence], optional
        A sequence (e.g., tuple or list) of two elements specifying the range `(min, max)` 
        for clipping. If None, no clipping is applied. Default is None.
    clip_lower : bool, optional, default=True
        Whether to apply clipping at the lower bound. If False, the lower bound is not 
        enforced even if `bin_range` is specified.
    clip_upper : bool, optional, default=True
        Whether to apply clipping at the upper bound. If False, the upper bound is not 
        enforced even if `bin_range` is specified.

    Returns
    -------
    np.ndarray
        The clipped array, where values are constrained between the lower and upper bounds 
        if specified and enabled. If no clipping is applied, the original array is returned.

    Examples
    --------
    Basic usage with both lower and upper clipping:

    >>> x = np.array([1, 5, 10, 15, 20])
    >>> get_clipped_data(x, bin_range=(5, 15))
    array([ 5,  5, 10, 15, 15])

    Only apply upper clipping:

    >>> get_clipped_data(x, bin_range=(5, 15), clip_lower=False)
    array([ 1,  5, 10, 15, 15])

    No clipping:

    >>> get_clipped_data(x, bin_range=(5, 15), clip_lower=False, clip_upper=False)
    array([ 1,  5, 10, 15, 20])

    """
    if (bin_range is None) or ((clip_lower == False) and (clip_upper == False)):
        return np.array(x)
    xmin = bin_range[0] if clip_lower else None
    xmax = bin_range[1] if clip_upper else None
    return np.clip(x, xmin, xmax)

def get_histogram_range(range=None,
                        D:int=1):
    # normalize the range argument
    if range is None:
        range = (None,) * D
    elif len(range) != D:
        raise ValueError('range argument must have one entry per dimension')
    return range

def get_histogram_bins(sample,
                       bins=10,
                       bin_range=None,
                       D:int=1):
    try:
        # Sample is an ND-array.
        N, D = sample.shape
    except (AttributeError, ValueError):
        # Sample is a sequence of 1D arrays.
        sample = np.atleast_2d(sample).T
        N, D = sample.shape
    
    nbin = np.empty(D, np.intp)
    edges = D*[None]
    dedges = D*[None]

    try:
        M = len(bins)
        if M != D:
            if (D == 2):
                xedges = yedges = np.asarray(bins)
                bins = [xedges, yedges]
            else:
                raise ValueError(
                    'The dimension of bins must be equal to the dimension of the '
                    'sample x.')
    except TypeError:
        # bins is an integer
        bins = D*[bins]

    bin_range = get_histogram_range(bin_range, D=D)

    import operator
    from numpy.lib.histograms import  _get_outer_edges
    
    # Create edge arrays
    for i in range(D):
        if np.ndim(bins[i]) == 0:
            if bins[i] < 1:
                raise ValueError(
                    f'`bins[{i}]` must be positive, when an integer')
            smin, smax = _get_outer_edges(sample[:,i], bin_range[i])
            try:
                n = operator.index(bins[i])
    
            except TypeError as e:
                raise TypeError(
                    f"`bins[{i}]` must be an integer, when a scalar"
                ) from e
    
            edges[i] = np.linspace(smin, smax, n + 1)
        elif np.ndim(bins[i]) == 1:
            edges[i] = np.asarray(bins[i])
            if np.any(edges[i][:-1] > edges[i][1:]):
                raise ValueError(
                    f'`bins[{i}]` must be monotonically increasing, when an array')
        else:
            raise ValueError(
                f'`bins[{i}]` must be a scalar or 1d array')
    
        nbin[i] = len(edges[i]) + 1  # includes an outlier on each end
        dedges[i] = np.diff(edges[i])
    return edges


def histogram(x:np.ndarray, weights:Optional[np.ndarray]=None,
              bins:Union[int, Sequence]=10,
              bin_range:Optional[Sequence]=None,
              underflow:bool=False,
              overflow:bool=False,
              divide_bin_width:bool=False,
              normalize:bool=True,
              clip_weight:bool=False,
              evaluate_error:bool=False,
              error_mode:Union[BinErrorMode, str]="auto"):
    """
        Compute the histogram of a data array.
        
        Arguments:
        -------------------------------------------------------------------------------
        x: ndarray
            Input data array from which the histogram is computed.
        weights: (optional) ndarray
            Array of weights with same shape as input data. If not given, the
            input data is assumed to have unit weights.
        bins: (optional) int or sequence of scalars, default = 10
            If integer, it defines the number of equal-width bins in the
            given range.
            If sequence, it defines a monotonically increasing array of bin edges,
            including the rightmost edge.
       bin_range: (optional) sequence of the form (float, float)
           The lower and upper range of the bins.  If not provided, range is simply 
           ``(x.min(), x.max())``.  Values outside the range are ignored.
       underflow: bool, default = False
           Include undeflow data in the first bin.
       overflow: bool, default = False
           Include overflow data in the last bin.
       divide_bin_width: bool, default = False
           Divide each bin by the bin width.           
       normalize: bool, default = True
           Normalize the sum of weights to one. Weights outside the bin range will
           not be counted if ``clip_weight`` is set to false, so the sum of bin
           content could be less than one.
       clip_weight: bool, default = False
           Ignore data outside given range when evaluating total weight
           used in normalization.
       evaluate_error: bool, default = True
           Evaluate the error of the bin contents using the given error option.
       error_mode: BinErrorMode or str, default = "auto"
           How to evaluate bin errors. If "sumw2", symmetric errors from the Wald
           approximation is used (square root of sum of squares of weights). If
           "poisson", asymmetric errors from Poisson interval at one sigma is
           used. If "auto", it will use sumw2 error if data has unit weights,
           else Poisson error will be used.
           
       Returns
       -------------------------------------------------------------------------------
       bin_content: np.ndarray
           The bin content of the histogram.
       bin_edges: np.ndarray
           The bin edges of the histogram.
       bin_errors: np.ndarray
           The bin errors of the histogram.
    """
    x = get_clipped_data(x, bin_range=bin_range, clip_lower=underflow,
                         clip_upper=overflow)

    unweighted = weights is None
    if weights is None:
        weights = np.ones(x.shape)
    else:
        # fix overflow bugs
        weights = np.array(weights, dtype=float)
        
    if normalize:
        if clip_weight and (bin_range is not None):
            first_edge, last_edge = bin_range
            norm_factor = weights[(x >= first_edge) & (x <= last_edge)].sum()
        else:
            norm_factor = weights.sum()
    else:
        norm_factor = 1

    # make sure bin_content has int type when no weights are given
    if unweighted:
        bin_content, bin_edges = np.histogram(x, bins=bins, range=bin_range)
    else:
        bin_content, bin_edges = np.histogram(x, bins=bins, range=bin_range, weights=weights)
    
    if divide_bin_width:
        bin_width = bin_edge_to_bin_width(bin_edges)
        norm_factor *= bin_width
    
    if evaluate_error:
        error_mode = BinErrorMode.parse(error_mode)
        if error_mode == BinErrorMode.AUTO:
            unweighted = unweighted or np.allclose(weights, np.ones(weights.shape))
            error_mode = BinErrorMode.POISSON if unweighted else BinErrorMode.SUMW2
        if error_mode == BinErrorMode.POISSON:
            bin_errors =  poisson_interval(bin_content)
        elif error_mode == BinErrorMode.SUMW2:
            bin_content_weight2, _ = np.histogram(x, bins=bins, range=bin_range, weights=weights**2)
            bin_errors = np.sqrt(bin_content_weight2)
        if norm_factor != 1:
            if isinstance(bin_errors, tuple):
                bin_errors = (bin_errors[0] / norm_factor, bin_errors[1] / norm_factor)
            else:
                bin_errors /= norm_factor
    else:
        bin_errors = None
        
    if norm_factor != 1:
        bin_content = bin_content.astype(float, copy=False)
        bin_content /= norm_factor
    
    return bin_content, bin_edges, bin_errors


def histogram2d(x:np.ndarray, y:np.ndarray, 
                weights:Optional[np.ndarray]=None,
                bins:Union[int, Sequence]=10,
                bin_range:Optional[Sequence]=None,
                underflow:bool=False,
                overflow:bool=False,
                divide_bin_width:bool=False,
                normalize:bool=True,
                clip_weight:bool=False,
                evaluate_error:bool=False,
                error_mode:Union[BinErrorMode, str]="auto"):
    """
        Compute the 2d histogram of a 2d data array.
        
        Arguments:
        -------------------------------------------------------------------------------
        x: ndarray
            Input data array for the x coordinates of the points to be histogrammed.
        y: ndarray
            Input data array for the y coordinates of the points to be histogrammed.
        weights: (optional) ndarray
            Array of weights with same shape as input data. If not given, the
            input data is assumed to have unit weights.
        bins: (optional) int or sequence of scalars, default = 10
            (same as numpy.histogram2d) The bin specification :

            If int, the number of bins for the two dimensions (nx=ny=bins).
            
            If array_like, the bin edges for the two dimensions (x_edges=y_edges=bins).
            
            If [int, int], the number of bins in each dimension (nx, ny = bins).
            
            If [array, array], the bin edges in each dimension (x_edges, y_edges = bins).
            
            A combination [int, array] or [array, int], where int is the number of bins and array is the bin edges.
       bin_range: (optional) sequence of the form (float, float)
           (same as numpy.histogram2d) The leftmost and rightmost edges of the bins along each dimension (if not specified explicitly in the bins parameters): [[xmin, xmax], [ymin, ymax]]. All values outside of this range will be considered outliers and not tallied in the histogram.
       underflow: bool, default = False
           Include undeflow data in the first bin.
       overflow: bool, default = False
           Include overflow data in the last bin.
       divide_bin_width: bool, default = False
           Divide each bin by the bin width.           
       normalize: bool, default = True
           Normalize the sum of weights to one. Weights outside the bin range will
           not be counted if ``clip_weight`` is set to false, so the sum of bin
           content could be less than one.
       clip_weight: bool, default = False
           Ignore data outside given range when evaluating total weight
           used in normalization.
       evaluate_error: bool, default = True
           Evaluate the error of the bin contents using the given error option.
       error_mode: BinErrorMode or str, default = "auto"
           How to evaluate bin errors. If "sumw2", symmetric errors from the Wald
           approximation is used (square root of sum of squares of weights). If
           "poisson", asymmetric errors from Poisson interval at one sigma is
           used. If "auto", it will use sumw2 error if data has unit weights,
           else Poisson error will be used.
           
       Returns
       -------------------------------------------------------------------------------
       bin_content: np.ndarray, shape(nx, ny)
           The bi-dimensional histogram of samples x and y. Values in x are histogrammed along the first dimension and values in y are histogrammed along the second dimension.
       x_edges: np.ndarray, shape(nx+1,)
           The bin edges along the first dimension.
       y_edges: np.ndarray, shape(ny+1,)
           The bin edges along the first dimension.
       bin_errors: np.ndarray, shape(nx, ny)
           The bin errors of the histogram.
    """
    
    if len(x) != len(y):
        raise ValueError('x and y must have the same length.')
        
    bin_range = get_histogram_range(bin_range, D=2)
    x = get_clipped_data(x, bin_range=bin_range[0], clip_lower=underflow,
                         clip_upper=overflow)
    y = get_clipped_data(y, bin_range=bin_range[1], clip_lower=underflow,
                         clip_upper=overflow)
    N = len(x)
    
    unweighted = weights is None
    if weights is None:
        weights = np.ones((N,))
    else:
        # fix overflow bugs
        weights = np.array(weights, dtype=float)
        
    if normalize:
        if clip_weight:
            mask = None
            if (bin_range[0] is not None):
                first_edge, last_edge = bin_range[0]
                mask = (x >= first_edge) & (x <= last_edge)
            if (bin_range[1] is not None):
                first_edge, last_edge = bin_range[1]
                mask &= ((y >= first_edge) & (y <= last_edge))
            norm_factor = weights[mask].sum()
        else:
            norm_factor = weights.sum()
    else:
        norm_factor = 1

    if unweighted:
        bin_content, x_edges, y_edges = np.histogram2d(x, y,
                                                       bins=bins,
                                                       range=bin_range)
    else:
        bin_content, x_edges, y_edges = np.histogram2d(x, y,
                                                       bins=bins,
                                                       range=bin_range,
                                                       weights=weights)
    
    if divide_bin_width:
        x_bin_width = bin_edge_to_bin_width(x_edges)
        y_bin_width = bin_edge_to_bin_width(y_edges)
        norm_factor *= (x_bin_width * y_bin_width)
    
    if evaluate_error:
        error_mode = BinErrorMode.parse(error_mode)
        if error_mode == BinErrorMode.AUTO:
            unweighted = unweighted or np.allclose(weights, np.ones(weights.shape))
            error_mode = BinErrorMode.POISSON if unweighted else BinErrorMode.SUMW2
        if error_mode == BinErrorMode.POISSON:
            errlo, errhi = poisson_interval(bin_content.flatten())
            bin_errors =  (errlo.reshape(bin_content.shape),
                           errhi.reshape(bin_content.shape))
        elif error_mode == BinErrorMode.SUMW2:
            bin_content_weight2, _, _ = np.histogram2d(x, y, bins=bins,
                                                       range=bin_range,
                                                       weights=weights**2)
            bin_errors = np.sqrt(bin_content_weight2)
        if norm_factor != 1:
            if isinstance(bin_errors, tuple):
                bin_errors = (bin_errors[0] / norm_factor, bin_errors[1] / norm_factor)
            else:
                bin_errors /= norm_factor
    else:
        bin_errors = None
        
    if norm_factor != 1:
        bin_content /= norm_factor
    
    return bin_content, x_edges, y_edges, bin_errors
        
def get_hist_data(x:np.ndarray, weights:Optional[np.ndarray]=None,
                  bins:Union[int, Sequence]=10,
                  bin_range:Optional[Sequence]=None,
                  underflow:bool=False,
                  overflow:bool=False,
                  divide_bin_width:bool=False,
                  normalize:bool=True,
                  clip_weight:bool=False,
                  xerr:bool=True,
                  yerr:bool=True,
                  error_mode:Union[BinErrorMode, str]="auto"):
    """
        Extract histogram data from a data array.
        
        Arguments:
        -------------------------------------------------------------------------------
        x: ndarray
            Input data array from which the histogram is computed.
        weights: (optional) ndarray
            Array of weights with same shape as input data. If not given, the
            input data is assumed to have unit weights.
        bins: (optional) int or sequence of scalars, default = 10
            If integer, it defines the number of equal-width bins in the
            given range.
            If sequence, it defines a monotonically increasing array of bin edges,
            including the rightmost edge.
        bin_range: (optional) sequence of the form (float, float)
            The lower and upper range of the bins.  If not provided, range is simply 
            ``(x.min(), x.max())``.  Values outside the range are ignored.
        underflow: bool, default = False
            Include undeflow data in the first bin.
        overflow: bool, default = False
            Include overflow data in the last bin.
        divide_bin_width: bool, default = False
            Divide each bin by the bin width.
        normalize: bool, default = True
            Normalize the sum of weights to one. Weights outside the bin range will
            not be counted if ``clip_weight`` is set to false, so the sum of bin
            content could be less than one.
        clip_weight: bool, default = False
            If True, ignore data outside given range when evaluating total weight
            used in normalization.
        xerr: bool, default = True
            If True, evaluate the error of the bin centers (= bin widths / 2).
        yerr: bool, default = True
            If True, evaluate the error of the bin contents using the given error
            option.
        error_mode: BinErrorMode or str, default = "auto"
            How to evaluate bin errors. If "sumw2", symmetric errors from the Wald
            approximation is used (square root of sum of squares of weights). If
            "poisson", asymmetric errors from Poisson interval at one sigma is
            used. If "auto", it will use sumw2 error if data has unit weights,
            else Poisson error will be used.
            
        Returns
        -------------------------------------------------------------------------------
        hist_data: dict
            A dictionary with the keys "x", "y", "xerr", "yerr" with the bin centers,
            bin content, half bin widths and bin errors as values.
    """
    y, bin_edges, yerr = histogram(x, weights=weights,
                                   bins=bins, bin_range=bin_range,
                                   underflow=underflow,
                                   overflow=overflow,
                                   normalize=normalize,
                                   divide_bin_width=divide_bin_width,
                                   clip_weight=clip_weight,
                                   evaluate_error=yerr,
                                   error_mode=error_mode)
    x = bin_edge_to_bin_center(bin_edges)
    if xerr:
        # todo do not hard-code number of digits to keep
        xerr = np.round(np.diff(bin_edges) / 2, 5)
    else:
        xerr = None
    hist_data = {
        "x": x,
        "y": y,
        "xerr": xerr,
        "yerr": yerr
    }
    return hist_data


def get_stacked_hist_data(x:List[np.ndarray],
                          weights:List[Optional[np.ndarray]]=None,
                          bins:Union[int, Sequence]=10,
                          bin_range:Optional[Sequence]=None,
                          underflow:bool=False,
                          overflow:bool=False,
                          divide_bin_width:bool=False,
                          normalize:bool=True,
                          clip_weight:bool=False,
                          xerr:bool=True,
                          yerr:bool=True,
                          merge:bool=True,
                          error_mode:Union[BinErrorMode, str]="auto"):
    merged_x = np.concatenate(x)
    if bin_range is None:
        bin_range = (np.min(merged_x), np.max(merged_x))
    if merge:
        if weights is not None:
            merged_weights = np.concatenate(weights)
            assert merged_x.shape == merged_weights.shape
        else:
            merged_weights = None
        hist_data = get_hist_data(x=merged_x, weights=merged_weights,
                                  bins=bins, bin_range=bin_range,
                                  underflow=underflow,
                                  overflow=overflow,
                                  divide_bin_width=divide_bin_width,
                                  normalize=normalize,
                                  clip_weight=clip_weight,
                                  xerr=xerr, yerr=yerr,
                                  error_mode=error_mode)
        return hist_data
    else:
        hist_data_list = []
        if weights is None:
            weights = len(x) * None
        for x_i, weights_i in zip(x, weights):
            hist_data = get_hist_data(x=x_i, weights=weights_i,
                                      bins=bins, bin_range=bin_range,
                                      underflow=underflow,
                                      overflow=overflow,
                                      divide_bin_width=False,
                                      normalize=False,
                                      clip_weight=clip_weight,
                                      xerr=xerr, yerr=yerr,
                                      error_mode=error_mode)
            hist_data_list.append(hist_data)
        if normalize:
            norm_factor = np.sum([data['y'] for data in hist_data_list])
            for data in hist_data_list:
                data['y'] = data['y'] / norm_factor
                if isinstance(data['yerr'], tuple):
                    data['yerr'] = (data['yerr'][0] / norm_factor,
                                    data['yerr'][1] / norm_factor)
                elif data['yerr'] is not None:
                    data['yerr'] = data['yerr'] / norm_factor
        if divide_bin_width:
            bin_edges = np.histogram_bin_edges([bin_range[0], bin_range[1]],
                                               bins=bins, range=bin_range)
            bin_widths = bin_edge_to_bin_width(bin_edges)
            for data in hist_data_list:
                data['y'] = data['y'] / bin_widths
                if isinstance(data['yerr'], tuple):
                    data['yerr'] = (data['yerr'][0] / bin_widths,
                                    data['yerr'][1] / bin_widths)
                elif data['yerr'] is not None:
                    data['yerr'] = data['yerr'] / bin_widths
        from quickstats.utils.common_utils import list_of_dict_to_dict_of_list
        stacked_hist_data = list_of_dict_to_dict_of_list(hist_data_list)
        return stacked_hist_data

def get_sumw2(weights: np.ndarray):
    return np.sqrt(np.sum(weights ** 2))

def get_hist_mean(x:np.ndarray, y:np.ndarray):
    return np.sum(x * y) / np.sum(y)

def get_hist_std(x:np.ndarray, y:np.ndarray):
    mean = get_hist_mean(x, y)
    count = np.sum(y)
    if count == 0.:
        return 0.
    # for negative stddev (e.g. when having negative weights) - return std=0
    std2 = np.max([np.sum(y * (x - mean)**2) / count, 0.])
    return np.sqrt(std2)

def get_hist_effective_entries(y:np.ndarray, yerr:np.ndarray):
    # neff = \frac{(\sum Weights )^2}{(\sum Weight^2 )}
    sumw2 = np.sum(yerr ** 2)
    if sumw2 != 0.:
        return (np.sum(y) ** 2) / sumw2
    else:
        return 0
    
def get_hist_mean_error(x:np.ndarray, y:np.ndarray, yerr:np.ndarray):
    # mean error = StdDev / sqrt( Neff )
    neff = get_hist_effective_entries(y, yerr)
    if neff > 0.:
        std = get_hist_std(x, y)
        return std / np.sqrt(neff)
    else:
        return 0.
    
def get_cumul_hist(y:np.ndarray, yerr:np.ndarray):
    y_cum = np.cumsum(y)
    yerr_cum = np.sqrt(np.cumsum(yerr ** 2))
    return y_cum, yerr_cum

def get_bin_centers_from_range(xlow:float, xhigh:float, nbins:int, bin_precision:int=8):
    bin_width = (xhigh - xlow) / nbins
    low_bin_center  = xlow + bin_width / 2
    high_bin_center = xhigh - bin_width /2
    bins = np.around(np.linspace(low_bin_center, high_bin_center, nbins), bin_precision)
    return bins

def select_binned_data(mask:np.ndarray, x:np.ndarray, y:np.ndarray,
                       xerr:Optional[ArrayLike]=None,
                       yerr:Optional[ArrayLike]=None):
    x, y = np.asarray(x)[mask], np.asarray(y)[mask]
    def select_err(err):
        if (err is None) or (not isinstance(err, (list, tuple, np.ndarray))):
            return err
        if np.ndim(err, 2) and (np.shape(err)[0] == 2):
            return (select_err(err[0]), select_err(err[1]))
        return err[mask]
    xerr, yerr = select_err(xerr), select_err(yerr)
    return x, y, xerr, yerr    

def dataset_is_binned(x:np.ndarray, y:np.ndarray, xlow:float, xhigh:float, nbins:int,
                      ghost_threshold:float=1e-8, bin_precision:int=8):
    bin_centers = get_bin_centers_from_range(xlow, xhigh, nbins, bin_precision=bin_precision)
    x = np.around(x, bin_precision)
    same_nbins = len(x) == len(bin_centers)
    if same_nbins and np.allclose(bin_centers, x):
        return True
    elif np.all(y == 1.):
        return False
    else:
        y_no_ghost = y[y > ghost_threshold]
        unit_weight_no_ghost = np.all(y_no_ghost) == 1.
        scaled_weight_no_ghost = len(np.unique(y_no_ghost)) == 1
        if unit_weight_no_ghost or scaled_weight_no_ghost:
            return False
        elif same_nbins:
            return True
        elif array_issubset(bin_centers, x):
            return True
    raise RuntimeError('found dataset with invalid binning')
    
def fill_missing_bins(x:np.ndarray, y:np.ndarray, xlow:float, xhigh:float, nbins:int,
                      value:float=0, bin_precision:int=8):
    bin_centers = get_bin_centers_from_range(xlow, xhigh, nbins, bin_precision=bin_precision)
    x_rounded = np.around(x, bin_precision)
    missing_bins = np.setdiff1d(bin_centers, x_rounded)
    if value == 0:
        missing_values = np.zeros(missing_bins.shape)
    else:
        missing_values = np.full(missing_bins.shape, value)
    x = np.concatenate([x, missing_bins])
    y = np.concatenate([y, missing_values])
    idx = np.argsort(x)
    x = x[idx]
    y = y[idx]
    return x, y

def rebin_dataset(x:np.ndarray, y:np.ndarray, nbins:int):
    bin_edges = bin_center_to_bin_edge(x)
    from quickstats.interface.root import TH1
    pyh = TH1.from_numpy_histogram(y, bin_edges=bin_edges)
    pyh.rebin(nbins)
    x = pyh.bin_center
    y = pyh.bin_content
    return x, y

def get_hist_comparison_data(reference_data, target_data,
                             mode:Union[HistComparisonMode, str]="ratio"):
    mode = HistComparisonMode.parse(mode)
    if not np.allclose(target_data['x'], reference_data['x']):
        raise RuntimeError("cannot compare two distributions with different binnings")

    from quickstats.concepts import Histogram1D
    
    h_ref = Histogram1D(bin_content=reference_data['y'],
                        bin_edges=bin_center_to_bin_edge(reference_data['x']),
                        bin_errors=reference_data.get('yerr', None))
    h_tar = Histogram1D(bin_content=target_data['y'],
                        bin_edges=bin_center_to_bin_edge(target_data['x']),
                        bin_errors=target_data.get('yerr', None))

    if mode == HistComparisonMode.RATIO:
        h_com = h_tar / h_ref
    elif mode == HistComparisonMode.DIFFERENCE:
        h_com = t_tar - h_ref
    else:
        raise ValueError(f'Unknown comparison mode: {mode}')
    
    comparison_data = {
        'x': reference_data['x'],
        'y': h_com.bin_content,
        'yerr': h_com.bin_errors,
        'xerr': reference_data.get('xerr', None)
    }
    return comparison_data

def get_global_pvalue_significance(x:np.ndarray, pvalue_local:Optional[np.ndarray]=None,
                                   Z_local:Optional[np.ndarray]=None, Z_ref:float=0):
    if (pvalue_local is None) and (Z_local is None):
        raise ValueError('either pvalue_local or Z_local must be provided')
    elif (pvalue_local is not None) and (Z_local is not None):
        raise ValueError('can not specify both pvalue_local and Z_local')        
    elif (pvalue_local is not None) and (Z_local is None):
        Z_local = pvalue_to_significance(pvalue_local)
        pvalue_local = np.array(pvalue_local)
    elif (pvalue_local is None) and (Z_local is not None):
        Z_local = np.array(Z_local)
        pvalue_local = significance_to_pvalue(Z_local)
    sort_idx = np.argsort(x)
    x = x[sort_idx]
    Z_local = Z_local[sort_idx]
    pvalue_local = pvalue_local[sort_idx]
    asign = np.sign(Z_local - Z_ref)
    sign_change = (np.roll(asign, 1) - asign)
    sign_change[0] = 0
    # number of downcrossings
    N_up = np.sum(sign_change < 0)
    exp_term = np.exp(-0.5*(Z_local**2 - Z_ref**2))
    p_global = N_up * exp_term + pvalue_local
    delta_p_global = np.sqrt(N_up) * exp_term
    Z_global = pvalue_to_significance(p_global)
    Z_global_delta_up = pvalue_to_significance(p_global + delta_p_global)
    mask = ~np.isinf(Z_global_delta_up)
    Z_global_errhi = np.where(mask, np.subtract(Z_global, Z_global_delta_up, where=mask), np.nan)
    Z_global_delta_down = pvalue_to_significance(p_global - delta_p_global)
    mask = ~np.isinf(Z_global_delta_down)
    Z_global_errlo = np.where(mask, np.subtract(Z_global_delta_down, Z_global, where=mask), np.nan)
    result = {
        'N_up'           : np.full(p_global.shape, N_up),
        'p_global'       : p_global,
        'p_global_err'   : delta_p_global,
        'Z_global'       : Z_global,
        'Z_global_errhi' : Z_global_errhi,
        'Z_global_errlo' : Z_global_errlo
    }
    return result

HistoMaskType = Union[ArrayLike, Callable]
def get_histogram_mask(x: np.ndarray,
                       condition: HistoMaskType,
                       y: Optional[np.ndarray]=None) -> np.ndarray:
    if (y is not None) and (len(x) != len(y)):
        raise ValueError('x and y values must have the same size')
    mask = np.full(x.shape[:1], False)
    if callable(condition):
        if y is None:
            mask |= np.array(list(map(condition, x)))
        else:
            mask |= np.array(list(map(condition, x, y)))
    else:
        try:
            condition = np.asarray(condition)
            if len(condition) == 2:
                xmin, xmax = condition
                mask |= ((x > xmin) & (x < xmax))
            elif len(condition) == 4:
                xmin, xmax, ymin, ymax = condition
                mask |= (x > xmin) & (x < xmax) & (y > ymin) & (y < ymax)
            else:
                raise ValueError("range based mask condition must be in the form "
                                 "(xmin, xmax) or (xmin, xmax, ymin, ymax)")
        except (TypeError, ValueError):
            raise TypeError(f'invalid mask condition: {condition}')
    return mask

def upcast_error(size:int, values:Union[float, ArrayLike, None]=None) -> Union[np.ndarray, None]:
    if values is None:
        return None
    values = np.asarray(values)
    if values.ndim == 0:
        return np.full((2, size), values)
    elif (values.ndim == 1) and (values.shape == (size,)):
        return np.tile(values, (2, 1))
    elif (values.ndim == 2) and (values.shape == (2, size)):
        return values
    else:
        raise ValueError(f'"values" (shape: {values.shape}) must be a scalar or a 1D or (2, n) '
                         f'array-like whose shape matches ({size},)')

def custom_median_with_tie(data, threshold=0.5):
    """
    Compute the median or a custom statistic based on the two middle values (in the case of ties).

    Parameters:
    - data: list or array of numeric values.
    - threshold: a value between 0 and 1 that defines what is considered an "extreme case".
      If the difference between the two middle values is greater than the threshold times the median, the mean-based custom action is taken.

    Returns:
    - Custom median (or value closest to the mean if the two middle values are too different).
    """
    data = np.sort(data)
    
    median = np.median(data)
    mean = np.mean(data)
    
    if len(data) % 2 == 0:
        mid_left = data[len(data)//2 - 1]
        mid_right = data[len(data)//2]
        
        if abs(mid_right - mid_left) > threshold * median:
            closest_to_mean = min([mid_left, mid_right], key=lambda x: abs(x - mean))
            return closest_to_mean
        else:
            return (mid_left + mid_right) / 2
    else:
        return median