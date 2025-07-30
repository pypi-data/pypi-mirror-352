from typing import Dict, Optional, Union, List, Tuple
import pandas as pd
import numpy as np

from quickstats.plots import AbstractPlot, General1DPlot
from quickstats.utils.common_utils import combine_dict
from quickstats.plots.template import handle_has_label

class TwoAxis1DPlot(General1DPlot):
    
    def __init__(self, data_map:Union[pd.DataFrame, Dict[str, pd.DataFrame]],
                 **kwargs):
        super().__init__(data_map=data_map, **kwargs)
        
    def draw(self, xattrib:str, yattrib:str,
             targets_first:List[str],
             targets_second:List[str],
             yerrloattrib:Optional[str]=None,
             yerrhiattrib:Optional[str]=None,
             xlabel:Optional[str]=None,
             ylabel_first:Optional[str]=None,
             ylabel_second:Optional[str]=None,
             xmin:Optional[float]=None, xmax:Optional[float]=None,
             ymin_first:Optional[float]=None, ymax_first:Optional[float]=None,
             ymin_second:Optional[float]=None, ymax_second:Optional[float]=None,
             ypad_first:Optional[float]=0.3,
             ypad_second:Optional[float]=0.3,
             logx:bool=False,
             logy_first:bool=False,
             logy_second:bool=False,
             draw_stats:bool=True):
        
        ax1 = self.draw_frame(logx=logx, logy=logy_first)
        ax2 = ax1.twinx()
        if logy_second:
            ax2.set_yscale('log')
        
        legend_order = []
        if isinstance(self.data_map, dict):
            if self.styles_map is None:
                styles_map = {k:None for k in self.data_map}
            else:
                styles_map = self.styles_map
            if self.label_map is None:
                label_map = {k:k for k in self.data_map}
            else:
                label_map = self.label_map
            handles = {}
            for ax, targets in [(ax1, targets_first), (ax2, targets_second)]:
                for target in targets:
                    data = self.data_map[target]
                    styles = styles_map.get(target, None)
                    if styles is None:
                        styles = {}
                    label = label_map.get(target, "")
                    if draw_stats:
                        if target in self.stat_configs:
                            stat_configs = self.stat_configs[target]
                        elif None in self.stat_configs:
                            stat_configs = self.stat_configs[None]
                        else:
                            stat_configs = None
                    else:
                        stat_configs = None
                    if ('color' not in styles):
                        styles['color'] = next(self.color_cycle)
                    handle, stat_handles = self.draw_single_data(ax, data, 
                                                                 xattrib=xattrib,
                                                                 yattrib=yattrib,
                                                                 yerrloattrib=yerrloattrib,
                                                                 yerrhiattrib=yerrhiattrib,
                                                                 stat_configs=stat_configs,
                                                                 styles=styles,
                                                                 label=label)
                    handles[target] = handle
                    if stat_handles is not None:
                        for i, stat_handle in enumerate(stat_handles):
                            if handle_has_label(stat_handle):
                                handle_name = f"{target}_stat_handle_{i}"
                                handles[handle_name] = stat_handle
            legend_order.extend(handles.keys())
            self.update_legend_handles(handles)
        else:
            raise ValueError("invalid data format")
            
        self.legend_order = legend_order
        handles, labels = self.get_legend_handles_labels()
        ax1.legend(handles, labels, **self.styles['legend'])
        
        tmp_styles = combine_dict(self.styles)
        self.styles['axis']['y_axis_styles']['left'] = True
        self.styles['axis']['y_axis_styles']['labelleft'] = True
        self.styles['axis']['y_axis_styles']['right'] = False
        self.styles['axis']['y_axis_styles']['labelright'] = False
        self.draw_axis_components(ax1, xlabel=xlabel, ylabel=ylabel_first)
        self.styles['axis']['y_axis_styles']['left'] = False
        self.styles['axis']['y_axis_styles']['labelleft'] = False
        self.styles['axis']['y_axis_styles']['right'] = True
        self.styles['axis']['y_axis_styles']['labelright'] = True
        self.draw_axis_components(ax2, xlabel=xlabel, ylabel=ylabel_second)
        self.styles = tmp_styles
        self.set_axis_range(ax1, xmin=xmin, xmax=xmax, ymin=ymin_first, ymax=ymax_first, ypad=ypad_first)
        self.set_axis_range(ax2, xmin=xmin, xmax=xmax, ymin=ymin_second, ymax=ymax_second, ypad=ypad_second)
        
        return ax1, ax2