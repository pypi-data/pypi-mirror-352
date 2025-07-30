from __future__ import annotations

from typing import Dict, List, Optional, Union, Any, TypeVar, Tuple

import pandas as pd
from matplotlib.axes import Axes

from quickstats.core import mappings as mp
from .core import PlotFormat, ErrorDisplayFormat
from .histogram_plot import HistogramPlot
from .colors import ColorType, ColormapType

class DataModelingPlot(HistogramPlot):

    STYLES_MAP = {
        'DATA': {
            'errorbar': {
                'marker': 'o',
                'linestyle': 'none'
            }
        },
        'MODEL': {
            # do not draw marker for models
            'errorbar': {
                'marker': 'none',
                'linestyle': '-',
                'elinewidth': 0,
                'capsize': 0
            },
            'masked_errorbar': {
                'marker': 'none',
                'linestyle': '--',
                'elinewidth': 0,
                'capsize': 0
            }
        }
    }

    CONFIG = {
        'plot_format': 'hist',
        'error_format': 'shade',
        'comparison_mode': 'ratio',
    }

    CONFIG_MAP = {
        'BINNED.DATA': {
            'plot_format': 'hist',
            'error_format': 'shade'
        },
        'BINNED.MODEL': {
            'plot_format': 'hist',
            'error_format': 'shade'
        },
        'BINNED.COMPARISON': {
            'plot_format': 'hist',
            'error_format': 'shade'
        },
        'ANALYTIC.DATA': {
            'plot_format': 'errorbar',
            'error_format': 'errorbar'
        },        
        'ANALYTIC.MODEL': {
            'plot_format': 'errorbar',
            'error_format': 'shade'
        },
        'ANALYTIC.COMPARISON': {
            'plot_format': 'errorbar',
            'error_format': 'errorbar'
        },           
    }

    def __init__(
        self,
        data_map: Union[T, Dict[str, T]],
        analytic_model: bool = False,
        color_cycle: Optional[ColormapType] = None,
        label_map: Optional[Dict[str, str]] = None,
        styles: Optional[Dict[str, Any]] = None,
        styles_map: Optional[Dict[str, Union[Dict[str, Any], str]]] = None,
        analysis_label_options: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None,
        config_map: Optional[Dict[str, Dict[str, Any]]] = None,
        figure_index: Optional[int] = None,
        verbosity: Union[int, str] = 'INFO'
    ) -> None:
        super().__init__(
            data_map=data_map,
            color_cycle=color_cycle,
            label_map=label_map,
            styles=styles,
            styles_map=styles_map,
            analysis_label_options=analysis_label_options,
            config=config,
            config_map=config_map,
            figure_index=figure_index,
            verbosity=verbosity
        )
        self.analytic_model = analytic_model
        
    def resolve_plot_options(
        self,
        targets: List[Optional[str]]
    ) -> Dict[str, Any]:
        data_targets = list(targets['DATA']) if targets['DATA'] else []
        model_targets = list(targets['MODEL']) if targets['MODEL'] else []
        if not data_targets and not model_targets:
            raise RuntimeError('No targets to draw')
        overlap_targets = set(data_targets).intersection(set(model_targets))
        if overlap_targets:
            raise RuntimeError(
                f'Found overlap between data targets and model targets: '
                f'{", ".join(overlap_targets)}'
            )
        self.reset_color_index()
        plot_options = {}
        scope = 'ANALYTIC' if self.analytic_model else 'BINNED'
        for domain, targets in [('DATA', data_targets),
                                ('MODEL', model_targets)]:
            default_plot_format = self.get_target_config('plot_format', f'{scope}.{domain}')
            default_error_format = self.get_target_config('error_format', f'{scope}.{domain}')
            for target in targets:
                target_config = self.config_map.get(target, {})
                plot_format = PlotFormat.parse(
                    target_config.get('plot_format') or default_plot_format
                )
                styles = self.get_target_styles(plot_format.artist, domain, merge=False)
                styles.update(self.get_target_styles(plot_format.artist, target, merge=False))
                styles.setdefault('label', self.label_map.get(target) or target)
                styles.setdefault('color', styles.get('color') or self.get_next_color())
    
                error_format = ErrorDisplayFormat.parse(
                    target_config.get('error_format') or default_error_format
                )
                error_styles = self.get_target_styles(error_format.artist, domain, merge=False)
                error_styles.update(self.get_target_styles(error_format.artist, target, merge=False))
                isolate_error_legend = self.get_target_config('isolate_error_legend', target)
                if isolate_error_legend:
                    error_target = self.label_map.format(target, 'error')
                    error_styles.setdefault('label', self.label_map.get(error_target) or error_target)
                else:
                    error_styles.setdefault('label', styles['label'])
                inherit_color = self.get_target_config('inherit_color', target)
                if inherit_color:
                    error_styles.setdefault('color', styles['color'])
                masked_styles = self.get_target_styles(
                    f'masked_{plot_format.artist}', domain, merge=False
                )
                masked_styles.update(self.get_target_styles(
                    f'masked_{plot_format.artist}', target, merge=False
                ))
                
                if masked_styles:
                    masked_target = self.label_map.format(target, 'masked')
                    masked_styles.setdefault('label', self.label_map.get(masked_target))
                masked_styles = masked_styles or None
                plot_options[target] = {
                    'plot_format': plot_format,
                    'error_format': error_format,
                    'styles': styles,
                    'masked_styles': masked_styles,
                    'error_styles': error_styles
                }
                
        return plot_options

    def resolve_comparison_options(
        self,
        comparison_options: Optional[Dict[str, Any]] = None,
        plot_options: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        if comparison_options is None:
            return None
        comparison_options = mp.concat((comparison_options,), copy=True)
        scope = 'ANALYTIC' if self.analytic_model else 'BINNED'
        default_plot_format = self.get_target_config('plot_format', f'{scope}.COMPARISON')
        default_error_format = self.get_target_config('error_format', f'{scope}.COMPARISON')
        comparison_options.setdefault('plot_format', default_plot_format)
        comparison_options.setdefault('error_format', default_error_format)
        return super().resolve_comparison_options(comparison_options, plot_options)

    def draw(
        self,
        data_targets: Optional[Union[str, List[str]]],
        model_targets: Optional[Union[str, List[str]]],
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        unit: Optional[str] = None,
        divide_bin_width: bool = False,
        normalize: bool = False,
        show_error: bool = True,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        ymin: Optional[float] = None,
        ymax: Optional[float] = None,
        ypad: float = 0.3,
        logx: bool = False,
        logy: bool = False,
        mask_condition: Optional[Union[Sequence[float], Callable]] = None,
        comparison_options: Optional[Dict[str, Any]] = None,
        legend_order: Optional[List[str]] = None,
        primary_target: Optional[List[str]] = None,        
    ) -> Union[Axes, Tuple[Axes, Axes]]:
        if isinstance(data_targets, str):
            data_targets = [data_targets]
        if isinstance(model_targets, str):
            model_targets = [model_targets]            
        targets = {
            'DATA': data_targets,
            'MODEL': model_targets
        }
        return super().draw(
            targets=targets,
            xlabel=xlabel,
            ylabel=ylabel,
            unit=unit,
            divide_bin_width=divide_bin_width,
            normalize=normalize,
            show_error=show_error,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            ypad=ypad,
            logy=logy,
            logx=logx,
            mask_condition=mask_condition,
            comparison_options=comparison_options,
            legend_order=legend_order,
            primary_target=primary_target,
        )