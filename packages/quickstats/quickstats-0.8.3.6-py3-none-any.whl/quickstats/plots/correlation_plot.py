import os
import yaml
from typing import Optional, Dict, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from quickstats.plots import AbstractPlot
from quickstats.utils.common_utils import combine_dict
from .template import format_axis_ticks
from .colors import get_color_brightness, inverse_brightness_color

STYLES = {
    "default": {
        'cmap': 'seismic',
        'value_color': 'black'
    },
    "viridis": {
        'cmap': 'viridis',
        'value_color': 'black'
    }
}

class CorrelationPlot(AbstractPlot):

    STYLES = {
        'axis': {
            'major_length': 0,
            'minor_length': 0,
            'major_width': 0,
            'minor_width': 0
        },
        'xlabel': {
            'loc' : 'center'
        },
        'ylabel': {
            'loc' : 'center'
        },
        'title':{
            'fontsize': 20,
            'loc': 'center',
            'pad': 10
        },
        'colorbar': {
        },
        'colorbar_label': {
            'labelpad': 10
        },
        'colorbar_axis': {}
    }
    
    CONFIG = {
        'cax_kwargs': {
            'position': 'right',
            'size': '5%',
            'pad' : 0.05
        }
    }
    
    def __init__(self, data:pd.DataFrame, label_map:Optional[Dict]=None,
                 styles: Optional[Union[Dict, str]] = None,
                 config: Optional[Dict] = None):
        
        self.data = data
        super().__init__(label_map=label_map,
                         styles=styles,
                         config=config)        
        
    @staticmethod
    def parse_style(style:Optional[str]=None):
        if not style:
            return STYLES["default"]
        elif isinstance(style, dict):
            return style
        if os.path.exists(style):
            return yaml.safe_load(open(style))
        _style = STYLES.get(style.lower(), None)
        if not _style:
            raise ValueError(f'unknown style: {style}')
        return _style
        
    def draw(self, cmap:str='seismic', xlabel_rotation:float=90, ylabel_rotation:float=0, label_size:float=25,
             figscale:int=1, show_values:bool=True, value_color:str="auto", value_size=16, value_precision:int=2,
             gridline:Optional[str]="--", gridcolor:str="black", title:Optional[str]=None,
             xlabel:Optional[str]=None, ylabel:Optional[str]=None, xlabelpad:Optional[float]=None,
             ylabelpad:Optional[float]=None, xlabelpos:str="top", ylabelpos="left",
             vmin:float=-1, vmax:float=1, norm:Optional=None, draw_colorbar:bool=False,
             colorbar_label: Optional[str] = None):
        if norm is not None:
            vmin, vmax = None, None
        if self.label_map is None:
            label_map = {}
        else:
            label_map = combine_dict(self.label_map)
        plt.clf()
        size = np.max([len(self.data.columns), len(self.data.index)])
        figsize = size * figscale
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(figsize, figsize), facecolor="#FFFFFF", dpi=72)
        
        handle = ax.matshow(self.data, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax)
        
        if draw_colorbar:
            figure = plt.gcf()
            from mpl_toolkits.axes_grid1 import make_axes_locatable
            divider = make_axes_locatable(ax)
            cax = divider.append_axes(**self.config['cax_kwargs'])
            cbar = figure.colorbar(handle, cax=cax, **self.styles['colorbar'])
            if colorbar_label:
                cbar.set_label(label=colorbar_label, **self.styles['colorbar_label'])
            format_axis_ticks(cax, **self.styles.get('colorbar_axis', {}))
        
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        
        xticks = np.arange(0, len(self.data.columns), 1)
        yticks = np.arange(0, len(self.data.index), 1)
        ax.set_xticks(xticks)
        ax.set_yticks(yticks)
        ax.set_xticklabels([label_map.get(label, label) for label in self.data.columns],
                           rotation=xlabel_rotation,
                           fontsize=label_size)
        if xlabelpad is not None:
            ax.tick_params(axis='x', which='major', pad=xlabelpad)
        ax.set_yticklabels([label_map.get(label, label) for label in self.data.index],
                           rotation=ylabel_rotation,
                           fontsize=label_size)
        if ylabelpad is not None:
            ax.tick_params(axis='y', which='major', pad=ylabelpad)
        
        ax.tick_params(axis="both", which="both", length=0)
        ax.xaxis.set_ticks_position(xlabelpos)
        ax.yaxis.set_ticks_position(ylabelpos)
        
        if show_values:
            fmt_str = f'{{:0.{value_precision}f}}'
            for (i, j), z in np.ndenumerate(self.data.values):
                if (value_color == "auto") or callable(value_color):
                    background_rgba = handle.cmap(handle.norm(z))
                    r, g, b, _ = background_rgba
                    brightness = get_color_brightness(r, g, b)
                    if callable(value_color):
                        text_color = value_color(brightness)
                    else:
                        text_color = inverse_brightness_color(brightness, 0.5)
                else:
                    text_color = value_color
                
                ax.text(j, i, fmt_str.format(z), 
                        ha='center', va='center', 
                        color=text_color, fontsize=value_size)
        
        if gridline:
            for i in range(len(yticks) - 1):
                ax.axhline(i + 0.5, linestyle=gridline, color=gridcolor)
            for i in range(len(xticks) - 1):
                ax.axvline(i + 0.5, linestyle=gridline, color=gridcolor)
        
        if title is not None:
            ax.set_title(title, **self.styles['title'])
        return ax
    
    def draw_style(self, style:Optional[Dict]=None):
        style = self.parse_style(style)
        return self.draw(**style)