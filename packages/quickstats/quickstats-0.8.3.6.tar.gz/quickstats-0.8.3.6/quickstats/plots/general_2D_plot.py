from __future__ import annotations

from typing import Dict, Optional, Union, List, Tuple, Callable, Any, cast
from collections import defaultdict

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from quickstats.core import mappings as mp
from quickstats.maths.interpolation import interpolate_2d
from quickstats.maths.numerics import pivot_table
from .multi_data_plot import MultiDataPlot
from .template import (
    format_axis_ticks,
    convert_size,
    contour_to_shapes
)
from .colors import ColorType, ColormapType

class General2DPlot(MultiDataPlot):
    """
    Class for plotting general 2D data.
    
    Provides functionality for plotting 2D data with support for:
    - Colormesh plots
    - Contour plots (filled and unfilled)
    - Scatter plots
    - Multiple colorbars
    - Custom interpolation
    """

    COLOR_CYCLE: str = 'default'    
    
    STYLES: Dict[str, Any] = {
        'pcolormesh': {
            'cmap': 'plasma',
            'shading': 'auto',
            'rasterized': True
        },
        'colorbar': {
            'pad': 0.02,
        },
        'contour': {
            'linestyles': 'solid',
            'linewidths': 2
        },
        'contourf': {
            'alpha': 0.5,
            'zorder': 0 
        },
        'scatter': {
            'c': 'hh:darkpink',
            'marker': 'o',
            's': 40,
            'edgecolors': 'hh:darkblue',
            'alpha': 0.7,
            'linewidth': 1,
        },
        'legend': {
            'handletextpad': 0.5
        },
        'clabel': {
            'inline': True,
            'fontsize': 10
        },
        'axis_divider': {
            'position': 'right',
            'size': 0.3,
            'pad': 0.1
        }
    }
    
    CONFIG: Dict[str, Any] = {
        'interpolation': 'cubic',
        'num_grid_points': 500,
        'contour_shape': False,
        'alphashape_alpha': 2
    }    

    def __init__(
        self,
        data_map: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        color_map: Optional[Dict[str, ColorType]] = None,
        color_cycle: Optional[ColormapType] = None,
        label_map: Optional[Dict[str, str]] = None,
        styles: Optional[Dict[str, Any]] = None,
        styles_map: Optional[Dict[str, Union[Dict[str, Any], str]]] = None,
        analysis_label_options: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize General2DPlot with same parameters as MultiDataPlot."""
        self.Z_interp: Dict[Optional[str], np.ndarray] = {}
        self.axis_divider: Optional[Any] = None
        self.caxs: List[Axes] = []
        super().__init__(
            data_map=data_map,
            color_map=color_map,
            color_cycle=color_cycle,
            label_map=label_map,
            styles=styles,
            styles_map=styles_map,
            analysis_label_options=analysis_label_options,
            config=config,
        )

    def reset_metadata(self) -> None:
        """Reset plot metadata."""
        super().reset_metadata()
        self.Z_interp = {}
        self.contour_shapes = {}
        self.axis_divider = None
        self.caxs = []
        
    def resolve_target_styles(
        self,
        targets: List[Optional[str]],
        norm: Optional[Normalize] = None,
        cmap: str = 'GnBu',
        clabel_fmt: Union[str, Dict[str, Any]] = '%1.3f',
        clabel_manual: Optional[Dict[str, Any]] = None,
        contour_levels: Optional[List[float]] = None
    ) -> Dict[Optional[str], Dict[str, Any]]:
        """
        Resolve plotting styles for each target.

        Parameters
        ----------
        targets : List[Optional[str]]
            List of targets to resolve styles for
        norm : Optional[Normalize], default None
            Normalization to apply to all plots
        cmap : str, default 'GnBu'
            Colormap to use for plots
        clabel_fmt : Union[str, Dict[str, Any]], default '%1.3f'
            Format for contour labels
        clabel_manual : Optional[Dict[str, Any]], default None
            Manual contour label positions
        contour_levels : Optional[List[float]], default None
            Contour levels to use

        Returns
        -------
        Dict[Optional[str], Dict[str, Any]]
            Styles dictionary for each target
        """
        target_styles = {}
        for target in targets:
            styles = self.get_target_styles(target=target)
            
            # Set pcolormesh styles
            styles['pcolormesh'].setdefault('norm', norm)
            styles['pcolormesh'].setdefault('cmap', cmap)

            # Set contour styles
            styles['contour'].setdefault('norm', norm)
            styles['contour'].setdefault('levels', contour_levels)
            if 'colors' not in styles['contour']:
                styles['contour'].setdefault('cmap', cmap)

            # Set contour label styles
            styles['clabel'].setdefault('fmt', clabel_fmt)
            styles['clabel'].setdefault('manual', clabel_manual)

            # Set filled contour styles
            styles['contourf'].setdefault('norm', norm)
            styles['contourf'].setdefault('levels', contour_levels)
            if 'colors' not in styles['contourf']:
                styles['contourf'].setdefault('cmap', cmap)

            target_styles[target] = styles
        return target_styles

    def get_global_norm(
        self,
        zattrib: str,
        targets: List[str],
        transform: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> Normalize:
        """Calculate global normalization across all targets."""
        if not targets:
            raise ValueError('No targets specified')
                
        z = self.data_map[targets[0]][zattrib].values
        if transform is not None:
            z = transform(z)
        vmin = np.min(z)
        vmax = np.max(z)
        
        for target in targets[1:]:
            z = self.data_map[target][zattrib].values
            if transform is not None:
                z = transform(z)
            vmin = min(vmin, np.min(z))
            vmax = max(vmax, np.max(z))
                
        return Normalize(vmin=vmin, vmax=vmax)

    def get_interp_data(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        domain: Optional[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get interpolated data based on configuration.

        Parameters
        ----------
        x, y, z : numpy.ndarray
            Input data arrays
        domain : Optional[str], default None
            Domain name for caching

        Returns
        -------
        Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]
            X grid, Y grid, interpolated Z values
        """
        interp_method = self.config.get('interpolation')
        if interp_method:
            n = self.config['num_grid_points']
            return interpolate_2d(x, y, z, method=interp_method, n=n)
        return pivot_table(x, y, z, missing=np.nan)

    def select_colorbar_target(self, handles: Dict[str, Any]) -> Optional[Any]:
        """Select appropriate target for colorbar from available handles."""
        for key in ['pcm', 'contourf', 'contour']:
            if key in handles:
                return handles[key]
        return None

    def draw_colorbar(
        self,
        ax: Axes,
        mappable: Any,
        styles: Dict[str, Any]
    ) -> None:
        if self.axis_divider is None:
            self.axis_divider = make_axes_locatable(ax)
            
        pad = styles['axis_divider'].get('pad', 0.05)
        if isinstance(pad, str):
            pad = convert_size(pad)
            
        orig_pad = pad
        for cax_i in self.caxs[-1:]:
            # Adjust padding based on existing colorbars
            axis_width = cax_i.get_tightbbox().width
            cbar_width = cax_i.get_window_extent().width
            ticks_width = axis_width - cbar_width
            pad_width = self.caxs[0].get_tightbbox().xmin - ax.get_tightbbox().xmax
            width_ratio = ticks_width / pad_width
            pad += orig_pad * width_ratio

        axis_divider_styles = mp.concat((styles['axis_divider'], {'pad': pad}))
        cax = self.axis_divider.append_axes(**axis_divider_styles)
        
        cbar = plt.colorbar(mappable, cax=cax, **styles['colorbar'])
        if styles['colorbar_label'].get('label'):
            cbar.set_label(**styles['colorbar_label'])
            
        format_axis_ticks(cax, **styles['colorbar_axis'])
        self.caxs.append(cax)
        
        return cbar

    def draw_single_data(
        self,
        ax: Axes,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        zlabel: Optional[str] = None,
        draw_colormesh: bool = True,
        draw_contour: bool = False,
        draw_contourf: bool = False,
        draw_clabel: bool = True,
        draw_scatter: bool = False,
        draw_colorbar: bool = True,
        styles: Optional[Dict[str, Any]] = None,
        domain: Optional[str] = None,
    ) -> None:
        """Draw single dataset with selected plot types."""
        styles = mp.concat((self.styles, styles), copy=True)
        styles = defaultdict(dict, styles)
        
        # Get interpolated data if needed
        if draw_colormesh or draw_contour or draw_contourf:
            X, Y, Z = self.get_interp_data(x, y, z)
            self.Z_interp[domain] = Z
        
        handles: Dict[str, Any] = {}
        
        # Draw selected plot types
        if draw_colormesh:
            handles['pcm'] = ax.pcolormesh(X, Y, Z, **styles['pcolormesh'])

        contour_handle = None
        if draw_contour:
            contour = ax.contour(X, Y, Z, **styles['contour'])
            handles['contour'] = contour
            if draw_clabel:
                handles['clabel'] = ax.clabel(contour, **styles['clabel'])
            contour_handle = contour
                
        if draw_contourf:
            contourf = ax.contourf(X, Y, Z, **styles['contourf'])
            handles['contourf'] = contourf
            contour_handle = contourf

        if self.config['contour_shape'] and (contour_handle is not None):
            alpha = self.config['alphashape_alpha']
            self.contour_shapes[domain] = contour_to_shapes(contour_handle, alpha)
            
        if draw_scatter:
            handles['scatter'] = ax.scatter(x, y, **styles['scatter'])
        
        if draw_colorbar:
            mappable = self.select_colorbar_target(handles)
            if mappable:
                styles['colorbar_label'].setdefault('label', zlabel)
                handles['cbar'] = self.draw_colorbar(ax, mappable, styles)

        self.update_legend_handles(handles, domain=domain)

    def draw(
        self,
        xattrib: str,
        yattrib: str,
        zattrib: str,
        targets: Optional[List[str]] = None,
        colorbar_targets: Optional[List[str]] = None,
        legend_order: Optional[List[str]] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        zlabel: Optional[str] = None,
        title: Optional[str] = None,
        ymin: Optional[float] = None,
        ymax: Optional[float] = None,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        zmin: Optional[float] = None,
        zmax: Optional[float] = None,
        logx: bool = False,
        logy: bool = False,
        logz: bool = False,
        norm: Optional[Normalize] = None,
        cmap: str = 'GnBu',
        draw_colormesh: bool = True,
        draw_contour: bool = False,
        draw_contourf: bool = False,
        draw_scatter: bool = False,
        draw_clabel: bool = True,
        draw_colorbar: bool = True,
        draw_legend: bool = True,
        clabel_fmt: Union[str, Dict[str, Any]] = '%1.3f',
        clabel_manual: Optional[Dict[str, Any]] = None,
        contour_levels: Optional[List[float]] = None,
        transform: Optional[Callable[[np.ndarray], np.ndarray]] = None,
        ax: Optional[Axes] = None,
    ) -> Axes:
        """
        Draw complete 2D plot with all components.

        Parameters
        ----------
        xattrib : str
            Column name for x values
        yattrib : str
            Column name for y values
        zattrib : str
            Column name for z values
        targets : Optional[List[str]], default None
            List of targets to plot. If None, plots all available targets
        colorbar_targets : Optional[List[str]], default None
            Targets to draw colorbars for. If None, uses all targets
        legend_order : Optional[List[str]], default None
            Custom order for legend entries
        xlabel, ylabel, zlabel : Optional[str], default None
            Axis labels
        title : Optional[str], default None
            Plot title
        ymin, ymax : Optional[float], default None
            Y-axis limits
        xmin, xmax : Optional[float], default None
            X-axis limits
        zmin, zmax : Optional[float], default None
            Z-axis (colorbar) limits. Cannot be used with norm
        logx, logy : bool, default False
            Use logarithmic scale for axes
        logz : bool, default False
            Use logarithmic scale for colorbar
        norm : Optional[Normalize], default None
            Custom normalization for colorbar. Cannot be used with zmin/zmax
        cmap : str, default 'GnBu'
            Colormap name for plot
        draw_colormesh : bool, default True
            Draw pcolormesh plot
        draw_contour : bool, default False
            Draw contour lines
        draw_contourf : bool, default False
            Draw filled contours
        draw_scatter : bool, default False
            Draw scatter plot
        draw_clabel : bool, default True
            Add contour labels (if draw_contour is True)
        draw_colorbar : bool, default True
            Draw colorbar
        draw_legend : bool, default True
            Draw legend
        clabel_fmt : Union[str, Dict[str, Any]], default '%1.3f'
            Format for contour labels
        clabel_manual : Optional[Dict[str, Any]], default None
            Manual positions for contour labels
        contour_levels : Optional[List[float]], default None
            Specific levels for contours
        transform : Optional[Callable[[np.ndarray], np.ndarray]], default None
            Transform to apply to z values before plotting
        ax : Optional[Axes], default None
            Axes to plot on. If None, creates new axes

        Returns
        -------
        matplotlib.axes.Axes
            The plotted axes

        Raises
        ------
        RuntimeError
            If no targets to plot
        ValueError
            If incompatible options specified (e.g., both norm and zmin/zmax)

        Notes
        -----
        - If using draw_contour with draw_clabel, clabel_fmt and clabel_manual
          can be used to customize the labels
        - The transform function is applied to z values before any normalization
        """
        self.reset_metadata()
        
        if ax is None:
            ax = self.draw_frame(logx=logx, logy=logy)
            
        targets = self.resolve_targets(targets)
        if not targets:
            raise RuntimeError('No targets to draw')
            
        colorbar_targets = colorbar_targets or list(targets)
        
        if zmin is not None and zmax is not None:
            if norm is not None:
                raise ValueError('Cannot specify both (zmin, zmax) and norm')
            norm = (LogNorm if logz else Normalize)(
                vmin=zmin, vmax=zmax)
        elif norm is None:
            norm = self.get_global_norm(zattrib, targets, transform)
            
        target_styles = self.resolve_target_styles(
            targets=targets,
            norm=norm,              
            cmap=cmap,
            clabel_fmt=clabel_fmt,
            clabel_manual=clabel_manual,
            contour_levels=contour_levels
        )
            
        for target in targets:
            data = self.data_map[target]
            x = data[xattrib].values
            y = data[yattrib].values
            z = data[zattrib].values
            
            if transform is not None:
                z = transform(z)
                
            self.draw_single_data(
                ax, x, y, z,
                zlabel=zlabel,
                draw_colormesh=draw_colormesh,
                draw_contour=draw_contour,
                draw_contourf=draw_contourf,
                draw_scatter=draw_scatter,
                draw_clabel=draw_clabel,
                draw_colorbar=draw_colorbar and target in colorbar_targets,
                styles=self.styles_map.get(target),
                domain=target,
            )

        # Finalize plot
        self.draw_axis_components(
            ax,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title
        )
        
        self.set_axis_range(
            ax,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax
        )
        
        self.finalize()
        
        if legend_order is not None:
            self.legend_order = legend_order
        else:
            self.legend_order = self.get_labelled_legend_domains()
            
        if self.config['draw_legend']:
            self.draw_legend(ax)

        return ax