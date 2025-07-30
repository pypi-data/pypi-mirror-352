from typing import Dict, Optional, Union, List, Tuple
import pandas as pd
import numpy as np
from matplotlib.axes import Axes

from quickstats.plots import get_color_cycle, get_cmap

from quickstats.plots import General1DPlot, StatPlotConfig
from quickstats.plots.core import get_rgba
from quickstats.plots.template import create_transform, handle_has_label
from quickstats.utils.common_utils import combine_dict
from .core import ErrorDisplayFormat

class TwoPanel1DPlot(General1DPlot):

    STYLES = {
        'fill_between': {
             'alpha': 0.3,
             'hatch': None,
             'linewidth': 1.0
        },
        'ratio_frame':{
            'height_ratios': (1, 1),
            'hspace': 0.05           
        },
        'legend_lower': {
        }
    }

    CONFIG: Dict[str, bool] = {
        'error_format': 'fill',
        'isolate_error_legend': False,
        'inherit_color': True,
        'error_on_top': True
    }    
    
    def __init__(
        self,
        data_map:Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        label_map:Optional[Dict]=None,
        styles_map:Optional[Dict]=None,
        color_cycle=None,
        color_cycle_lower=None,
        styles:Optional[Union[Dict, str]]=None,
        analysis_label_options:Optional[Dict]=None,
        config:Optional[Dict]=None
    ):

        super().__init__(
            data_map=data_map,
            color_cycle=color_cycle,
            label_map=label_map,
            styles_map=styles_map,
            styles=styles,
            analysis_label_options=analysis_label_options,
            config=config
        )
        if color_cycle_lower is not None:
            self.cmap_lower = get_cmap(color_cycle_lower)
        else:
            self.cmap_lower = None

    def draw(
        self,
        xattrib:str,
        yattrib_upper:str,
        yattrib_lower:str,
        targets_upper:Optional[List[str]],
        targets_lower:Optional[List[str]],
        yerrloattrib_upper:Optional[str]=None,
        yerrhiattrib_upper:Optional[str]=None,
        yerrloattrib_lower:Optional[str]=None,
        yerrhiattrib_lower:Optional[str]=None,
        offset_error: bool = False,
        xlabel:Optional[str]=None,
        xmin:Optional[float]=None,
        xmax:Optional[float]=None,
        ylabel_upper:Optional[str]=None,
        ylabel_lower:Optional[str]=None,
        ymin_lower:Optional[float]=None,
        ymin_upper:Optional[float]=None,
        ymax_lower:Optional[float]=None,
        ymax_upper:Optional[float]=None,
        ypad_upper:Optional[float]=0.3,
        ypad_lower:Optional[float]=0.3,
        title: Optional[str] = None,
        logx:bool=False,
        logy_upper:bool=False,
        logy_lower:bool=False,
        legend_order_upper: Optional[List[str]] = None,
        legend_order_lower: Optional[List[str]] = None
    ):

        self.reset_metadata()

        if self.cmap_lower is not None:
            prop_cycle_lower = get_color_cycle(self.cmap_lower)
        else:
            prop_cycle_lower = None
        ax_upper, ax_lower = self.draw_frame(
            logx=logx,
            logy=logy_upper,
            logy_lower=logy_lower,
            prop_cycle_lower=prop_cycle_lower,
            frametype='ratio'
        )

        for (domain, ax, targets, yattrib,
             yerrloattrib, yerrhiattrib) in [
            ('upper', ax_upper, targets_upper, yattrib_upper, yerrloattrib_upper, yerrhiattrib_upper),
            ('lower', ax_lower, targets_lower, yattrib_lower, yerrloattrib_lower, yerrhiattrib_lower)
        ]:
            for target in targets:
                self.draw_single_target(
                    ax,
                    target=target,
                    xattrib=xattrib,
                    yattrib=yattrib,
                    yerrloattrib=yerrloattrib,
                    yerrhiattrib=yerrhiattrib,
                    offset_error=offset_error
                )

        self.draw_axis_components(ax_upper, ylabel=ylabel_upper, title=title)
        ax_upper.tick_params(axis='x', labelbottom=False)
        self.draw_axis_components(ax_lower, xlabel=xlabel, ylabel=ylabel_lower)
        self.set_axis_range(ax_upper, xmin=xmin, xmax=xmax,
                            ymin=ymin_upper, ymax=ymax_upper, ypad=ypad_upper)
        self.set_axis_range(ax_lower, xmin=xmin, xmax=xmax,
                            ymin=ymin_lower, ymax=ymax_lower, ypad=ypad_lower)

        if title is not None:
            ax.set_title(title, **self.styles['title'])
            
        if self.config['draw_legend']:
            self.draw_legend(
                ax_upper,
                targets=legend_order_upper,
                **self.styles['legend']
            )
            self.draw_legend(
                ax_lower,
                targets=legend_order_lower,
                **self.styles['legend_lower']
            )
        return ax_upper, ax_lower

