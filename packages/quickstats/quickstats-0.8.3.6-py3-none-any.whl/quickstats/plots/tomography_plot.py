from typing import Dict, Optional, Union, List

import pandas as pd
import numpy as np
from matplotlib.collections import LineCollection

from quickstats.plots import AbstractPlot
from quickstats.utils.common_utils import combine_dict

class TomographyPlot(AbstractPlot):

    STYLES = {
        'line_collection': {
            'linewidths': 1,
            'colors': 'r'
        }
    }
    
    def __init__(self, data: pd.DataFrame,
                 color_cycle:Optional[Union[List, str, "ListedColorMap"]]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 verbosity:Optional[Union[int, str]]='INFO'):
        assert isinstance(data, pd.DataFrame)
        self.data = data
        super().__init__(color_cycle=color_cycle,
                         styles=styles,
                         analysis_label_options=analysis_label_options,
                         verbosity=verbosity)
        
    def draw(self,
             xloattrib: str,
             xhiattrib: str,
             yattrib: str,
             xlabel: Optional[str] = None,
             ylabel: Optional[str] = None,
             xmin: Optional[float] = None,
             xmax: Optional[float] = None,
             ymin: Optional[float] = None,
             ymax: Optional[float] = None,
             ypadlo: Optional[float] = 0.05,
             ypadhi: Optional[float] = 0.05,
             logy:  bool = False):
        
        ax = self.draw_frame(logy=logy)

        xlo_arr = self.data[xloattrib].values
        xhi_arr = self.data[xhiattrib].values
        y_arr = self.data[yattrib].values

        segments = []
        for xlo, xhi, y in zip(xlo_arr, xhi_arr, y_arr):
            segments.append([(xlo, y), (xhi, y)])

        line_collection = LineCollection(segments, **self.styles['line_collection'])

        data_xmin = np.min(xlo_arr)
        data_xmax = np.max(xhi_arr)
        data_ymin = np.min(y_arr)
        data_ymax = np.max(y_arr)
        ax.set_xlim(data_xmin, data_xmax)
        ax.set_ylim(data_ymin, data_ymax)

        ax.add_collection(line_collection)
            
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax,
                            ymin=ymin, ymax=ymax,
                            ypadlo=ypadlo, ypadhi=ypadhi)
        
        return ax
