from __future__ import annotations

from typing import Dict, Optional, Union, List, Tuple, Any

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle

from quickstats.core import mappings as mp
from quickstats.maths.numerics import get_nan_shapes
from quickstats.utils.string_utils import remove_neg_zero
from .general_2D_plot import General2DPlot
from .likelihood_mixin import LikelihoodMixin
from .colors import ColorType, ColormapType

class Likelihood2DPlot(LikelihoodMixin, General2DPlot):
    """
    Class for plotting 2D likelihood scans with confidence levels.
    """
    
    DOF: int = 2
    
    COLOR_CYCLE: str = 'default'    
    
    STYLES: Dict[str, Any] = {
        'polygon': {
            'fill': True,
            'hatch': '/',
            'alpha': 0.5,
            'color': 'gray'            
        },
        'bestfit': {
            'marker': '*',
            'linewidth': 0,
            'markersize': 20,
            'color': '#E9F1DF',
            'markeredgecolor': 'black'
        },
        'contourf': {
            'extend': 'min'
        }
    }

    COLOR_MAP: Dict[str, str] = {
        '1_sigma': 'hh:darkblue',
        '2_sigma': '#F2385A',
        '3_sigma': '#FDC536',
        '0p68_CL': 'hh:darkblue',
        '0p95_CL': '#F2385A',
        '0p99_CL': '#FDC536',
        'contour.1_sigma': '#000000',
        'contour.2_sigma': '#F2385A',
        'contourf.1_sigma': '#4AD9D9',
        'contourf.2_sigma': '#FDC536',        
    }

    LABEL_MAP: Dict[str, str] = {
        'confidence_level': '{level:.0%} CL',
        'sigma_level': r'{level:.0g} $\sigma$',
        'bestfit': 'Best fit ({x:.2f}, {y:.2f})',
        'polygon': 'Nan NLL region',
    }

    CONFIG: Dict[str, Any] = {
        'interpolation': 'cubic',
        'num_grid_points': 500,
        'level_key': {
            'confidence_level': '{level_str}_CL',
            'sigma_level': '{level_str}_sigma',
        },
        'remove_nan_points_within_distance': None,
        'shade_nan_points': False,
        'alphashape_alpha': 0.1,
        'distinct_colors': False
    }

    def __init__(
        self,
        data_map: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        color_map: Optional[Dict[str, ColorType]] = None,
        color_cycle: Optional[ColormapType] = None,
        label_map: Optional[Dict[str, str]] = None,
        styles: Optional[Dict[str, Any]] = None,
        styles_map: Optional[Dict[str, Union[Dict[str, Any], str]]] = None,
        analysis_label_options: Optional[Union[Dict[str, Any], str]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.nan_shapes = {}
        self.contour_shapes = {}
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
        """Reset plot metadata including NaN shapes."""
        super().reset_metadata()
        self.nan_shapes = {}
        self.contour_shapes = {}
    
    def _get_color_for_level(
        self,
        target: str,
        artist: str,
        key: str,
        used_colors: List[str],
        default_colors: List[str],
        color_index: int
    ) -> Tuple[str, int]:
        """Get color for contour level."""
        for domain in [
            self.color_map.format(target, artist, key),
            self.color_map.format(target, key),
            self.color_map.format(artist, key),
            self.color_map.format(key)
        ]:
            if domain in self.color_map:
                color = self.color_map[domain]
                if (color not in used_colors) or (not self.config['distinct_colors']):
                    return color, color_index
                    
        if color_index >= len(default_colors):
            self.stdout.warning(
                'Number of colors required exceeds available colors. Recycling colors.'
            )
        color = default_colors[color_index % len(default_colors)]
        return color, color_index + 1

    def resolve_target_styles(self, **kwargs) -> Dict[str, Dict[str, Any]]:
        """Resolve styles for targets with level-specific colors."""
        level_specs = kwargs.pop('level_specs', {})
        if level_specs:
            contour_levels = [spec['chi2'] for spec in level_specs.values()]
        else:
            contour_levels = None
            
        target_styles = super().resolve_target_styles(contour_levels=contour_levels, **kwargs)
        default_colors = self.get_colors()
        color_index = 0
        
        for target, styles in target_styles.items():
            for artist in ['contour', 'contourf']:
                if artist not in styles or 'colors' in styles[artist]:
                    continue
                    
                colors = []
                for key in level_specs:
                    color, color_index = self._get_color_for_level(
                        target, artist, key, colors,
                        default_colors, color_index
                    )
                    colors.append(color)
                    
                styles[artist]['colors'] = colors
                styles[artist].pop('cmap')
                
        return target_styles
   
    def get_bestfit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray
    ) -> Tuple[float, float, float]:
        """Find the point of minimum likelihood."""
        mask = (~np.isnan(z)) & (z >= 0.)
        x, y, z = x[mask], y[mask], z[mask]
        X, Y, Z = self.get_interp_data(x, y, z)
        X, Y, Z = X.flatten(), Y.flatten(), Z.flatten()
        bestfit_idx = np.argmin(Z)
        return X[bestfit_idx], Y[bestfit_idx], Z[bestfit_idx]
   
    def _remove_points_near_shapes(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        Z: np.ndarray,
        shapes: List[Any],
        distance: float
    ) -> np.ndarray:
        """Remove points within distance of NaN shapes."""
        from shapely import Point
        
        XY = np.column_stack((X.ravel(), Y.ravel()))
        mask = np.full(XY.shape[0], False)
        
        for shape in shapes:
            x_ext, y_ext = shape.exterior.coords.xy
            min_x, max_x = np.min(x_ext) - distance, np.max(x_ext) + distance
            min_y, max_y = np.min(y_ext) - distance, np.max(y_ext) + distance
            # only focus on points within the largest box formed by the convex hull + distance
            box_mask = (((XY[:, 0] > min_x) & (XY[:, 0] < max_x)) & 
                       ((XY[:, 1] > min_y) & (XY[:, 1] < max_y)))
            points_in_box = XY[box_mask]
            # remove points inside the polygon
            inside_mask = np.array([shape.contains(Point(xy)) for xy in points_in_box])
            points_outside = points_in_box[~inside_mask]
            # remove points within distance d of the polygon
            near_mask = np.array([
                shape.exterior.distance(Point(xy)) < distance 
                for xy in points_outside
            ])
            
            box_indices = np.arange(mask.shape[0])[box_mask]
            mask[box_indices[inside_mask]] = True
            outside_indices = box_indices[~inside_mask]
            mask[outside_indices[near_mask]] = True
            
        Z_new = Z.copy()
        Z_new[mask.reshape(Z.shape)] = np.nan
        return Z_new
   
    def get_interp_data(
        self,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        domain: Optional[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get interpolated data handling NaN regions."""
        X, Y, Z = super().get_interp_data(x, y, z)
        
        distance = self.config.get('remove_nan_points_within_distance')
        shade_nan_points = self.config.get('shade_nan_points', False)
        if distance or shade_nan_points:
            alpha = self.config.get('alphashape_alpha', 2)
            nan_shapes = get_nan_shapes(x, y, z, alpha=alpha)
            self.nan_shapes[domain] = nan_shapes
        else:
            nan_shapes = None
            
        if distance and nan_shapes:
            Z = self._remove_points_near_shapes(X, Y, Z, nan_shapes, distance)
               
        return X, Y, Z
       
    def select_colorbar_target(self, handles: Dict[str, Any]) -> Optional[Any]:
        """Select target for colorbar from available handles."""
        return handles.get('pcm')
   
    def _get_contour_styles(
        self,
        domain: Optional[str],
        artist: str
    ) -> Dict[str, Any]:
        """Get styles for specified contour artist."""
        handle = self.get_handle(self.legend_data.format(domain, artist))
        if handle:
            return {
                'facecolors': handle.get_facecolor(),
                'edgecolors': handle.get_edgecolor(),
                'linestyles': getattr(handle, 'linestyles', '-'),
                'linewidths': handle.get_linewidth(),
                'hatches': getattr(handle, 'hatches', None)
            }
        return {}

    def create_custom_handles(
        self,
        level_specs: Optional[Dict[str, Dict[str, Any]]] = None,
        domain: Optional[str] = None
    ) -> None:
        """Create custom legend handles for contours."""
        if not level_specs:
            return
            
        handles = {}
        contour_styles = self._get_contour_styles(domain, 'contour')
        contourf_styles = self._get_contour_styles(domain, 'contourf')
        
        def get_style(style_dict: Dict[str, Any], key: str, idx: int) -> Any:
            value = style_dict.get(key)
            if isinstance(value, (list, tuple, np.ndarray)):
                return value[idx] if len(value) > idx else value[0]
            return value
   
        for i, (key, spec) in enumerate(level_specs.items()):
            hatch = get_style(contourf_styles, 'hatches', i)
            kwargs = {'hatch': hatch} if hatch else {}
            if contour_styles and contourf_styles:
                handle = Rectangle((0, 0), 1, 1,
                    label=spec['label'],
                    edgecolor=get_style(contour_styles, 'edgecolors', i),
                    facecolor=get_style(contourf_styles, 'facecolors', i),
                    linestyle=get_style(contour_styles, 'linestyles', i),
                    linewidth=get_style(contour_styles, 'linewidths', i),
                    **kwargs,
                )
            elif contour_styles:
                handle = Line2D([0], [0],
                    label=spec['label'],
                    color=get_style(contour_styles, 'edgecolors', i),
                    linestyle=get_style(contour_styles, 'linestyles', i)
                )
            elif contourf_styles:
                handle = Rectangle((0, 0), 1, 1,
                    label=spec['label'],
                    facecolor=get_style(contourf_styles, 'facecolors', i),
                    **kwargs,
                )
            else:
                continue
            handles[key] = handle
            
        self.update_legend_handles(handles, domain=domain)

    def draw_bestfit(
        self,
        ax: Axes,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray,
        styles: Optional[Dict[str, Any]] = None,
        domain: Optional[str] = None
    ) -> None:
        """Draw best fit point (minimum likelihood)."""
        styles = mp.concat((self.styles.get('bestfit'), styles), copy=True)
        styles.setdefault('color', self.get_target_color('bestfit', domain))
        bestfit_x, bestfit_y, bestfit_z = self.get_bestfit(x, y, z)
        
        bestfit_label_fmt = self.get_target_label('bestfit', domain)
        if bestfit_label_fmt:
            bestfit_label = bestfit_label_fmt.format(x=bestfit_x, y=bestfit_y)
            styles['label'] = remove_neg_zero(bestfit_label)
            
        handle, = ax.plot(bestfit_x, bestfit_y, **styles)
        self.update_legend_handles({'bestfit': handle}, domain=domain)
    
    def draw_nan_shapes(
        self,
        ax: Axes,
        shapes: List[Any],
        styles: Optional[Dict[str, Any]] = None,
        domain: Optional[str] = None
    ) -> None:
        """Draw shapes around NaN regions."""
        if not shapes:
            return
            
        styles = mp.concat((self.styles.get('polygon'), styles), copy=True)
        self.get_target_label('nan_shape', target)
        styles['label'] = label
            
        handle = None
        for shape in shapes:
            x, y = shape.exterior.coords.xy
            xy = np.column_stack((np.array(x).ravel(), np.array(y).ravel()))
            polygon = Polygon(xy, **styles)
            ax.add_patch(polygon)
            if handle is None:
                handle = polygon
                
        if handle is not None:
            self.update_legend_handles({'nan_shape': handle}, domain=domain)
    
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
        draw_clabel: bool = False,
        draw_scatter: bool = False,
        draw_colorbar: bool = True,
        draw_bestfit: bool = True,
        styles: Optional[Dict[str, Any]] = None,
        level_specs: Optional[Dict[str, Dict[str, Any]]] = None,
        domain: Optional[str] = None,
    ) -> None:
        """Draw single dataset with all components."""
        styles = styles or {}
        super().draw_single_data(
            ax=ax,
            x=x,
            y=y,
            z=z,
            zlabel=zlabel,
            draw_colormesh=draw_colormesh,
            draw_contour=draw_contour,
            draw_contourf=draw_contourf,
            draw_clabel=draw_clabel,
            draw_scatter=draw_scatter,
            draw_colorbar=draw_colorbar,
            styles=styles,
            domain=domain
        )
    
        self.create_custom_handles(level_specs=level_specs, domain=domain)
    
        if draw_bestfit:
            self.draw_bestfit(ax, x, y, z, styles=styles.get('bestfit'), domain=domain)
    
        if self.config['shade_nan_points']:
            self.draw_nan_shapes(
                ax,
                self.nan_shapes.get(domain),
                styles=styles.get('polygon'),
                domain=domain
            )
            
    def draw(
        self,
        xattrib: str,
        yattrib: str,
        zattrib: str = 'qmu',
        targets: Optional[List[str]] = None,
        colorbar_targets: Optional[List[str]] = None,
        legend_order: Optional[List[str]] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        zlabel: Optional[str] = r"$-2\Delta ln(L)$",
        title: Optional[str] = None,
        ymin: Optional[float] = None,
        ymax: Optional[float] = None,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        zmax: Optional[float] = None,
        logx: bool = False,
        logy: bool = False,
        norm: Optional[Any] = None,
        cmap: str = 'GnBu',
        draw_colormesh: bool = False,
        draw_contour: bool = True,
        draw_contourf: bool = False,
        draw_scatter: bool = False,
        draw_clabel: bool = False,
        draw_colorbar: bool = True,
        draw_bestfit: bool = True,
        sigma_levels: Optional[Tuple[float, ...]] = (1, 2),
        confidence_levels: Optional[Tuple[float, ...]] = None
    ) -> Axes:
        """
        Draw 2D likelihood plot.
       
        Parameters
        ----------
        xattrib : str
            Column name for x values
        yattrib : str
            Column name for y values
        zattrib : str, default 'qmu'
            Column name for likelihood values
        targets : Optional[List[str]], default None
            Target datasets to plot
        colorbar_targets : Optional[List[str]], default None
            Targets to draw colorbars for
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
        zmax : Optional[float], default None
            Maximum z value for normalization
        logx, logy : bool, default False
            Use logarithmic scale for axes
        norm : Optional[Any], default None
            Custom normalization for colormap
        cmap : str, default 'GnBu'
            Colormap name
        draw_colormesh : bool, default False
            Draw pcolormesh plot
        draw_contour : bool, default True
            Draw contour lines
        draw_contourf : bool, default False
            Draw filled contours
        draw_scatter : bool, default False
            Draw scatter plot
        draw_clabel : bool, default False
            Add contour labels
        draw_colorbar : bool, default True
            Draw colorbar
        draw_bestfit : bool, default True
            Draw best fit point
        sigma_levels : Optional[Tuple[float, ...]], default (1, 2)
            Sigma levels to show
        confidence_levels : Optional[Tuple[float, ...]], default None
            Confidence levels to show
            
        Returns
        -------
        matplotlib.axes.Axes
            The plotted axes
       
        Raises
        ------
        RuntimeError
            If no targets to draw
        ValueError
            If incompatible normalization options specified
        """
        self.reset_metadata()
        ax = self.draw_frame(logx=logx, logy=logy)
            
        targets = self.resolve_targets(targets)
        if not targets:
            raise RuntimeError('No targets to draw')
            
        colorbar_targets = colorbar_targets or list(targets)
        
        if zmax is not None:
            if norm is not None:
                raise ValueError('Cannot specify both zmax and norm')
            norm = Normalize(vmin=0, vmax=zmax)
            
        if norm is None:
            norm = self.get_global_norm(zattrib, targets)
     
        level_specs = self.get_level_specs(
            sigma_levels=sigma_levels,
            confidence_levels=confidence_levels
        )
        
        target_styles = self.resolve_target_styles(
            targets=targets,
            norm=norm,
            cmap=cmap,
            level_specs=level_specs
        )

        for target in targets:
            data = self.data_map[target]
            x = data[xattrib].values
            y = data[yattrib].values
            z = data[zattrib].values
            
            target_draw_colorbar = draw_colorbar and target in colorbar_targets
            
            self.draw_single_data(
                ax, x, y, z,
                zlabel=zlabel,
                draw_colormesh=draw_colormesh,
                draw_contour=draw_contour,
                draw_contourf=draw_contourf,
                draw_scatter=draw_scatter,
                draw_clabel=draw_clabel,
                draw_colorbar=target_draw_colorbar,
                draw_bestfit=draw_bestfit,
                styles=target_styles[target],
                level_specs=level_specs,
                domain=target
            )
       
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel, title=title)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        self.finalize()
            
        if self.config['draw_legend']:
            self.draw_legend(ax, targets=legend_order)
            
        return ax