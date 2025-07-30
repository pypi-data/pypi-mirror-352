from typing import Dict, Optional, Union, List, Tuple
import pandas as pd
import numpy as np

from quickstats.utils.common_utils import combine_dict
from quickstats.maths.numerics import to_string
from quickstats.plots import AbstractPlot, get_cmap_rgba

class SamplePurityPlot(AbstractPlot):
    
    STYLES = {
        'figure':{
            'figsize': (15.111, 20.333),
            'dpi': 200
        },
        'axis': {
            'major_length': 8,
            'minor_length': 0,
            'major_width': 1,
            'minor_width': 0,
            'labelsize': 12,
            'tick_bothsides': False,
            'direction': 'out'
        },
        'xlabel': {
            'fontsize': 12,
            'loc' : 'right',
            'labelpad': 3
        },
        'ylabel': {
            'fontsize': 12,
            'loc' : 'top',
            'labelpad': 10
        },
        'barh':{
            'height': 0.8
        },
        'legend':{
            'ncol': 'auto',
            'bbox_to_anchor': (0, 1),
            'loc': 'lower left',
            'fontsize': 10
        }
    }
    
    CONFIG = {
        'fig_bar_width': 12,
        'fig_bar_height': 0.5
    }
    
    def __init__(self, data:pd.DataFrame,
                 color_cycle:Optional[Union[List, str, "ListedColorMap"]]="simple_contrast",
                 sample_label_map:Optional[Dict]=None,
                 category_label_map:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None):
        super().__init__(color_cycle=color_cycle,
                         styles=styles,
                         analysis_label_options=analysis_label_options)
        assert isinstance(data, pd.DataFrame)
        self.data = data
        self.sample_label_map = sample_label_map
        self.category_label_map = category_label_map
        
    def get_text_color(self, r:float, g:float, b:float, a:float):
        return 'white' if r * g * b < 0.5 else 'darkgrey'
        
    def draw(self, xlabel:Optional[str]=None,
             ylabel:Optional[str]=None,
             samples:Optional[List[str]]=None,
             categories:Optional[List[str]]=None,
             figsize:Optional[Union[Tuple, List, str]]='auto',
             height:Optional[float]=None, add_text:bool=True,
             precision:int=1, threshold:float=2):
        df = self.data
        sample_label_map = self.sample_label_map if self.sample_label_map is not None else {}
        category_label_map = self.category_label_map if self.category_label_map is not None else {}
        if samples is None:
            samples = df.index
        else:
            df = df.loc[samples]
        samples = [sample_label_map.get(sample, sample) for sample in samples]
        if categories is None:
            categories = df.columns
        else:
            df = df[categories]
        categories = [category_label_map.get(category, category) for category in categories]
        data = df.div(df.sum(axis=1), axis=0).mul(100, axis=0).to_numpy()
        data_cumsum = data.cumsum(axis=1)
        colors = get_cmap_rgba(self.cmap, df.shape[1], resample=False)
        ax = self.draw_frame()
        if figsize is not None:
            if figsize == 'auto':
                fig_width = self.config['fig_bar_width']
                fig_height = self.config['fig_bar_height'] * len(samples)
            else:
                fig_width, fig_height = figsize
            self.figure.set_size_inches(fig_width, fig_height, forward=True)
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel,
                                  xticks=[], xticklabels=[],
                                  yticks=range(len(samples)), yticklabels=samples,
                                  xlim=(0, 100))
        if height is None:
            barh_styles = combine_dict(self.styles['barh'])
        else:
            barh_styles = combine_dict(self.styles['barh'], {"height": height})
        height = barh_styles['height']
        padding = 1 - height
        ax.set_ylim(0 - height / 2 - padding, len(samples) - 1 + height / 2 + padding)
        for i, (colname, color) in enumerate(zip(categories, colors)):
            widths = data[:, i]
            starts = data_cumsum[:, i] - widths
            ax.barh(samples, widths, left=starts, label=colname,
                    color=color, **barh_styles)
            xcenters = starts + widths / 2
            text_color = self.get_text_color(*color)
            if add_text:
                for y, (x, c) in enumerate(zip(xcenters, widths)):
                    if c < threshold:
                        continue
                    ax.text(x, y, to_string(c, precision), ha='center', va='center',
                            color=text_color)
        if (('ncol' in self.styles['legend']) and
            (self.styles['legend']['ncol'] == 'auto')):
            legend_styles = {"ncol": len(categories)}
        else:
            legend_styles = {}
        
        self.draw_legend(ax, **legend_styles)
        
        return ax
    