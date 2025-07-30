from __future__ import annotations

from typing import Dict, Optional, Union, List, Tuple, Any

import pandas as pd
import numpy as np

from quickstats.core import mappings as mp
from quickstats.maths.interpolation import get_intervals
from .general_1D_plot import General1DPlot
from .likelihood_mixin import LikelihoodMixin
from .template import create_transform
from .colors import ColormapType

class Likelihood1DPlot(LikelihoodMixin, General1DPlot):
    """
    Class for plotting 1D likelihood scans with confidence levels.
    """

    DOF: int = 1
    COLOR_CYCLE: str = "atlas_hdbs"
    
    STYLES: Dict[str, Any] = {
        'plot': {
            'marker': 'none'
        },
        'annotate': {
            'fontsize': 20
        },
        'text': {
            'fontsize': 20
        },
        'level_line': {
            'color': 'gray',
            'linestyle': '--'
        },
        'level_text': {
            'x': 0.98,
            'ha': 'right',
            'color': 'gray'            
        },
        'level_interval': {
            'loc': (0.2, 0.4),
            'main_text': '',
            'interval_text': r'{level_label}: {xlabel}$\in {intervals}$',
            'dy': 0.05,
            'decimal_place': 2            
        }
    }
    
    LABEL_MAP = {
        'confidence_level': '{level:.0%} CL',
        'sigma_level': r'{level:.0g} $\sigma$',
    }

    CONFIG = {
        'level_key': {
            'confidence_level': '{level_str}_CL',
            'sigma_level': '{level_str}_sigma',
        }
    }    

    def __init__(
        self,
        data_map: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        color_cycle: Optional[ColormapType] = None,
        label_map: Optional[Dict[str, str]] = None,
        styles: Optional[Dict[str, Any]] = None,
        styles_map: Optional[Dict[str, Dict[str, Any]]] = None,
        analysis_label_options: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        self.intervals: Dict[str, List[Tuple[float, float]]] = {}
        super().__init__(
            data_map=data_map,
            color_cycle=color_cycle,
            label_map=label_map,
            styles=styles,
            styles_map=styles_map,
            analysis_label_options=analysis_label_options,
            config=config
        )

    def reset_metadata(self) -> None:
        """Reset plot metadata."""
        super().reset_metadata()
        self.intervals.clear()

    def get_bestfit(self, x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
        """Find the best fit point (minimum of likelihood)."""
        bestfit_idx = np.argmin(y)
        return x[bestfit_idx], y[bestfit_idx]
        
    def get_intervals(self, x:np.ndarray, y:np.ndarray,
                      level_specs: Optional[List[Dict[str, Any]]] = None):
        if not level_specs:
            return
        intervals = {}
        for key, spec in level_specs.items():
            intervals[key] = get_intervals(x, y, spec['chi2'])
        return intervals        

    def draw_level_lines(
        self,
        ax: Any,
        level_specs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """Draw horizontal lines indicating confidence/sigma levels."""
        if not level_specs:
            return

        line_styles = mp.concat((self.styles['line'], self.styles['level_line']), copy=True)
        text_styles = mp.concat((self.styles['text'], self.styles['level_text']), copy=True)
        
        x_pos = text_styles.get('x', 0.98)
        text_styles.setdefault('va', 'bottom' if (0 < x_pos < 1) else 'center')
        transform = create_transform(transform_x="axis", transform_y="data")
        
        for spec in level_specs.values():
            ax.hlines(spec['chi2'], xmin=0, xmax=1, zorder=0,
                     transform=transform, **line_styles)
            ax.text(y=spec['chi2'], s=spec['label'],
                   transform=transform, **text_styles)
    
    def draw_level_intervals(
        self,
        ax: Any,
        x: np.ndarray,
        y: np.ndarray,
        xlabel: str = "",
        level_specs: Optional[Dict[str, Dict[str, Any]]] = None,
        domain: Optional[str] = None
    ) -> None:
        """Draw confidence/sigma interval annotations."""
        if not level_specs:
            return
            
        self.intervals = self.get_intervals(x, y, level_specs)
        # do not draw when no intervals available
        if all(not len(intervals) for intervals in self.intervals.values()):
            return
            
        styles = self.styles['level_interval']
        if domain is not None:
            domain_styles = self.styles_map.get(domain, {}).get('level_interval')
            styles = mp.concat((styles, domain_styles))

        ax.annotate(styles['main_text'], styles['loc'],
                   xycoords='axes fraction', **self.styles['annotate'])
        
        for i, (key, spec) in enumerate(level_specs.items()):
            intervals = self.intervals.get(key)
            if not len(intervals):
                continue
                
            interval_str = self._format_intervals(intervals, styles['decimal_place'])
            text = styles['interval_text'].format(
                level_label=spec['label'],
                xlabel=xlabel,
                intervals=interval_str
            )
            
            y_pos = styles['loc'][1] - (i + 1) * styles['dy']
            ax.annotate(text, (styles['loc'][0], y_pos),
                       xycoords='axes fraction', **self.styles['annotate'])

    @staticmethod
    def _format_intervals(intervals: List[Tuple[float, float]], dp: int) -> str:
        """Format intervals for display."""
        parts = [f"[{lo:.{dp}f}, {hi:.{dp}f}]" for lo, hi in intervals]
        return r" \cup ".join(parts).replace('-inf', 'N.A.').replace('inf', 'N.A.')

    def draw(
        self,
        xattrib: str,
        yattrib: str = 'qmu',
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = r"$-2\Delta ln(L)$",
        title: Optional[str] = None,            
        targets: Optional[List[str]] = None,
        ymin: float = 0,
        ymax: float = 7,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        draw_level_lines: bool = True,
        draw_level_intervals: bool = False,
        sigma_levels: Optional[Tuple[float, ...]] = (1, 2),
        confidence_levels: Optional[Tuple[float, ...]] = None
    ) -> Any:
        """
        Draw likelihood profile plot.

        Parameters
        ----------
        xattrib : str
            Column name for x values
        yattrib : str, default 'qmu'
            Column name for likelihood values
        xlabel, ylabel : Optional[str]
            Axis labels
        title : Optional[str], default None
            Title            
        targets : Optional[List[str]]
            Targets to plot
        ymin, ymax : float
            Y-axis limits
        xmin, xmax : Optional[float]
            X-axis limits
        draw_level_lines : bool, default True
            Draw horizontal lines for confidence levels
        draw_level_intervals : bool, default False
            Draw confidence interval annotations
        sigma_levels : Optional[Tuple[float, ...]], default (1, 2)
            Sigma levels to indicate
        confidence_levels : Optional[Tuple[float, ...]]
            Confidence levels to indicate
        """
        
        targets = self.resolve_targets(targets)
        ax = super().draw(
            xattrib=xattrib,
            yattrib=yattrib,
            xlabel=xlabel,
            ylabel=ylabel,
            targets=targets,
            ymin=ymin,
            ymax=ymax,
            xmin=xmin,
            xmax=xmax
        )

        level_specs = self.get_level_specs(sigma_levels, confidence_levels)
        
        if draw_level_lines:
            self.draw_level_lines(ax, level_specs)

        if draw_level_intervals:
            for target in targets:
                data = self.data_map[target]
                self.draw_level_intervals(
                    ax,
                    data[xattrib].values,
                    data[yattrib].values,
                    xlabel=xlabel,
                    level_specs=level_specs,
                    domain=target
                )

        return ax