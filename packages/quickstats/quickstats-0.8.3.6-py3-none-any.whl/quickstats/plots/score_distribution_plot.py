from typing import Optional, Union, Dict, List

import pandas as pd
import numpy as np

from matplotlib import colors
from matplotlib.ticker import MaxNLocator
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

from quickstats.maths.statistics import poisson_interval
from quickstats.utils.common_utils import combine_dict
from quickstats.plots import AbstractPlot
from quickstats.plots.template import create_transform, format_axis_ticks

class ScoreDistributionPlot(AbstractPlot):
    
    CONFIG = {
        "boundary_style": {
            "ymin": 0,
            "ymax": 0.4,
            "linestyle": "--",
            "color": "k"
        }
    }
    
    def __init__(self, data_map:Dict[str, pd.DataFrame], plot_options:Dict[str, Dict],
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 config:Optional[Dict]=None):
        """
        Arguments:
            plot_options: dicionary
                A dictionary containing plot options for various group of samples.
                Format: { <sample_group>: {
                            "samples": <list of sample names>,
                            "styles": <options in mpl.hist>},
                            "type": "hist" or "errorbar"
                          ...}
             
        """
        self.data_map = data_map
        self.plot_options = plot_options
        super().__init__(styles=styles,
                         analysis_label_options=analysis_label_options,
                         config=config)
    
    def draw(self, column_name:str="score", weight_name:Optional[str]="weight",
             xlabel:str="Score", ylabel:str="Fraction of Events / {bin_width:.2f}",
             boundaries:Optional[List]=None, nbins:int=25, xmin:float=0, xmax:float=1,
             ymin:float=0, ymax:float=1, logy:bool=False):
        """
        
        Arguments:
            column_name: string, default = "score"
                Name of the score variable in the dataframe.
            weight_name: (optional) string, default = "weight"
                If specified, normalize the histogram by the "weight_name" variable
                in the dataframe.
            xlabel: string, default = "Score"
                Label of x-axis.
            ylabel: string, default = "Fraction of Events / {bin_width}"
                Label of y-axis.
            boundaries: (optional) list of float
                If specified, draw score boundaries at given values.
            nbins: int, default = 25
                Number of histogram bins.
            xmin: float, default = 0
                Minimum value of x-axis.
            xmax: float, default = 1
                Maximum value of x-axis.
            ymin: float, default = 0
                Minimum value of y-axis.
            ymax: float, default = 1
                Maximum value of y-axis.
            logy: bool, default = False
                Draw y-axis with log scale.
        """
        ax = self.draw_frame(logy=logy)
        for key in self.plot_options:
            samples = self.plot_options[key]["samples"]
            plot_style  = self.plot_options[key].get("styles", {})
            df = pd.concat([self.data_map[sample] for sample in samples], ignore_index = True)
            if weight_name is not None:
                norm_weights = df[weight_name] / df[weight_name].sum()
            else:
                norm_weights = None
            plot_type = self.plot_options[key].get("type", "hist")
            if plot_type == "hist":
                y, x, _ = ax.hist(df[column_name], nbins, range=(xmin, xmax),
                                  weights=norm_weights, **plot_style, zorder=-5)
            elif plot_type == "errorbar":
                n_data = len(df[column_name])
                norm_weights = np.ones((n_data,)) / n_data
                y, bins = np.histogram(df[column_name], nbins,
                                       range=(xmin, xmax),
                                       weights=norm_weights)
                bin_centers  = 0.5*(bins[1:] + bins[:-1])
                yerrlo, yerrhi = poisson_interval(y * n_data)
                ax.errorbar(bin_centers, y, 
                            yerr=(yerrlo / n_data, yerrhi / n_data),
                            **plot_style)
            else:
                raise RuntimeError(f'unknown plot type: {plot_type}')
                
        bin_width = (xmax - xmin) / nbins
        ylabel = ylabel.format(bin_width=bin_width)
        
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        
        if not logy:
            ax.yaxis.set_major_locator(MaxNLocator(prune='lower', steps=[10]))
            ax.xaxis.set_major_locator(MaxNLocator(steps=[10]))

        handles, labels = ax.get_legend_handles_labels()
        new_handles = [Line2D([], [], c=h.get_edgecolor(), linestyle=h.get_linestyle(),
                              **self.styles['legend_Line2D']) if isinstance(h, Polygon) else h for h in handles]
        self.draw_legend(ax, handles=new_handles, labels=labels)
        if boundaries is not None:
            for boundary in boundaries:
                ax.axvline(x=boundary, **self.config["boundary_style"])
        return ax