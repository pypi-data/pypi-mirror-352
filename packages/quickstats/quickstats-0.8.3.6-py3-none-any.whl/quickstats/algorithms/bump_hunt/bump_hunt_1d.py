###############################################################################
### This is a reimplementation of pyBumpHunter package
### taken from https://github.com/scikit-hep/pyBumpHunter
### Original author: Louis Vaslin (main developer), Julien Donini
###############################################################################
from typing import Optional, Union, Tuple, List, Dict, Any, Callable, Literal
from itertools import repeat
from functools import cached_property
from collections import defaultdict

import numpy as np
from scipy.special import gammainc as Gamma
from scipy.stats import norm
from pydantic import Field

from quickstats import semistaticmethod
from quickstats.core.typing import ArrayLike
from quickstats.concepts import Binning, Histogram1D
from quickstats.interface.pydantic import DefaultModel
from quickstats.maths.numerics import sliced_sum
from quickstats.utils.common_utils import execute_multi_tasks, combine_dict
from quickstats.utils.string_utils import format_aligned_dict
from .settings import BumpHuntMode, SignalStrengthScale, AutoScanStep

__all__ = ['BumpHunt1D']


class BumpHuntOutput1D:
    """
    Stores the output of the BumpHunter 1D analysis, including results,
    p-values, and computed attributes such as significance and bump location.

    Parameters
    ----------
    results : Dict[str, np.ndarray]
        Dictionary containing the results, such as 'nll', 'min_loc', etc.
    data_pval_arr : np.ndarray
        Array of p-values for the data.
    binning : List[Binning]
        List of `Binning` objects that define the histogram bins for each channel.
    """

    def __init__(self, results: Dict[str, np.ndarray],
                 data_pval_arr: np.ndarray,
                 data_window_arr: np.ndarray,
                 data_hists: List[Histogram1D],
                 ref_hists: List[Histogram1D]):
        self._results = results
        self._data_pval_arr = data_pval_arr
        self._data_window_arr = data_window_arr
        self._data_hists = data_hists
        self._ref_hists = ref_hists

    @property
    def results(self) -> Dict[str, np.ndarray]:
        """
            Returns the dictionary of results storing computed data and pseudo-experiment outcomes.

            Case nchannel = 1, value shape = (1 + npseudo);
            Case nchannel > 1, value shape = (1 + npseudo, nchannel);
            Note for key = 'nll', value shape = (1 + npseudo) irrespective of nchannel;
            Index 0 of first dimension is the observed data, followed by the pseudo-experiments.
            
        """
        return self._results

    @property
    def data_pval_arr(self) -> np.ndarray:
        """
            Returns the p-value array for the data.

            Case nchannel = 1, shape = (nwidths, <nwindows>) 
            Case nchannel > 1, shape = (nchannel, nwidths, <nwindows>)
        """
        return self._data_pval_arr

    @property
    def data_window_arr(self) -> np.ndarray:
        """
            Returns the bump window array for the data.

            Case nchannel = 1, shape = (nwidths, <nwindows>, 2)
            Case nchannel > 1, shape = (nchannel, nwidths, <nwindows>, 2)
        """
        return self._data_window_arr

    @property
    def data_hists(self) -> List[Histogram1D]:
        """
            Returns the list of data histograms for each channel.
        """
        return self._data_hists

    @property
    def ref_hists(self) -> List[Histogram1D]:
        """
            Returns the list of reference histograms for each channel..
        """
        return self._ref_hists

    @property
    def binnings(self) -> List[Binning]:
        """
            Returns the list of binning for each channel.
        """
        return [h.binning for h in self._data_hists]

    @cached_property
    def nchannel(self) -> int:
        """Returns the number of channels in the data."""
        return len(self._data_hists)

    @cached_property
    def npseudo(self) -> int:
        """Returns the number of pseudo-experiments based on the 'nll' array shape."""
        return self.results['nll'].shape[0] - 1

    @cached_property
    def S(self) -> Optional[float]:
        """
        Calculates the number of pseudo-experiments with NLL greater than or equal to the data NLL.
        
        Returns
        -------
        Optional[float]
            The count of pseudo-experiments, or None if no pseudo-experiments are available.
        """
        nll_array = self.results['nll']
        if nll_array.size > 1:
            nll_data = nll_array[0]
            nll_pseudo = nll_array[1:]
            return nll_pseudo[nll_pseudo >= nll_data].size
        return None

    @cached_property
    def global_pval(self) -> Optional[float]:
        """
        Computes the global p-value based on the number of pseudo-experiments and S.
        
        Returns
        -------
        Optional[float]
            The global p-value, or None if it cannot be computed.
        """
        if self.npseudo < 1 or self.S is None:
            return None
        return self.S / self.npseudo

    @cached_property
    def significance(self) -> Optional[float]:
        """
        Computes the global significance as a z-score using the global p-value.
        
        Returns
        -------
        Optional[float]
            The significance, or None if the global p-value cannot be computed.
        """
        global_pval = self.global_pval
        if global_pval is None:
            return None
        if global_pval == 1:
            return 0
        if global_pval == 0:
            return norm.ppf(1 - (1 / self.npseudo))
        return norm.ppf(1 - global_pval)

    @cached_property
    def bump_edge(self) -> ArrayLike:
        """
        Returns the edges of the bump (signal window) for the data.

        Returns
        -------
        np.ndarray
            The bump edges for one or multiple channels.
        """
        binnings = self.binnings
        min_loc = self.results['min_loc'][0]
        min_width = self.results['min_width'][0]
        if self.nchannel == 1:
            return np.array([binnings[0].bin_edges[min_loc], binnings[0].bin_edges[min_loc + min_width]])
        return np.array([[binnings[i].bin_edges[min_loc[i]], binnings[i].bin_edges[min_loc[i] + min_width[i]]] for i in range(self.nchannel)])

    @cached_property
    def bump_edge_c(self) -> np.ndarray:
        """
        Returns the common overlap of bump edges across all channels.

        Returns
        -------
        np.ndarray
            Common bump edge overlap for all channels.
        """
        bump_edge = self.bump_edge
        if self.nchannel == 1:
            return np.array(bump_edge)
        return np.array([np.max(bump_edge[:, 0]), np.min(bump_edge[:, 1])])

    @cached_property
    def bump_mean(self) -> float:
        """Returns the mean position of the bump in the data."""
        low_edge, high_edge = self.bump_edge_c
        return (low_edge + high_edge) / 2

    @cached_property
    def bump_width(self) -> float:
        """Returns the width of the bump (signal region)."""
        low_edge, high_edge = self.bump_edge_c
        return high_edge - low_edge

    def get_summary(self) -> Dict[str, Any]:
        """
        Generates a summary of the bump scan results, including the bump edge, significance, and p-values.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing key bump statistics and channel-specific outputs.
        """
        channel_attribs = {
            'bump_edge': self.bump_edge
        }

        # Collect attributes for each channel
        for key in ['min_pval', 'min_loc', 'min_width', 'signal_eval']:
            channel_attribs[key] = self.results[key][0]

        if self.nchannel == 1:
            for key, value in channel_attribs.items():
                channel_attribs[key] = [value]

        # Summarize outputs
        result = {}
        channel_output = {}

        for i in range(self.nchannel):
            channel_output[i] = {
                'bump_edge': channel_attribs['bump_edge'][i],
                'bin_loc': channel_attribs['min_loc'][i],
                'bin_width': channel_attribs['min_width'][i],
                'nsignal': channel_attribs['signal_eval'][i],
                'local_pval': channel_attribs['min_pval'][i]
            }

        result['channel_output'] = channel_output
        result['bump_edge'] = self.bump_edge_c
        result['bump_mean'] = self.bump_mean
        result['bump_width'] = self.bump_width
        result['nsignal'] = np.sum(channel_attribs['signal_eval'])
        result['nll'] = self.results['nll'][0]
        result['local_pval'] = np.prod(channel_attribs['min_pval'])
        result['local_significance'] = norm.ppf(1 - result['local_pval'])
        result['global_pval'] = self.global_pval
        result['global_significance'] = self.significance

        return result

    def print_summary(self) -> None:
        """Prints the formatted summary of the bump scan results."""
        print(self.get_summary_text())

    def get_summary_text(self, val_fmt: str = ".3g") -> str:
        """
        Returns a formatted string representation of the bump scan results.

        Parameters
        ----------
        val_fmt : str, optional
            Format string for the numerical values (default is '.3g').

        Returns
        -------
        str
            Formatted text summary.
        """
        summary = self.get_summary()
        channel_output = summary.pop('channel_output')

        # Format each channel output
        for idx, output in channel_output.items():
            low_edge, high_edge = output.pop('bump_edge')
            output['low_edge'] = low_edge
            output['high_edge'] = high_edge
            for key, value in output.items():
                output[key] = format(value, val_fmt)

        # Format summary
        low_edge, high_edge = summary.pop('bump_edge')
        summary['low_edge'] = low_edge
        summary['high_edge'] = high_edge
        for key, value in summary.items():
            summary[key] = format(value, val_fmt)

        # Build result string
        result = ''
        for idx, output in channel_output.items():
            result += f'Channel {idx}\n\n'
            table = {
                'Bump edge': '[{low_edge}, {high_edge}] (bin_loc = {bin_loc}, bin_width = {bin_width})'.format(**output),
                'Number of signals': output['nsignal'],
                'Local p-value': output['local_pval']
            }
            result += format_aligned_dict(table, left_margin=4) + '\n'

        # Combined result
        result += f'Combined\n\n'
        table = {
            'Bump edge': '[{low_edge}, {high_edge}]'.format(**summary),
            'Bump mean': summary['bump_mean'],
            'Bump width': summary['bump_width'],
            'Number of signals': summary['nsignal'],
            'Test statistic (NLL)': summary['nll'],
            'Local p-value': summary['local_pval'],
            'Local significance': summary['local_significance']
        }
        if self.global_pval is not None:
            table['Global p-value'] = summary['global_pval']
            if self.global_pval == 0:
                table['Global significance'] = f'> {summary["global_significance"]} (lower limit)'
            else:
                table['Global significance'] = summary['global_significance']
        result += format_aligned_dict(table, left_margin=4) + '\n'

        return result

    def get_bin_by_bin_significance(self, channel: int = 0) -> np.ndarray:
        data_hist = self.data_hists[channel]._bin_content.astype(float)
        ref_hist = self.ref_hists[channel]._bin_content.astype(float)
        if 'norm_scale' in self.results:
            if self.nchannel == 1:
                norm_scale = self.results['norm_scale']
            else:
                norm_scale = self.results['norm_scale'][channel]
            ref_hist *= norm_scale
        excess = (data_hist > ref_hist) & (ref_hist > 0)
        deficit = data_hist < ref_hist
        sig = np.ones(ref_hist.size)
        sig[excess] = Gamma(data_hist[excess], ref_hist[excess])
        sig[deficit] = 1 - Gamma(data_hist[deficit] + 1, ref_hist[deficit])
        sig = norm.ppf(1 - sig)
        # force sig to be non-negative
        sig[sig < 0.0] = 0.0
        # avoid nans
        np.nan_to_num(sig, posinf=0, neginf=0, nan=0, copy=False)
        # put back the sign
        sig[deficit] = - sig[deficit]
        return sig

    def get_sig_hist(self, channel: int = 0) -> Histogram1D:
        sig = self.get_bin_by_bin_significance(channel=channel)
        bin_edges = self.binnings[channel].bin_edges
        sig_hist = Histogram1D(sig, bin_edges=bin_edges, error_mode='sumw2')
        return sig_hist

    def get_tomography_data(self, channel: int = 0,
                            threshold: Optional[float] = 1.) -> Dict[str, np.ndarray]:
        if (channel < 0) or (channel >= self.nchannel):
            raise ValueError(f'Channel index out of bounds (min = 0, max = {self.nchannel - 1}).')
        if self.nchannel == 1:
            pval_arr = self.data_pval_arr
            window_arr = self.data_window_arr
        else:
            pval_arr = self.data_pval_arr[channel]
            window_arr = self.data_window_arr[channel]

        data = {
            'lower_bin': [],
            'upper_bin': [],
            'pval': []
        }
        
        nwidths = len(pval_arr)
        for i in range(nwidths):
            data['lower_bin'].append(window_arr[i][:, 0])
            data['upper_bin'].append(window_arr[i][:, 1])
            data['pval'].append(pval_arr[i])
        for key, value in data.items():
            data[key] = np.concatenate(value)

        if threshold is not None:
            mask = data['pval'] < threshold
            for key, value in data.items():
                data[key] = value[mask]

        bin_edges = self.binnings[channel].bin_edges
        data['lower_edge'] = bin_edges[data['lower_bin']]
        data['upper_edge'] = bin_edges[data['upper_bin']]
            
        return data

    def plot_tomography(self, channel: int = 0,
                        xlabel: Optional[str] = None,
                        ylabel: Optional[str] = 'p-value',
                        logy: bool = True,
                        init_kwargs: Optional[Dict] = None,
                        draw_kwargs: Optional[Dict] = None):
        from quickstats.plots import TomographyPlot
        import pandas as pd

        init_kwargs = combine_dict(init_kwargs)
        default_draw_kwargs = {
            'xloattrib' : 'lower_edge',
            'xhiattrib' : 'upper_edge',
            'yattrib' : 'pval',
            'xlabel' : xlabel,
            'ylabel' : ylabel,
            'logy' : logy
        }
        draw_kwargs = combine_dict(default_draw_kwargs, draw_kwargs)

        data = self.get_tomography_data(channel=channel, threshold=1.)
        df = pd.DataFrame(data)
        plotter = TomographyPlot(df, **init_kwargs)
        return plotter.draw(**draw_kwargs)
        
    def plot_bump(self, channel: int = 0,
                  xlabel: Optional[str] = None,
                  ylabel: Optional[str] = 'Number of Events',
                  logy: bool = False,
                  init_kwargs: Optional[Dict] = None,
                  draw_kwargs: Optional[Dict] = None):
        from quickstats.plots import BumpHunt1DPlot

        data_hist = self.data_hists[channel]
        ref_hist = self.ref_hists[channel]
        sig_hist = self.get_sig_hist(channel=channel)
        bin_range = self.binnings[channel].bin_range
        bump_edge = self.bump_edge
        
        init_kwargs = combine_dict(init_kwargs)
        default_draw_kwargs = {
            'xlabel': xlabel,
            'ylabel': ylabel,
            'logy': logy,
            'xmin': bin_range[0],
            'xmax': bin_range[1],
            'bump_edge': bump_edge
        }
        draw_kwargs = combine_dict(default_draw_kwargs, draw_kwargs)

        plotter = BumpHunt1DPlot(data_hist=data_hist,
                                 ref_hist=ref_hist,
                                 sig_hist=sig_hist,
                                 **init_kwargs)
        return plotter.draw(**draw_kwargs)
        
class BumpHunt1D(DefaultModel):
    
    scan_range: Optional[Tuple[float, float]] = Field(
        default=None, 
        description="x-axis range of the histograms. Defines the range in which the scan will be performed. "
                    "Can be either None or an array-like of float with shape (2, 2). If None, the range is set "
                    "automatically to include all the data given."
    )
    
    mode: BumpHuntMode = Field(
        default=BumpHuntMode.Excess, 
        description="Specifies whether the algorithm should look for an excess or deficit in the data. "
                    "Can be either 'excess' or 'deficit'. Default is 'excess'."
    )
    
    width_min: int = Field(
        default=1, 
        description="Minimum value of the scan window width to be tested, in number of bins. Default is 1."
    )
    
    width_max: Optional[int] = Field(
        default=None, 
        description="Maximum value of the scan window width to be tested, in number of bins. "
                    "Can be either None or a positive integer. If None, it is set to the total number of bins "
                    "in the histograms divided by 2."
    )
    
    width_step: int = Field(
        default=1, 
        description="Number of bins by which the scan window width is increased at each step. Default is 1."
    )
    
    scan_step: Union[int, AutoScanStep] = Field(
        default=1, 
        description="Number of bins by which the position of the scan window is shifted at each step. "
                    "Can be 'full', 'half', or a positive integer. If 'full', the window is shifted by a number of bins "
                    "equal to its width. If 'half', it is shifted by max(1, width // 2)."
    )
    
    npseudo: int = Field(
        default=100, 
        description="Number of pseudo-data distributions to be sampled from the reference background distribution. "
                    "Must be greater than 0. Default is 100."
    )
    
    bins: Union[int, np.ndarray] = Field(
        default=60, 
        description="Defines the bins of the histograms. Can be an integer (for equal-width bins) or an array-like of "
                    "floats (for variable-width bins). For multiple channels, a list of arrays containing the bin edges "
                    "for each channel can be provided."
    )
    
    sigma_limit: float = Field(
        default=5.0, 
        description="Minimum significance required after signal injection. Default is 5.0."
    )
    
    mu_min: float = Field(
        default=0.5, 
        description="The minimum signal strength to inject in the background for the first iteration. Default is 0.5."
    )
    
    mu_step: float = Field(
        default=0.25, 
        description="Increment of the signal strength injected in the background at each iteration. Default is 0.25."
    )
    
    mu_scale: SignalStrengthScale = Field(
        default=SignalStrengthScale.Linear, 
        description="Specifies how the signal strength should vary. Can be 'log' (logarithmic scale) or 'lin' "
                    "(linear scale). Default is 'lin'."
    )
    
    signal_exp: Optional[float] = Field(
        default=None, 
        description="Expected number of signals used to compute the signal strength. If None, signal strength is not computed."
    )
    
    flip_sig: bool = Field(
        default=True, 
        description="Boolean specifying if the signal should be flipped when running in deficit mode. Ignored in excess mode. Default is True."
    )
    
    npseudo_inject: int = Field(
        default=100, 
        description="Number of background+signal pseudo-experiments generated during signal injection tests. Default is 100."
    )
    
    seed: Optional[int] = Field(
        default=None, 
        description="Seed for the random number generator. If None, a random seed is used."
    )
    
    use_sideband: bool = Field(
        default=False, 
        description="Boolean specifying if sideband normalization should be applied. Default is False."
    )
    
    sideband_width: Optional[int] = Field(
        default=None, 
        description="Number of bins to be used as sideband during the scan when sideband normalization is activated. "
                    "If None, the entire histogram range is used for both scanning and normalization."
    )
    
    parallel: int = Field(
        default=-1, 
        description="Number of parallel workers (threads or processes) to be used for the scan. "
                    "If negative, the number of workers is set to the number of CPUs. If 0, tasks are run sequentially. Default is -1."
    )
    
    executor: Literal['process', 'thread'] = Field(
        default='process', 
        description="Type of executor to use for parallelism. Can be 'process' for multiprocessing or 'thread' for multithreading. Default is 'process'."
    )

    _pvalue_thres: float = 1e-300

    @staticmethod
    def _get_pval_algo(mode: Union[str, BumpHuntMode] = 'excess') -> Callable:
        """Get algorithm for evaluating local pvalues from slices of data and reference counts."""
        mode = BumpHuntMode.parse(mode)
        if mode == BumpHuntMode.Excess:
            def pval_algo(N_data: np.ndarray, N_ref: np.ndarray) -> np.ndarray:
                result = np.ones(N_data.size)
                mask = (N_data > N_ref) & (N_ref > 0)
                result[mask] = Gamma(N_data[mask], N_ref[mask])
                return result
            return pval_algo
        elif mode == BumpHuntMode.Deficit:
            def pval_algo(N_data: np.ndarray, N_ref: np.ndarray) -> np.ndarray:
                result = np.ones(N_data.size)
                mask = N_data < N_ref
                result[mask] = 1.0 - Gamma(N_data[mask] + 1, N_ref[mask])
                return result
            return pval_algo
        raise BumpHuntMode.on_parse_exception(mode)

    @staticmethod
    def _resolve_scan_steps(scan_step: Union[str, int], widths: np.ndarray) -> np.ndarray:
        """
        """
        # Auto-adjust scan step if specified.
        if isinstance(scan_step, int):
            steps = np.full(widths.shape, scan_step)
        else:
            scan_step = AutoScanStep.parse(scan_step)
            if scan_step == AutoScanStep.Full:
                steps = np.array(widths)
            elif scan_step == AutoScanStep.Half:
                steps = np.maximum(np.ones(widths.shape, dtype=int), widths // 2)
            else:
                raise AutoScanStep.on_parse_exception(scan_step)
        return steps

    @staticmethod
    def _get_index_bounds(ref: np.ndarray, sideband_width: Optional[int] = None) -> Tuple[int, int]:
        nonzero_indices = np.where(ref > 0)[0]
        idx_inf = np.min(nonzero_indices)
        idx_sup = np.max(nonzero_indices) + 1
        if sideband_width is not None:
            idx_inf += sideband_width
            idx_sup -= sideband_width
        return idx_inf, idx_sup

    @staticmethod
    def _get_sideband_norm(data: np.ndarray, ref: np.ndarray) -> Tuple[float, float]:
        idx_inf, idx_sup = BumpHunt1D._get_index_bounds(ref)
        data_total = data[idx_inf:idx_sup].sum()
        ref_total = ref[idx_inf:idx_sup].sum()
        return data_total, ref_total

    @staticmethod
    def _scan_hist(
        data: np.ndarray,
        ref: np.ndarray,
        widths: np.ndarray,
        mode: Union[str, BumpHuntMode] = 'excess',
        scan_step: Union[str, int] = 1,
        use_sideband: bool = False,
        sideband_width: Optional[int] = None,
        detailed: bool = True
    ) -> Dict[str, Any]:
        """Scan a distribution and compute the p-value associated to every scan window.

        The algorithm follows the BumpHunter algorithm. Compute also the significance for the data histogram.
        """
        data = np.asarray(data)
        ref = np.asarray(ref)
        widths = np.asarray(widths, dtype=int)

        if np.ndim(data) != 1:
            raise ValueError(f'Target histogram must be one-dimensional, got {np.ndim(data)} instead.')
        if np.ndim(ref) != 1:
            raise ValueError(f'Reference histogram must be one-dimensional, got {np.ndim(ref)} instead.')
        if data.shape != ref.shape:
            raise ValueError(f'Target and reference histograms must have the same shape.')
        if np.ndim(widths) != 1:
            raise ValueError(f'Widths array must be one-dimensional, got {np.ndim(widths)} instead.')
        if not use_sideband:
            sideband_width = None

        # remove the first/last hist bins if empty ... just to be consistent with c++
        data_inf, data_sup = BumpHunt1D._get_index_bounds(ref, sideband_width=sideband_width)
        if use_sideband:
            data_total, ref_total = BumpHunt1D._get_sideband_norm(data, ref)
        else:
            data_total, ref_total = None, None

        steps = BumpHunt1D._resolve_scan_steps(scan_step, widths)
        pval_algo = BumpHunt1D._get_pval_algo(mode)

        pval_arr = np.empty(widths.shape, dtype=object)
        window_arr = np.empty(widths.shape, dtype=object)
        delta_arr = np.zeros(widths.shape, dtype=object)
        scale_arr = np.ones(widths.shape)

        for i, (width, step) in enumerate(zip(widths, steps)):
            # define position range
            pos = np.arange(data_inf, data_sup - width + 1, step)

            # check that there is at least one interval to check for a given width
            # if not, we must set dummy values in order to avoid crashes
            if not pos.size:
                pval_arr[i] = np.array([1.0])
                continue

            slices = np.stack([pos, pos + width], axis=1)
            N_data = sliced_sum(data, slices)
            N_ref = sliced_sum(ref, slices)

            # compute and apply side-band normalization scale factor (if needed)
            if use_sideband:
                scale = (data_total - N_data) / (ref_total - N_ref)
                N_ref *= scale
                scale_arr[i] = scale

            pval = pval_algo(N_data, N_ref)

            if use_sideband:
                # prevent issue with very low p-value, sometimes induced by normalization in the tail
                pval = np.minimum(pval, self._pvalue_thres)

            pval_arr[i] = pval
            window_arr[i] = slices
            delta_arr[i] = N_data - N_ref

        # get the minimum p-value and associated window among all width
        min_pvals = np.array(list(map(np.min, pval_arr)))
        min_locs = np.array(list(map(np.argmin, pval_arr)))
        idx = min_pvals.argmin()

        result = {
            'pval_arr': pval_arr,
            'window_arr': window_arr,
            'min_pval': min_pvals[idx],
            'min_width': widths[idx],
            'min_loc': min_locs[idx],
            'signal_eval': delta_arr[idx][min_locs[idx]],
            'norm_scale': scale_arr[idx] if use_sideband else None
        }
        if not detailed:
            result.pop('pval_arr')
            result.pop('window_arr')
        return result

    @staticmethod
    def _default_result_multi(
        data_list: List[np.ndarray],
        ref_list: List[np.ndarray],
        widths: np.ndarray,
        sideband_width: Optional[int] = None
    ) -> Dict[str, Any]:
        nchannel = len(data_list)
        data_inf_list = []
        data_sup_list = []
        for i in range(nchannel):
            data_inf, data_sup = BumpHunt1D._get_index_bounds(ref_list[i], sideband_width=sideband_width)
            data_inf_list.append(data_inf)
            data_sup_list.append(data_sup)
        pval_arr = np.ones((nchannel, widths.size))
        window_arr = np.zeros((nchannel, widths.size, 2))
        result = {
            'pval_arr': pval_arr,
            'window_arr': window_arr,
            'min_pval': np.ones(nchannel),
            'min_loc': np.array(data_inf_list),
            'min_width': np.array(data_sup_list),
            'signal_eval': np.zeros(nchannel),
            'norm_scale': np.array([None] * nchannel)
        }
        return result

    @staticmethod
    def _combine_result(
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        combined_result = defaultdict(list)
        for result in results:
            for key, value in result.items():
                combined_result[key].append(value)
        for key, value in combined_result.items():
            combined_result[key] = np.array(value)
        return combined_result

    @staticmethod
    def _combine_channel_result(
        data_list: List[np.ndarray],
        ref_list: List[np.ndarray],
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        combined_result = BumpHunt1D._combine_result(results)
        combined_result['signal_eval'] = []
        for data, ref, result in zip(data_list, ref_list, results):
            start, end = result['min_loc'], result['min_loc'] + result['min_width']
            signal_eval = data[start:end].sum() - ref[start:end].sum()
            combined_result['signal_eval'].append(signal_eval)
        return combined_result

    @staticmethod
    def _scan_hist_multi(
        data_list: Union[np.ndarray, List[np.ndarray]],
        ref_list: Union[np.ndarray, List[np.ndarray]],
        widths: np.ndarray,
        binning_list: List[Binning],
        mode: Union[str, BumpHuntMode] = 'excess',
        scan_step: Union[str, int] = 1,
        use_sideband: bool = False,
        sideband_width: Optional[int] = None,
        detailed: bool = True
    ) -> Dict[str, Any]:
        """
        Scan a distribution in multiple channels and compute the p-value associated to every scan window.

        The algorithm follows the BumpHunter algorithm extended to multiple channels.
        """
        widths = np.asarray(widths)

        if not len(data_list):
            raise ValueError(f'Data list is empty.')
        if not len(ref_list):
            raise ValueError(f'Reference list is empty.')

        if not isinstance(data_list, (list, np.ndarray)):
            raise ValueError(f'Multi-channel data histograms must be a list of 1D arrays or 2D arrays of shape '
                             f'(nchannel, nbins), got {type(data_list).__name__} instead.')
        if not isinstance(ref_list, (list, np.ndarray)):
            raise ValueError(f'Multi-channel reference histograms must be a list of 1D arrays or 2D arrays of shape '
                             f'(nchannel, nbins), got {type(ref_list).__name__} instead.')
        if len(data_list) != len(ref_list):
            raise ValueError(f'Number of channels for data (= {len(data_list)}) and reference (= {len(ref_list)}) histograms must be equal.')
        if len(data_list) != len(binning_list):
            raise ValueError(f'Number of channel binnings (= {len(binning_list)}) must equal the number of channels (= {len(data_list)})')

        data_list = [np.asarray(data) for data in data_list]
        ref_list = [np.asarray(ref) for ref in ref_list]
        nchannel = len(data_list)

        for i, (data, ref) in enumerate(zip(data_list, ref_list)):
            if np.ndim(data) != 1:
                raise ValueError(f'(Channel {i + 1}) Target histogram must be one-dimensional, got {np.ndim(data)} instead.')
            if np.ndim(ref) != 1:
                raise ValueError(f'(Channel {i + 1}) Reference histogram must be one-dimensional, got {np.ndim(ref)} instead.')
            if data.shape != ref.shape:
                raise ValueError(f'Inconsistent shapes between data (= {data.shape}) and reference (= {ref.shape}) histograms in channel {i + 1}.')

        if nchannel == 1:
            return BumpHunt1D._scan_hist(data_list[0], ref_list[0],
                                           widths=widths,
                                           mode=mode,
                                           scan_step=scan_step,
                                           use_sideband=use_sideband,
                                           sideband_width=sideband_width,
                                           detailed=detailed)

        if not use_sideband:
            sideband_width = None

        def get_loc_right(res: Dict[str, Any]) -> float:
            return res['min_loc'] + res['min_width']

        results = []
        for channel_idx in range(len(data_list)):
            data = data_list[channel_idx]
            ref = ref_list[channel_idx]
            result = BumpHunt1D._scan_hist(
                data, ref, widths,
                mode=mode,
                scan_step=scan_step,
                use_sideband=use_sideband,
                sideband_width=sideband_width
            )
            results.append(result)

            if channel_idx == 0:
                continue

            result_prev = results[channel_idx - 1]

            # get the right edge of the bump
            loc_right_curr = get_loc_right(result)
            loc_right_prev = get_loc_right(result_prev)

            binning_curr = binning_list[channel_idx]
            binning_prev = binning_list[channel_idx - 1]
            bin_edges_curr = binning_curr.bin_edges
            bin_edges_prev = binning_prev.bin_edges

            # no overlap, we can break the loop
            if (bin_edges_curr[loc_right_curr] <= bin_edges_prev[result_prev['min_loc']] or
                bin_edges_curr[result['min_loc']] >= bin_edges_prev[loc_right_prev]):
                combined_result = BumpHunt1D._default_result_multi(data_list, ref_list, widths, sideband_width)
                break
            # there is an overlap, we can update the global results
            else:
                # check left bound of overlap interval
                if bin_edges_curr[result['min_loc']] < bin_edges_prev[result_prev['min_loc']]:
                    while bin_edges_curr[result['min_loc']] < bin_edges_prev[result_prev['min_loc']]:
                        result['min_loc'] += 1
                    result['min_loc'] -= 1
                # check right bound of overlap interval
                if bin_edges_curr[loc_right_curr] < bin_edges_prev[loc_right_prev]:
                    while bin_edges_curr[loc_right_curr] < bin_edges_prev[loc_right_prev]:
                        loc_right_curr -= 1
                    loc_right_curr += 1
                result['min_width'] = loc_right_curr - result['min_loc']
        else:
            combined_result = BumpHunt1D._combine_channel_result(data_list, ref_list, results)

        if not detailed:
            combined_result.pop('pval_arr')
            combined_result.pop('window_arr')
        return combined_result

    @staticmethod
    def _make_binned(data: np.ndarray, ref: np.ndarray, bins: Union[int, np.ndarray],
                     bin_range: Optional[ArrayLike] = None,
                     weights: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray, Binning]:
        ref_hist, edges = np.histogram(ref,
                                       bins=bins,
                                       range=bin_range,
                                       weights=weights)
        binning = Binning(bins=edges)
        data_hist, edges = np.histogram(data,
                                        bins=binning.bin_edges)
        return data_hist, ref_hist, binning

    @staticmethod
    def _validate_input(data: Union[np.ndarray, List[np.ndarray]],
                        ref: Union[np.ndarray, List[np.ndarray]],
                        weights: Optional[Union[np.ndarray, List[np.ndarray]]] = None) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        
        if not len(data):
            raise ValueError(f'Data array is empty.')
        if not len(ref):
            raise ValueError(f'Reference array is empty.')
            
        if np.ndim(data[0]) == 0:
            nchannel = 1
            data = [np.asarray(data)]
            ref = [np.asarray(ref)]
        elif np.ndim(data[0]) == 1:
            nchannel = len(data)
            data = [np.asarray(data_i) for data_i in data]
            ref = [np.asarray(ref_i) for ref_i in ref]
            if len(data) != len(ref):
                raise ValueError(f'Inconsistent number of channels between data (= {len(data)}) '
                                 f'and reference (= {len(ref)}).')
            if (weights is not None) and (len(weights) != nchannel):
                raise ValueError(f'Size of weights (= {len(weights)}) does not match the number of channels.')
        else:
            raise ValueError(f'Data distribution must be one-dimensional, got ndim = {np.ndim(data[0])} instead.')

        return data, ref, weights

    def bump_scan(
        self,
        data: Union[np.ndarray, List[np.ndarray]],
        ref: Union[np.ndarray, List[np.ndarray]],
        weights: Optional[Union[np.ndarray, List[np.ndarray]]] = None,
        binned: bool = False,
        do_pseudo: bool = True
    ) -> BumpHuntOutput1D:
        """
        Perform the full BumpHunter algorithm presented in https://arxiv.org/pdf/1101.0390.pdf without sidebands.
        This includes the generation of pseudo-data, the calculation of the BumpHunter p-value associated to data and to all pseudo experiment 
        as well as the calculation of the test statistic t.

        Arguments :
            data :
                The data distribution.
                If there is only one channel, it should be a numpy array containing the data distribution.
                Otherwise, it should be a list of numpy arrays (one per channel).
                The distribution(s) will be transformed into a binned histogram and the algorithm will look for the most significant excess.

            ref :
                The reference background distribution.
                If there is only one channel, it should be a numpy array containing the reference background distribution.
                Otherwise, it should be a list of numpy arrays (one per channel).
                The distribution(s) will be transformed into a binned histogram and the algorithm will compare it to data while looking for a bump.

            weights :
                An optional array of weights for the reference distribution.

            binned :
                Boolean that specifies if the given data and background are already in histogram form.
                If true, the data and background are considered as already 'histogramed'.
                Default to False.

            do_pseudo :
                Boolean specifying if pseudo data should be generated.
                If False, then the BumpHunter statistics distribution kept in memory is used to compute the global p-value and significance.
                If there is nothing in memory, the global p-value and significance will not be computed.
                Default to True.
        """
        
        # Set the seed if required (or reset it if None)
        np.random.seed(self.seed)

        data, ref, weights = BumpHunt1D._validate_input(data, ref, weights)
        nchannel = len(data)
            
        if binned:
            for i in range(nchannel):
                if data[i].shape != ref[i].shape:
                    raise ValueError(f'Inconsistent shapes between data (= {data[i].shape}) and reference '
                                     f'(= {ref[i].shape}) histograms in channel {i + 1}.')
                    
        default_bins = [self.bins] * nchannel
        if weights is None:
            weights = [None] * nchannel
        
        self.stdout.info('Generating histograms.')
        data_list, ref_list, binning_list, pseudo_list = [], [], [], []
        for i in range(nchannel):
            if not binned:
                data_hist, ref_hist, binning = self._make_binned(data[i], ref[i],
                                                                 bins=default_bins[i],
                                                                 bin_range=self.scan_range,
                                                                 weights=weights[i])

            else:
                data_hist = data[i]
                if weights[i] is not None:
                    ref_hist = ref[i] * weights[i]
                else:
                    ref_hist = ref[i]
                binning = default_bins[i]
            data_list.append(data_hist)
            ref_list.append(ref_hist)
            binning_list.append(binning)
            # generate pseudo-data histograms
            if do_pseudo:
                lam = np.tile(ref_hist, (self.npseudo, 1)).transpose()
                size = (ref_hist.size, self.npseudo)
                pseudo_hist = np.random.poisson(lam=lam, size=size)
                pseudo_list.append(pseudo_hist)
            
        if pseudo_list:
            pseudo_list = np.array(pseudo_list)
            # shape = (npseudo, nchannel, nbins)
            pseudo_list = np.transpose(pseudo_list, (2, 0, 1))
            # shape = (npseudo + 1, nchannel, nbins)
            all_data_list = np.concatenate([np.array([data_list]), pseudo_list])
            detailed = [True] + [False] * self.npseudo
        else:
            # shape = (1, nchannel, nbins)
            all_data_list = np.expand_dims(data_list, 0)
            detailed = [True]

        if nchannel > 1:
            bin_edges = binning_list[0].bin_edges
            for i in range(1, nchannel):
                if not np.allclose(bin_edges, binning_list[i].bin_edges):
                    raise RuntimeError('Inconsistent binnings across channels.')

        if self.width_max is None:
            width_max = data_list[0].size // 2
        else:
            width_max = self.width_max

        widths = np.arange(self.width_min, width_max + 1, self.width_step)
        self.stdout.info(f'Number of widths to be tested: {widths.size}')

        results = execute_multi_tasks(self._scan_hist_multi,
                                      all_data_list,
                                      repeat(ref_list),
                                      repeat(widths),
                                      repeat(binning_list),
                                      repeat(self.mode),
                                      repeat(self.scan_step),
                                      repeat(self.use_sideband),
                                      repeat(self.sideband_width),
                                      detailed,
                                      parallel=self.parallel,
                                      executor=self.executor)
        results = dict(self._combine_result(results))
        if not self.use_sideband:
            results.pop('norm_scale', None)

        if nchannel == 1:
            results['nll'] = - np.log(results['min_pval'])
        else:
            results['nll'] = - np.log(np.prod(results['min_pval'], axis=1))

        pval_arr = results.pop('pval_arr')[0]
        window_arr = results.pop('window_arr')[0]

        data_hists, ref_hists = [], []
        for data_binned, ref_binned, binning in zip(data_list, ref_list, binning_list):
            h_data = Histogram1D(data_binned, binning.bin_edges, error_mode='poisson')
            h_ref = Histogram1D(ref_binned, binning.bin_edges, error_mode='sumw2')
            data_hists.append(h_data)
            ref_hists.append(h_ref)
        output = BumpHuntOutput1D(results=results,
                                  data_pval_arr=pval_arr,
                                  data_window_arr=window_arr,
                                  data_hists=data_hists,
                                  ref_hists=ref_hists)

        global_pval = output.global_pval
        if global_pval is None:
            self.stdout.info('No pseudo data found : cannot compute global p-value')
        else:
            S, npseudo, significance = output.S, output.npseudo, output.significance
            self.stdout.info(f'Global p-value : {global_pval:1.4f} ({S} / {npseudo})')

            if global_pval == 1:
                self.stdout.info(f'Significance = {significance}')
            elif global_pval == 0:
                self.stdout.info(f'Significance > {significance:1.5f} (lower limit)')
            else:
                self.stdout.info(f'Significance = {significance:1.5f}')

        return output