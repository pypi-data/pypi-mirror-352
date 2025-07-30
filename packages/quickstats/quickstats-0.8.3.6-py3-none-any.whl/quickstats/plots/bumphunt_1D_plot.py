from typing import Dict, Optional, Union, List, Tuple

import pandas as pd
import numpy as np

from quickstats.plots import AbstractPlot
from quickstats.concepts import Histogram1D
from quickstats.utils.common_utils import combine_dict
from quickstats.plots.template import centralize_axis, create_transform, change_axis, remake_handles

class BumpHunt1DPlot(AbstractPlot):

    STYLES = {
        "legend": {
            "handletextpad": 0.3
        },
        "hist": {
            'histtype' : 'step',
            'linestyle': '-',
            'linewidth': 2
        },
        'errorbar': {
            "marker": 'none',
            "markersize": None,
            'linestyle': 'none',
            "linewidth": 0,
            "elinewidth": 2,
            "capsize": 0,
            "capthick": 0
        },
        'comp.hist': {
            'histtype' : 'stepfilled',
            'linestyle': '-',
            'linewidth': 2 ,
            'alpha': 0.5
        },
        'line_collection': {
            'linewidths': 2,
            'linestyle': '--'
        },
        'line': {
            'linewidth': 1,
            'color': 'gray',
            'linestyle': '--'            
        }
    }

    LABEL_MAP = {
        'bump': 'Bump',
        'data': 'Data',
        'ref': 'Reference',
        'sig': 'Significance'
    }

    CONFIG = {
        'xerr': True,
        'sigline': True,
        'box_legend_handle': False
    }
    
    def __init__(self,
                 data_hist: Histogram1D,
                 ref_hist: Histogram1D,
                 sig_hist: Optional[Histogram1D]=None,
                 color_cycle:Optional[Union[List, str, "ListedColorMap"]]=None,
                 label_map:Optional[Union[Dict, str]]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 verbosity:Optional[Union[int, str]]='INFO'):
        self.set_input(data_hist, ref_hist, sig_hist=sig_hist)
        super().__init__(color_cycle=color_cycle,
                         label_map=label_map,
                         styles=styles,
                         analysis_label_options=analysis_label_options,
                         verbosity=verbosity)

    def set_input(self, data_hist: Histogram1D,
                  ref_hist: Histogram1D,
                  sig_hist: Optional[Histogram1D]=None):
        assert isinstance(data_hist, Histogram1D)
        assert isinstance(ref_hist, Histogram1D)
        assert (sig_hist is None) or isinstance(sig_hist, Histogram1D)
        if data_hist.binning != ref_hist.binning:
            raise ValueError(f'`data_hist` and `ref_hist` must have the same binning')
        if (sig_hist is not None) and (sig_hist.binning != data_hist.binning):
            raise ValueError(f'`data_hist` and `sig_hist` must have the same binning')
        self.data_hist = data_hist
        self.ref_hist = ref_hist
        self.sig_hist = sig_hist

    def get_default_legend_order(self) -> List[str]:
        return ['data', 'ref', 'bump']
        
    def draw(self,
             xlabel: Optional[str] = None,
             ylabel: Optional[str] = None,
             title: Optional[str] = None,
             logy: bool = False,
             xmin: Optional[float] = None,
             xmax: Optional[float] = None,
             ymin: Optional[float] = None,
             ymax: Optional[float] = None,
             ypad: Optional[float] = None,
             normalize: bool = False,
             bump_edge: Optional[Tuple[float, float]] = None,
             ylim_sig: Optional[Tuple[float, float]] = None,
             ypad_sig: Optional[float] = 0.2,
             show_error: bool = True,
             show_sig: bool = True,
             show_bump: bool = True):

        data_hist = self.data_hist
        ref_hist = self.ref_hist
        sig_hist = self.sig_hist
        if normalize:
            data_hist = data_hist.normalize()
            ref_hist = ref_hist.normalize()

        if show_sig and (sig_hist is not None):
            ax, ax_ratio = self.draw_frame(frametype='ratio', logy=logy)
        else:
            ax = self.draw_frame(frametype='single', logy=logy)
            ax_ratio = None

        handle_map = {}
        label_map = self.label_map
        color_map = {
            'ref': next(self.color_cycle),
            'data': next(self.color_cycle),
            'sig': next(self.color_cycle),
            'bump': next(self.color_cycle)
        }

        styles = combine_dict({'color': color_map['ref'], 'label': label_map['ref']},
                              self.styles['hist'])
        _, _, ref_handle = ax.hist(x=ref_hist.bin_centers,
                                   bins=ref_hist.bin_edges,
                                   weights=ref_hist.bin_content,
                                   **styles)
        if not self.config['box_legend_handle']:
            ref_handle = remake_handles([ref_handle], polygon_to_line=True)[0]
        handle_map['ref'] = ref_handle

        xerr = data_hist.bin_widths / 2. if self.config['xerr'] else None
        styles = combine_dict({'color': color_map['data'], 'label': label_map['data']},
                              self.styles['errorbar'])
        data_handle = ax.errorbar(x=data_hist.bin_centers,
                                  y=data_hist.bin_content,
                                  xerr=xerr,
                                  yerr=data_hist.bin_errors,
                                  **styles)
        handle_map['data'] = data_handle

        if bump_edge is not None:
            styles = combine_dict({'colors': color_map['bump'], 'label': label_map['bump']},
                                  self.styles['line_collection'])
            with change_axis(ax):
                transform = create_transform(transform_x='data', transform_y='axis')
                bump_lines_handle = ax.vlines(bump_edge, ymin=0, ymax=1, 
                                              transform=transform, **styles)
                handle_map['bump'] = bump_lines_handle
            if ax_ratio is not None:
                with change_axis(ax_ratio):
                    transform = create_transform(transform_x='data', transform_y='axis')
                    comp_bump_lines_handle = ax_ratio.vlines(bump_edge, ymin=0, ymax=1,
                                                             transform=transform, **styles)

        if ax_ratio is not None:
            styles = combine_dict({'color': color_map['sig'], 'label': label_map['sig']},
                                  self.styles['comp.hist'])
            _, _, sig_handle = ax_ratio.hist(x=sig_hist.bin_centers,
                                             bins=sig_hist.bin_edges,
                                             weights=sig_hist.bin_content,
                                             **styles)
            handle_map['sig'] = sig_handle
            if ylim_sig is None:
                centralize_axis(ax_ratio, which="y", ref_value=0, padding=ypad_sig)
            else:
                ax_ratio.set_ylim(ylim_sig)

            if self.config['sigline']:
                ax_ratio.axhline(0, xmin=0, xmax=1, **self.styles['line'])
            self.draw_axis_components(ax_ratio, xlabel=xlabel, ylabel=self.label_map['sig'])

            self.draw_axis_components(ax, xlabel=None, ylabel=ylabel)
        else:
            self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)

        self.update_legend_handles(handle_map)
            
        self.set_axis_range(ax, xmin=xmin, xmax=xmax,
                            ymin=ymin, ymax=ymax, ypad=ypad)

        self.draw_legend(ax)
        
        self.reset_color_cycle()

        if ax_ratio is not None:
            return ax, ax_ratio
        return ax
