from __future__ import annotations

from typing import Dict, Optional, Union, List, Any
from collections import defaultdict

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from quickstats.core import mappings as mp
from .core import ErrorDisplayFormat
from .colors import ColormapType
from .multi_data_plot import MultiDataPlot
from .stat_plot_config import StatPlotConfig

PlotStyles = Dict[str, Any]
StatConfigs = List[StatPlotConfig]
TargetType = Optional[Union[str, List[Optional[str]]]]

class General1DPlot(MultiDataPlot):
    """
    Class for plotting general 1D data.
    """

    COLOR_CYCLE: str = 'default'

    STYLES: PlotStyles = {
        'plot': {
            'marker': 'o',
            'markersize': 8
        },
        'fill_between': {
            'alpha': 0.3,
            'hatch': None,
            'linewidth': 1.0,
        }
    }

    CONFIG: Dict[str, bool] = {
        'error_format': 'fill',
        'isolate_error_legend': False,
        'inherit_color': True,
        'error_on_top': False
    }

    def __init__(
        self,
        data_map: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        color_cycle: Optional[ColormapType] = None,
        label_map: Optional[Dict[str, str]] = None,
        styles: Optional[Union[PlotStyles, str]] = None,
        styles_map: Optional[Dict[str, Union[PlotStyles, str]]] = None,
        analysis_label_options: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None,
        config_map: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs
    ) -> None:
        """
        Initialize General1DPlot.

        Parameters
        ----------
        data_map : Union[pd.DataFrame, Dict[str, pd.DataFrame]]
            Data to plot, single DataFrame or dictionary of DataFrames
        color_cycle : Optional[ColormapType], default None
            Color cycle for plots
        label_map : Optional[Dict[str, str]], default None
            Mapping of targets to display labels
        styles : Optional[Union[PlotStyles,str]], default None
            Global plot styles
        styles_map : Optional[Dict[str, Union[PlotStyles, str]]], default None
            Target-specific style overrides
        analysis_label_options : Optional[Union[str, Dict[str, Any]]], default None
            Options for analysis labels
        config : Optional[Dict[str, Any]], default None
            Plot configuration parameters
        """
        self.stat_configs: Dict[Optional[str], StatConfigs] = {}
        super().__init__(
            data_map=data_map,
            color_cycle=color_cycle,
            label_map=label_map,
            styles=styles,
            styles_map=styles_map,
            config_map=config_map,
            analysis_label_options=analysis_label_options,
            config=config,
            **kwargs
        )

    def configure_stats(
        self,
        stat_configs: StatConfigs,
        targets: TargetType = None,
        extend: bool = True,
    ) -> None:
        """
        Configure statistical annotations for targets.

        Parameters
        ----------
        stat_configs : List[StatPlotConfig]
            Statistical configurations to apply
        targets : Optional[Union[str, List[Optional[str]]]], default None
            Targets to configure, if None applies to all
        extend : bool, default True
            Whether to extend existing configurations
        """
        if not isinstance(targets, list):
            targets = [targets]
            
        for target in targets:
            if extend and target in self.stat_configs:
                self.stat_configs[target].extend(stat_configs)
            else:
                self.stat_configs[target] = stat_configs
        
    def get_target_data(
        self,
        target: Optional[str],
        xattrib: str,
        yattrib: str,
        yerrloattrib: Optional[str] = None,
        yerrhiattrib: Optional[str] = None,
    ):
        if target not in self.data_map:
            raise ValueError(f'Target dataset does not exist: {target}')
        data = self.data_map[target].reset_index()
        x, y = data[xattrib].values, data[yattrib].values
        indices = np.argsort(x)
        x, y = x[indices], y[indices]

        if ((yerrloattrib and yerrloattrib in data) and 
            (yerrhiattrib and yerrhiattrib in data)):
            yerrlo = data[yerrloattrib].values[indices]
            yerrhi = data[yerrhiattrib].values[indices]
            yerr = (yerrlo, yerrhi)
        else:
            yerr = None
        return x, y, yerr

    def draw_single_target(
        self,
        ax: Axes,
        target: Optional[str],
        xattrib: str,
        yattrib: str,
        yerrloattrib: Optional[str] = None,
        yerrhiattrib: Optional[str] = None,
        draw_stats: bool = True,
        offset_error: bool = False,
        domain: Optional[str] = None,
        axis_index: int = 0
    ):
        
        x, y, yerr = self.get_target_data(
            target,
            xattrib=xattrib,
            yattrib=yattrib,
            yerrloattrib=yerrloattrib,
            yerrhiattrib=yerrhiattrib,
        )
            
        handles: Dict[str, Any] = {}
        styles = self.get_target_styles('plot', target)
        styles['label'] = self.label_map.get(target) or target
        # need to extract the first entry since we are drawing 1D data
        handles[target], = ax.plot(x, y, **styles)

        if yerr is not None:
            error_format = self.get_target_config('error_format', target)
            error_format = ErrorDisplayFormat.parse(error_format)
            error_styles = self.get_target_styles(error_format.artist, target)
            isolate_error_legend = self.get_target_config('isolate_error_legend', target)
            error_on_top = self.get_target_config('error_on_top', target)

            inherit_color = self.get_target_config('inherit_color', target)
            if inherit_color and ('facecolor' not in error_styles) and ('edgecolor' not in error_styles):
                error_styles.setdefault('color', handles[target].get_color())
            
            error_target = self.label_map.format(target, 'error')
            if (not isolate_error_legend) and (not error_on_top):
                error_styles['label'] = styles['label']
            else:
                error_styles['label'] = self.label_map.get(error_target) or error_target

            zorder = handles[target].get_zorder()
            error_styles.setdefault('zorder', zorder + (0.1 if error_on_top else -0.1))

            if error_format == ErrorDisplayFormat.ERRORBAR:
                if offset_error:
                    error_handle = ax.errorbar(x, y, yerr, **error_styles)
                else:
                    error_handle = ax.errorbar(x, y, (y - yerr[0], yerr[1] - y), **error_styles)
            elif error_format == ErrorDisplayFormat.FILL:
                if offset_error:
                    error_handle = ax.fill_between(x, y - yerr[0], y + yerr[1], **error_styles)
                else:
                    error_handle = ax.fill_between(x, yerr[0], yerr[1], **error_styles)
            else:
                raise RuntimeError(f'unsupported error format: {error_format.name}')

            
            if not isolate_error_legend:
                if error_on_top:
                    handles[target] = (handles[target], error_handle)
                else:
                    handles[target] = (error_handle, handles[target])
            else:
                handles[error_target] = error_handle

        stat_configs = self.stat_configs.get(target) if draw_stats else None
        if stat_configs:
            for i, stat_config in enumerate(stat_configs):
                stat_config.set_data(y)
                stat_handle = stat_config.apply(ax, handles[target])
                stat_target = self.legend_data.format(target, f"stat_handle_{i}")
                handles[stat_target] = stat_handle

        self.update_legend_handles(handles, domain=domain, ax=ax)
        self.legend_order.extend(handles.keys())

    def draw(
        self,
        xattrib: str,
        yattrib: str,
        yerrloattrib: Optional[str] = None,
        yerrhiattrib: Optional[str] = None,
        targets: Optional[List[str]] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        ymin: Optional[float] = None,
        ymax: Optional[float] = None,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        ypad: float = 0.3,
        logx: bool = False,
        logy: bool = False,
        draw_stats: bool = True,
        offset_error: bool = False,
        legend_order: Optional[List[str]] = None,
    ) -> Axes:
        """
        Draw complete plot with all datasets.

        Parameters
        ----------
        xattrib : str
            Column name for x values
        yattrib : str
            Column name for y values
        yerrloattrib : Optional[str], default None
            Column name for lower y errors
        yerrhiattrib : Optional[str], default None
            Column name for upper y errors
        targets : Optional[List[str]], default None
            Targets to plot
        xlabel : Optional[str], default None
            X-axis label
        ylabel : Optional[str], default None
            Y-axis label
        title : Optional[str], default None
            Title
        ymin, ymax : Optional[float], default None
            Y-axis limits
        xmin, xmax : Optional[float], default None
            X-axis limits
        ypad : float, default 0.3
            Y-axis padding fraction
        logx, logy : bool, default False
            Use logarithmic scale
        draw_stats : bool, default True
            Draw statistical annotations
        legend_order : Optional[List[str]], default None
            Custom legend order

        Returns
        -------
        matplotlib.axes.Axes
            The plotted axes
        """
        self.reset_metadata()
        ax = self.draw_frame(logx=logx, logy=logy)

        targets = self.resolve_targets(targets)
        for target in targets:
            self.draw_single_target(
                ax,
                target=target,
                xattrib=xattrib,
                yattrib=yattrib,
                yerrloattrib=yerrloattrib,
                yerrhiattrib=yerrhiattrib,
                draw_stats=draw_stats,
                offset_error=offset_error,
            )

        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, ypad=ypad)
        self.finalize()

        if title is not None:
            ax.set_title(title, **self.styles['title'])
            
        if self.config['draw_legend']:
            self.draw_legend(ax, targets=legend_order)

        return ax