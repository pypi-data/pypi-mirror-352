from typing import Dict, Optional, Union, List, Tuple

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from quickstats.core.typing import is_indexable_sequence
from quickstats.plots import General1DPlot
from quickstats.plots.settings import AXES_DOMAIN_FMT
from quickstats.utils.common_utils import combine_dict
from .colors import ColormapType

class MultiPanel1DPlot(General1DPlot):

    STYLES = {
        'fill_between': {
             'alpha': 0.3,
             'hatch': None,
             'linewidth': 1.0
        },
        'gridspec': {
            'height_ratios': None,
            'hspace': 0.05
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
        color_cycle:Optional[ColormapType]=None,
        color_cycle_map:Optional[Dict[str, ColormapType]]=None,
        label_map:Optional[Dict]=None,
        styles:Optional[Union[Dict, str]]=None,
        styles_map:Optional[Dict]=None,
        config:Optional[Dict]=None,
        config_map: Optional[Dict] = None,
        analysis_label_options:Optional[Dict]=None
    ) -> None:

        super().__init__(
            data_map=data_map,
            color_cycle=color_cycle,
            color_cycle_map=color_cycle_map,
            label_map=label_map,
            styles=styles,
            styles_map=styles_map,
            config=config,
            config_map=config_map,
            analysis_label_options=analysis_label_options
        )
        
    def draw(
        self,
        xattrib: str,
        yattribs: Union[str, List[str]],
        panel_targets: List[Union[str, List[str]]],
        yerrloattribs: Optional[Union[str, List[str]]] = None,
        yerrhiattribs: Optional[Union[str, List[str]]] = None,
        offset_error: bool = False,
        xlabel: Optional[str] = None,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        ylabels: Optional[Union[str, List[str]]] = None,
        ymins: Optional[Union[float, List[float]]] = None,
        ymaxs: Optional[Union[float, List[float]]] = None,
        ypads: Optional[Union[float, List[float]]] = None,
        title: Optional[str] = None,
        logx: bool = False,
        logys: Union[bool, List[bool]] = False,
        legend_order: Optional[List[str]] = None,
        height_ratios: Optional[List[float]] = None,
        hspace: Optional[float] = None
    ) -> Tuple[Axes, ...]:

        self.reset_metadata()

        nrows = len(panel_targets)

        gridspec = {}
        if height_ratios is not None:
            gridspec['height_ratios'] = height_ratios
        if hspace is not None:
            gridspec['hspace'] = hspace
        custom_styles = {
            'gridspec': gridspec
        }
        axes = self.draw_frame(
            nrows=nrows,
            frametype='multirow',
            logxs=logx,
            logys=logys,
            styles=custom_styles
        )
        if nrows == 1:
            axes = [axes]

        kwargs = {}
        for name, args in [('yattribs', yattribs),
                           ('yerrloattribs', yerrloattribs),
                           ('yerrhiattribs', yerrhiattribs),
                           ('ylabels', ylabels),
                           ('ymins', ymins),
                           ('ymaxs', ymaxs),
                           ('ypads', ypads)]:
            if not is_indexable_sequence(args):
                args = [args] * nrows
            if len(args) != nrows:
                raise ValueError(
                    f'`{name}` must be a string or a list of string with size matching the number of panels from `panel_targets`'
                )
            kwargs[name] = args

        for index, ax in enumerate(axes):
            targets = panel_targets[index]
            if isinstance(targets, str):
                targets = [targets]
            domain = AXES_DOMAIN_FMT.format(index=index)
            for target in targets:
                self.draw_single_target(
                    ax,
                    target=target,
                    xattrib=xattrib,
                    yattrib=kwargs['yattribs'][index],
                    yerrloattrib=kwargs['yerrloattribs'][index],
                    yerrhiattrib=kwargs['yerrhiattribs'][index],
                    offset_error=offset_error,
                    domain=domain                    
                )

        self.finalize()
        
        for index, ax in enumerate(axes):
            ax_title = title if index == 0 else None
            self.draw_axis_components(ax, xlabel=xlabel, ylabel=kwargs['ylabels'][index], title=ax_title)
            self.set_axis_range(
                ax, xmin=xmin, xmax=xmax,
                ymin=kwargs['ymins'][index],
                ymax=kwargs['ymaxs'][index],
                ypad=kwargs['ypads'][index]
            )
            
        if self.config['draw_legend']:
            for index, ax in enumerate(axes):
                domain = AXES_DOMAIN_FMT.format(index=index)
                legend_styles = self.get_target_styles(
                    'legend',
                    target=domain,
                    merge=True
                )
                self.draw_legend(
                    ax,
                    domains=domain,
                    targets=legend_order,
                    **legend_styles
                )
        
        return axes