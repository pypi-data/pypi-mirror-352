from typing import Dict, Optional, Union, List, Tuple
import pandas as pd
import numpy as np

from quickstats.plots import AbstractPlot

class General1DPlot(AbstractPlot):

    STYLES = {
    }
    
    CONFIG = {
    }
    
    def __init__(self, data_map:Union[pd.DataFrame, Dict[str, pd.DataFrame]],
                 label_map:Optional[Dict]=None,
                 styles_map:Optional[Dict]=None,
                 color_cycle=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 config:Optional[Dict]=None):
        
        self.data_map = data_map
        self.styles_map = styles_map
        
        super().__init__(color_cycle=color_cycle,
                         label_map=label_map,
                         styles=styles,
                         analysis_label_options=analysis_label_options,
                         config=config)
        
    def get_default_legend_order(self):
        if not isinstance(self.data_map, dict):
            return []
        else:
            return list(self.data_map)
        
    def draw_single_data(self, ax, data:pd.DataFrame,
                         xattrib:str, yattrib:str,
                         yerrloattrib:Optional[str]=None,
                         yerrhiattrib:Optional[str]=None,
                         stat_configs:Optional[List[StatPlotConfig]]=None,
                         styles:Optional[Dict]=None,
                         label:Optional[str]=None):
        pass

    # issue of coloring
    def draw(self, yattrib:str, *xattribs,
             targets:Optional[List]=None,
             target_alignment:str="vertical",
             width:float=1, spacing:float=0.1,
             xlabel:Optional[str]=None, ylabel:Optional[str]=None,
             ypad:Optional[float]=0.3, logy:bool=False):
        
        ax = self.draw_frame(logx=logx, logy=logy)
        
        legend_order = []
        if isinstance(self.data_map, pd.DataFrame):
            if draw_stats and (None in self.stat_configs):
                stat_configs = self.stat_configs[None]
            else:
                stat_configs = None
            handle, stat_handles = self.draw_single_data(ax, self.data_map,
                                                         xattrib=xattrib,
                                                         yattrib=yattrib,
                                                         yerrloattrib=yerrloattrib,
                                                         yerrhiattrib=yerrhiattrib,
                                                         stat_configs=stat_configs,
                                                         styles=self.styles_map)
        elif isinstance(self.data_map, dict):
            if targets is None:
                targets = list(self.data_map.keys())
            if self.styles_map is None:
                styles_map = {k:None for k in self.data_map}
            else:
                styles_map = self.styles_map
            if self.label_map is None:
                label_map = {k:k for k in self.data_map}
            else:
                label_map = self.label_map
            handles = {}
            for target in targets:
                data = self.data_map[target]
                styles = styles_map.get(target, None)
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
        self.draw_legend(ax)
        
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, ypad=ypad)
        
        return ax
