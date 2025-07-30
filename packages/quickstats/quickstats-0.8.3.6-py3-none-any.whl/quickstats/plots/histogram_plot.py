from typing import Optional, Union, Dict, Tuple, List, Any, TypeVar, Sequence, Callable

import numpy as np
from numpy.typing import NDArray
from matplotlib.artist import Artist
from matplotlib.axes import Axes

from quickstats.core import mappings as mp
from quickstats.core.typing import is_indexable_sequence
from quickstats.utils.string_utils import get_field_names
from quickstats.maths.numerics import get_subsequences
from quickstats.maths.histograms import HistComparisonMode
from quickstats.concepts import Histogram1D, StackedHistogram
from .multi_data_plot import MultiDataPlot
from .template import get_artist_colors, is_transparent_color, remake_handles
from .core import PlotFormat, ErrorDisplayFormat
from .colors import ColorType, ColormapType

T = TypeVar('T')
NumericArray = NDArray[np.float64]
HistogramType = TypeVar('HistogramType', Histogram1D, StackedHistogram)
ErrorType = Optional[Union[Tuple[NumericArray, NumericArray], NumericArray]]

def validate_arrays(y1: NumericArray, y2: NumericArray) -> None:
    """
    Validate if two arrays are consistent by checking their values match.

    Parameters
    ----------
    y1 : NumericArray
        First array to compare
    y2 : NumericArray
        Second array to compare

    Raises
    ------
    ValueError
        If arrays have different shapes or values don't match
    """
    if y1.shape != y2.shape:
        raise ValueError(f"Arrays have different shapes: {y1.shape} vs {y2.shape}")
    
    if not np.allclose(y1, y2):
        raise ValueError(
            "Histogram bin values do not match the supplied weights. Please check your inputs."
        )

def apply_mask_to_error(
    error: ErrorType,
    mask: np.ndarray,
) -> ErrorType:
    """
    Apply boolean mask to error data.

    Parameters
    ----------
    error : ErrorType
        Error data as either tuple of arrays or single array
    mask : NumericArray
        Boolean mask to apply

    Returns
    -------
    ErrorType
        Masked error data or None if no error data provided
    """
    if error is None:
        return None
    
    try:
        if isinstance(error, tuple):
            return error[0][mask], error[1][mask]
        return error[mask]
    except IndexError as e:
        raise ValueError(f"Error array shape doesn't match mask shape: {e}") from e

def has_color_specification(styles: Dict[str, Any]) -> bool:
    """
    Check if style dictionary contains color-related options.

    Parameters
    ----------
    styles : Dict[str, Any]
        Dictionary of style options

    Returns
    -------
    bool
        True if any color option present
    """
    return bool(styles.keys() & {'color', 'facecolor', 'edgecolor', 'colors'})

class HistogramPlot(MultiDataPlot):
    """
    Enhanced histogram plotting class with support for various styles and error displays.
    """

    DATA_TYPE: T = Histogram1D  

    COLOR_CYCLE = "default"

    STYLES = {
        "hist": {
            "histtype": "step",
            "linestyle": "-",
            "linewidth": 2,
        },
        "errorbar": {
            "marker": "o",
            "markersize": 8,
            "linestyle": "none",
            "linewidth": 2,
            "elinewidth": 1,
            "capsize": 2,
            "capthick": 1,
        },
        "fill_between": {
            "alpha": 0.5,
            "color": "gray",
        },
        "bar": {
            "linewidth": 0,
            "alpha": 0.5,
            "color": "gray",
        },
    }

    CONFIG = {
        'plot_format': 'hist',
        'error_format': 'shade',
        'comparison_mode': 'ratio',        
        'show_xerr': False,
        "error_on_top": True,
        "inherit_color": True,
        "box_legend_handle": True,
        "combine_stacked_error": False,
        "isolate_error_legend": False,
        'comparison_object_id': 'comparison_{reference}_{target}',
        'default_ylabel': {
            'unnormalized': 'Events / {bin_width:.2g}{space}{unit}',
            'normalized': 'Fraction of Events / {bin_width:.2g}{space}{unit}',
        }
    }

    CONFIG_MAP = {
        'comparison': {
            'plot_format': 'errorbar',
            'error_format': 'errorbar'
        }
    }

    def __init__(
        self,
        data_map: Union[T, Dict[str, T]],
        color_map: Optional[Dict[str, ColorType]] = None,        
        color_cycle: Optional[ColormapType] = None,
        label_map: Optional[Dict[str, str]] = None,
        styles: Optional[Dict[str, Any]] = None,
        styles_map: Optional[Dict[str, Union[Dict[str, Any], str]]] = None,
        analysis_label_options: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None,
        config_map: Optional[Dict[str, Dict[str, Any]]] = None,
        figure_index: Optional[int] = None,
        verbosity: Union[int, str] = 'INFO'
    ):
        self.histograms = {}
        super().__init__(
            data_map=data_map,
            color_map=color_map,
            color_cycle=color_cycle,
            label_map=label_map,
            styles=styles,
            styles_map=styles_map,
            analysis_label_options=analysis_label_options,
            config=config,
            config_map=config_map,
            figure_index=figure_index,
            verbosity=verbosity,
        )

    def reset_metadata(self) -> None:
        super().reset_metadata()
        self.histograms = {}

    def set_plot_format(self, plot_format: str) -> None:
        """
        Set the plot format.

        Parameters
        ----------
        plot_format : str
            The plot format to use
        """
        self.config['plot_format'] = PlotFormat.parse(plot_format)

    def set_error_format(self, error_format: str) -> None:
        """
        Set the error format.

        Parameters
        ----------
        error_format : str
            The error format to use
        """
        self.config['error_format'] = ErrorDisplayFormat.parse(error_format)

    def get_comparison_inputs(
        self,
        comparison_options: Dict[str, Any],
    ) -> List[str]:
        inputs = []
        for options in comparison_options['components']:
            for key in ['reference', 'target']:
                if options[key] not in inputs:
                    inputs.append(options[key])
        return inputs

    def get_histogram_data(
        self,
        target: Optional[str],
        normalize: bool = True,
        divide_bin_width: bool = False,
        remove_errors: bool = False,
        mask_condition: Optional[Union[Sequence[float], Callable]] = None,
        **kwargs,
    ) -> Histogram1D:
        if target not in self.data_map:
            raise RuntimeError(f'No input found for the target: {target}')
        histogram = self.data_map[target].copy()
        if normalize:
            histogram.normalize(density=divide_bin_width, inplace=True)
        if remove_errors:
            histogram.remove_errors()
        if mask_condition is not None:
            histogram.mask(mask_condition)
        return histogram

    def get_comparison_data(
        self,
        reference: str,
        target: str,
        mode: Union[str, HistComparisonMode] = "ratio",
        **kwargs,
    ) -> Histogram1D:
        for key in [reference, target]:
            if key not in self.histograms:
                raise ValueError(f'Histogram data not set: {key}')
        reference_hist = self.histograms[reference]
        target_hist = self.histograms[target]
        if target_hist.binning != reference_hist.binning:
            raise ValueError(f'Reference and target histograms have different binnings')
        return target_hist.compare(reference_hist, mode=mode)

    def resolve_plot_options(
        self,
        targets: List[Optional[str]]
    ) -> Dict[str, Any]:
        targets = self.resolve_targets(targets)
        if not targets:
            raise RuntimeError('No targets to draw')
        self.reset_color_index()
        plot_options = {}
        for target in targets:
            plot_format = PlotFormat.parse(
                self.get_target_config('plot_format', target)
            )
            styles = self.get_target_styles(plot_format.artist, target, merge=False)
            styles.setdefault('label', self.label_map.get(target) or target)
            styles.setdefault('color', styles.get('color') or self.get_next_color())

            error_format = ErrorDisplayFormat.parse(
                self.get_target_config('error_format', target)
            )
            error_styles = self.get_target_styles(error_format.artist, target, merge=False)
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
                f'masked_{plot_format.artist}', target, merge=False
            ) or None
            if masked_styles:
                masked_target = self.label_map.format(target, 'masked')
                masked_styles.setdefault('label', self.label_map.get(masked_target))
            plot_options[target] = {
                'plot_format': plot_format,
                'error_format': error_format,
                'styles': styles,
                'error_styles': error_styles,
                'masked_styles': masked_styles
            }
        return plot_options

    def resolve_comparison_options(
        self,
        comparison_options: Optional[Dict[str, Any]] = None,
        plot_options: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve comparison options for the plot.

        Parameters
        ----------
        comparison_options : Dict[str, Any]], optional
            Comparison options dictionary
        plot_options : Dict[str, Dict[str, Any]], optional
            Plot options dictionary

        Returns
        -------
        Optional[Dict[str, Any]]
            Resolved comparison options, or None if not provided
        """
        if comparison_options is None:
            return None
        self.reset_color_index()
        plot_options = plot_options or {}
        comparison_options = mp.concat((comparison_options,), copy=True)
    
        comparison_mode = comparison_options.pop('mode', self.config['comparison_mode'])
        comparison_options['mode'] = comparison_mode
        plot_format = comparison_options.pop('plot_format', self.get_target_config('plot_format', 'comparison'))
        error_format = comparison_options.pop('error_format', self.get_target_config('error_format', 'comparison'))
        
        components = comparison_options['components']
        if not isinstance(components, list):
            components = [components]
            comparison_options['components'] = components

        def get_target_color(target: str, style_type: str) -> Optional[str]:
            if target in plot_options:
                styles = plot_options[target][style_type]
                return styles.get('color') or self.get_next_color()
            return self.get_next_color()

        inherit_color = self.config['inherit_color']
        for component in components:
            if 'target' not in component:
                raise ValueError(f'Missing specification of "target" in comparison component')
            if 'reference' not in component:
                raise ValueError(f'Missing specification of "reference" in comparison component')
            if component['target'] == component['reference']:
                raise ValueError(f'"target" can not be same as "reference" in comparison component')
            component.setdefault('mode', comparison_mode)
            component.setdefault('plot_format', plot_format)
            component.setdefault('error_format', error_format)
            component.setdefault('styles', {})
            component.setdefault('error_styles', {})
            component['mode'] = HistComparisonMode.parse(component['mode'])
            component['plot_format'] = PlotFormat.parse(component['plot_format'])
            if component['plot_format'] != PlotFormat.ERRORBAR:
                raise ValueError('`plot_format` must be ERRORBAR for comparison options')
            component['error_format'] = ErrorDisplayFormat.parse(component['error_format'])
            if inherit_color:
                # inherit color from target
                reference = component['target']
                for style_type in ['styles', 'error_styles']:
                    styles = component[style_type]
                    # need to avoid triggering get_target_error if color is already set
                    styles.setdefault('color', styles.get('color') or get_target_color(reference, style_type))
                    if is_indexable_sequence(styles['color']):
                        styles.pop('color')                        
        return comparison_options
    
    def draw_hist(
        self,
        ax: Axes,
        histogram: HistogramType,
        styles: Optional[Dict[str, Any]] = None,
    ) -> List[Artist]:
        """
        Draw histogram on given axis.

        Parameters
        ----------
        ax : Axes
            Matplotlib axes to draw on
        histogram : HistogramType
            Histogram data to plot
        styles : Optional[Dict[str, Any]], optional
            Additional style options, by default None

        Returns
        -------
        List[Artist]
            Handles for drawn histogram elements

        Raises
        ------
        TypeError
            If histogram type is unsupported
        ValueError
            If histogram data is invalid
        """
        styles = mp.concat((self.styles["hist"], styles), copy=True)

        try:
            if isinstance(histogram, StackedHistogram):
                x = [h.bin_centers for h in histogram.histograms.values()]
                y = [h.bin_content for h in histogram.histograms.values()]
                n, _, patches = ax.hist(
                    x,
                    weights=y,
                    bins=histogram.bin_edges,
                    stacked=True,
                    **styles,
                )
                handles = list(patches)
                
                y_base = 0.
                for n_i, y_i in zip(n, y):
                    validate_arrays(n_i - y_base, y_i)
                    y_base += y_i
            elif isinstance(histogram, Histogram1D):
                n, _, patches = ax.hist(
                    histogram.bin_centers,
                    weights=histogram.bin_content,
                    bins=histogram.bin_edges,
                    **styles,
                )
                handles = [patches]
                validate_arrays(n, histogram.bin_content)
            else:
                raise TypeError(f"Unsupported histogram type: {type(histogram)}")
                
            return handles
            
        except Exception as e:
            raise ValueError(f"Failed to draw histogram: {str(e)}") from e

    def draw_errorbar(
        self,
        ax: Axes,
        histogram: HistogramType,
        styles: Optional[Dict[str, Any]] = None,
        masked_styles: Optional[Dict[str, Any]] = None,
        with_error: bool = True,
    ) -> Union[Artist, Tuple[Artist, Artist]]:
        """
        Draw error bars for histogram data.

        Parameters
        ----------
        ax : Axes
            Matplotlib axes to draw on
        histogram : HistogramType
            Histogram data to plot
        styles : Optional[Dict[str, Any]], optional
            Additional style options, by default None
        with_error : bool, optional
            Whether to display error bars, by default True

        Returns
        -------
        Artist
            Handle for error bar plot

        Raises
        ------
        ValueError
            If error bar plotting fails
        """
        styles = mp.concat((self.styles["errorbar"], styles))
        x = histogram.bin_centers
        y = histogram.bin_content

        xerr = None
        yerr = None
        
        if with_error:
            xerr = histogram.bin_widths / 2 if self.config['show_xerr'] else None
            yerr = histogram.bin_errors

        with_marker = styles.get('marker', None) != 'none'
        if histogram.is_masked():
            if with_marker or (not masked_styles):
                mask = ~histogram.bin_mask
                x = x[mask]
                y = y[mask]
                xerr = apply_mask_to_error(xerr, mask)
                yerr = apply_mask_to_error(yerr, mask)
            else:
                indices = np.arange(len(x))
                unmasked_section_indices = get_subsequences(
                    indices, ~histogram.bin_mask, min_length=2
                )
                
                if not len(unmasked_section_indices):
                    raise RuntimeError('Histogram is fully masked, nothing to draw')

                unmasked_handles = []
                for indices in unmasked_section_indices:
                    mask = np.full(x.shape, False)
                    mask[indices] = True
                    x_i = x[mask]
                    y_i = y[mask]
                    xerr_i = apply_mask_to_error(xerr, mask)
                    yerr_i = apply_mask_to_error(yerr, mask)
                    handle_i = ax.errorbar(x_i, y_i, xerr=xerr_i, yerr=yerr_i, **styles)
                    unmasked_handles.append(handle_i)
                    
                indices = np.arange(len(x))
                masked_section_indices = get_subsequences(
                    indices, histogram.bin_mask, min_length=2
                )
                masked_handles = []
                masked_styles = mp.concat((styles, masked_styles), copy=True)
                for indices in masked_section_indices:
                    mask = np.full(x.shape, False)
                    mask[indices] = True
                    x_i = x[mask]
                    y_i = histogram._bin_content_raw[mask]
                    # Extend to edge
                    x_i[0] = histogram.bin_edges[indices[0]]
                    x_i[-1] = histogram.bin_edges[indices[-1] + 1]
                    xerr_i = apply_mask_to_error(xerr, mask)
                    yerr_i = apply_mask_to_error(yerr, mask)
                    handle_i = ax.errorbar(x_i, y_i, xerr=xerr_i, yerr=yerr_i, **masked_styles)
                    masked_handles.append(handle_i)
                if masked_handles:
                    return unmasked_handles[0], masked_handles[0]
                return unmasked_handles[0]

        try:
            return ax.errorbar(x, y, xerr=xerr, yerr=yerr, **styles)
        except Exception as e:
            raise ValueError(f"Failed to draw error bars: {str(e)}") from e

    def draw_filled_error(
        self,
        ax: Axes,
        histogram: HistogramType,
        styles: Optional[Dict[str, Any]] = None,
    ) -> Artist:
        """
        Draw filled error regions on plot.

        Parameters
        ----------
        ax : Axes
            Matplotlib axes to draw on
        histogram : HistogramType
            Histogram data to plot
        styles : Optional[Dict[str, Any]], optional
            Additional style options, by default None

        Returns
        -------
        Artist
            Handle for filled error region

        Raises
        ------
        RuntimeError
            If histogram is fully masked
        ValueError
            If filled error drawing fails
        """
        styles = mp.concat((self.styles['fill_between'], styles), copy=True)
        x = histogram.bin_centers
        rel_yerr = histogram.rel_bin_errors
        
        if rel_yerr is None:
            rel_yerr = (histogram.bin_content, histogram.bin_content)
            styles['color'] = 'none'
            styles.pop('facecolor', None)
            styles.pop('edgecolor', None)

        try:
            handle = None
            if histogram.is_masked():
                # handle cases where data is not continuous
                indices = np.arange(len(x))
                mask = ~histogram.bin_mask
                section_indices = get_subsequences(indices, mask, min_length=2)
                
                if not len(section_indices):
                    raise RuntimeError('Histogram is fully masked, nothing to draw')
                    
                for indices in section_indices:
                    mask = np.full(x.shape, False)
                    mask[indices] = True
                    x_i = x[mask]
                    rel_yerr_i = apply_mask_to_error(rel_yerr, mask)
                    
                    # Extend to edge
                    x_i[0] = histogram.bin_edges[indices[0]]
                    x_i[-1] = histogram.bin_edges[indices[-1] + 1]
                    
                    if (handle is not None) and (not has_color_specification(styles)):
                        styles['color'] = handle.get_facecolors()[0]
                    
                    handle_i = ax.fill_between(x_i, rel_yerr_i[0], rel_yerr_i[1], **styles)
                    if handle is None:
                        handle = handle_i
            else:
                handle = ax.fill_between(x, rel_yerr[0], rel_yerr[1], **styles)
                
            return handle
            
        except Exception as e:
            raise ValueError(f"Failed to draw filled error: {str(e)}") from e

    def draw_shaded_error(
        self,
        ax: Axes,
        histogram: HistogramType,
        styles: Optional[Dict[str, Any]] = None,
    ) -> Artist:
        """
        Draw shaded error bars as bar plot.

        Parameters
        ----------
        ax : Axes
            Matplotlib axes to draw on
        histogram : HistogramType
            Histogram data to plot
        styles : Optional[Dict[str, Any]], optional
            Additional style options, by default None

        Returns
        -------
        Artist
            Handle for drawn bars

        Raises
        ------
        ValueError
            If error bar shading fails
        """
        styles = mp.concat((self.styles["bar"], styles), copy=True)
        x = histogram.bin_centers
        y = histogram.bin_content
        yerr = histogram.bin_errors

        if yerr is None:
            yerr = (np.zeros_like(y), np.zeros_like(y))
            styles["color"] = "none"
            styles.pop("facecolor", None)
            styles.pop("edgecolor", None)

        height = yerr[0] + yerr[1]
        bottom = y - yerr[0]
        widths = histogram.bin_widths

        try:
            return ax.bar(x, height=height, bottom=bottom, width=widths, **styles)
        except Exception as e:
            raise ValueError(f"Failed to draw shaded error: {str(e)}") from e

    def draw_histogram_data(
        self,
        ax: Axes,
        histogram: HistogramType,
        plot_format: Union[PlotFormat, str] = 'hist',
        error_format: Union[ErrorDisplayFormat, str] = 'shade',
        styles: Optional[Dict[str, Any]] = None,
        error_styles: Optional[Dict[str, Any]] = None,
        masked_styles: Optional[Dict[str, Any]] = None,
        domain: str = 'main'
    ) -> None:
        """
        Draw histogram data with specified plot and error formats.

        Parameters
        ----------
        ax : Axes
            Matplotlib axes to draw on
        histogram : HistogramType
            Histogram data to plot
        plot_format : Union[PlotFormat, str], optional
            Format for plotting histogram, by default 'hist'
        error_format : Union[ErrorDisplayFormat, str], optional
            Format for plotting error, by default 'shade'
        styles : Optional[Dict[str, Any]], optional
            Style options for plot, by default None
        error_styles : Optional[Dict[str, Any]], optional
            Style options for error representation, by default None
        domain : str, optional
            Domain name for legend labels, by default 'main'

        Raises
        ------
        ValueError
            If plotting fails
        """
        styles = styles or {}
        error_styles = error_styles or {}
        if masked_styles is not None:
            masked_styles.setdefault('label', self.label_map.get(f'{domain}.masked'))
        plot_format = PlotFormat.parse(plot_format)
        error_format = ErrorDisplayFormat.parse(error_format)

        plot_handles: List[Artist] = []
        masked_handles: List[Artist] = []
        error_handles: List[Artist] = []

        if plot_format == PlotFormat.HIST:
            handles = self.draw_hist(ax, histogram, styles=styles)
            plot_handles.extend(handles)

        def custom_draw(
            histogram_current: HistogramType,
            styles_current: Dict[str, Any],
            error_styles_current: Dict[str, Any],
            masked_styles_current: Optional[Dict[str, Any]] = None,
        ) -> None:
            if plot_format == PlotFormat.ERRORBAR:
                with_error = error_format == ErrorDisplayFormat.ERRORBAR
                handle = self.draw_errorbar(
                    ax,
                    histogram_current,
                    styles=styles_current,
                    masked_styles=masked_styles_current,
                    with_error=with_error,
                )
                # NB: to fix check for masked handle
                if len(handle) == 2:
                    masked_handles.append(handle[1])
                    handle = handle[0]
                plot_handles.append(handle)

            # inherit colors from plot handle
            # priority: edgecolor > facecolor
            if not has_color_specification(error_styles_current):
                plot_handle = plot_handles[len(error_handles)]
                
                if plot_format == PlotFormat.HIST:
                    # take care of case histtype = 'step' or 'stepfilled'
                    plot_handle = plot_handle[0] if isinstance(plot_handle, list) else plot_handle
                    colors = get_artist_colors(plot_handle)
                    color = colors['edgecolor']
                    if is_transparent_color(color):
                        color = colors['facecolor']
                elif plot_format == PlotFormat.ERRORBAR:
                    plot_handle = plot_handle[0]
                    colors = get_artist_colors(plot_handle)
                    color = colors['markeredgecolor']
                    if is_transparent_color(color):
                        color = colors['markerfacecolor']
                else:
                    raise ValueError(f'Unsupported plot format: {plot_format}')

                zorder = plot_handle.get_zorder()
                if self.config['error_on_top']:
                    error_styles_current['zorder'] = zorder + 0.1
                if self.config['inherit_color']:
                    error_styles_current['color'] = color

            if error_styles_current.get('color', None) is None:
                error_styles_current.pop('color', None)

            if error_format == ErrorDisplayFormat.FILL:
                handle = self.draw_filled_error(ax, histogram_current, styles=error_styles_current)
                error_handles.append(handle)
            elif error_format == ErrorDisplayFormat.SHADE:
                handle = self.draw_shaded_error(ax, histogram_current, styles=error_styles_current)
                error_handles.append(handle)
            elif (error_format == ErrorDisplayFormat.ERRORBAR) and (plot_format != PlotFormat.ERRORBAR):
                error_styles_current = mp.concat((error_styles_current, {'marker': 'none'}), copy=True)
                handle = self.draw_errorbar(
                    ax,
                    histogram_current,
                    styles=error_styles_current,
                    with_error=True
                )
                error_handles.append(handle)

        combine_stacked_error = self.config['combine_stacked_error']
        # must draw error for individual histogram when plot with errorbar
        if plot_format == PlotFormat.ERRORBAR:
            combine_stacked_error = False

        if (not isinstance(histogram, StackedHistogram)) or \
           (isinstance(histogram, StackedHistogram) and combine_stacked_error):
            error_color = error_styles.get('color')
            # use artist default color when drawn
            if isinstance(error_color, list):
                error_color = None
            error_label = error_styles.get('label')
            if isinstance(error_label, list):
                error_label = self.label_map.get(f'{domain}.error', domain)
            error_styles = mp.concat(
                (error_styles, {'color': error_color, 'label': error_label}),
                copy=True
            )
            if masked_styles is not None:
                masked_label = self.label_map.get(f'{domain}.masked', domain)
                masked_styles = mp.concat(
                    (masked_styles, {'label': masked_label}),
                    copy=True
                )
            custom_draw(histogram, styles, error_styles, masked_styles)
        elif isinstance(histogram, StackedHistogram):
            def make_list(option: Any) -> List[Any]:
                if option is None:
                    return [None] * histogram.count
                if not isinstance(option, list):
                    return [option] * histogram.count
                if len(option) != histogram.count:
                    raise ValueError(
                        f"Option list length ({len(option)}) does not match histogram count ({histogram.count})"
                    )
                return option

            colors = make_list(styles.get('color', None))
            labels = make_list(styles.get('label', None))
            error_colors = make_list(error_styles.get('color', None))
            error_labels = make_list(error_styles.get('label', None))
            if masked_styles is not None:
                masked_labels = make_list(masked_styles.get('label', None))
            else:
                masked_labels = [None] * histogram.count

            for i, (_, histogram_i) in enumerate(histogram.offset_histograms()):
                styles_i = mp.concat(
                    (styles, {'color': colors[i], 'label': labels[i]}),
                    copy=True
                )
                error_styles_i = mp.concat(
                    (error_styles, {'color': error_colors[i], 'label': error_labels[i]}),
                    copy=True
                )
                if masked_styles is not None:
                    masked_styles_i = mp.concat(
                        (masked_styles, {'label': masked_labels[i]}),
                        copy=True
                    )
                else:
                    masked_styles_i = None
                custom_draw(histogram_i, styles_i, error_styles_i, masked_styles_i)

        handles = {}
        # there should be one-to-one correspondence between plot handle and error handle
        # except when plotting stacked histograms but showing merged errors
        if isinstance(histogram, StackedHistogram) and combine_stacked_error:
            if len(plot_handles) != histogram.count or (len(error_handles) != 1 and histogram.has_errors()):
                raise ValueError(
                    f"Mismatch in handle counts. Expected {histogram.count} plot handles "
                    f"and 1 error handle, got {len(plot_handles)} and {len(error_handles)}"
                )
            # reverse legend order for stacked histogram
            keys = list(histogram.histograms.keys())[::-1]
            plot_handles = plot_handles[::-1]
            for name, handle in zip(keys, plot_handles):
                handles[f'{domain}.{name}'] = handle
            if histogram.has_errors():
                handles[f'{domain}.error'] = error_handles[0]
        else:
            if plot_format == PlotFormat.ERRORBAR and error_format == ErrorDisplayFormat.ERRORBAR:
                error_handles = [None] * len(plot_handles)
            elif len(plot_handles) != len(error_handles):
                raise ValueError(
                    f"Mismatch in handle counts: {len(plot_handles)} plot handles "
                    f"vs {len(error_handles)} error handles"
                )

            if isinstance(histogram, StackedHistogram):
                # reverse legend order for stacked histogram
                keys = [f'{domain}.{name}' for name in histogram.histograms.keys()][::-1]
            else:
                keys = [domain]
            plot_handles = plot_handles[::-1]
            error_handles = error_handles[::-1]
            isolate_error_legend = self.config['isolate_error_legend']
            for key, plot_handle, error_handle in zip(keys, plot_handles, error_handles):
                # case histogram plot with histtype = 'step' or 'stepfilled'
                if isinstance(plot_handle, list):
                    plot_handle = plot_handle[0]

                if error_handle is None:
                    handles[key] = plot_handle
                else:
                    if isolate_error_legend:
                        handles[key] = plot_handle
                        handles[f'{key}.error'] = error_handle
                    else:
                        handles[key] = (
                            (plot_handle, error_handle)
                            if self.config['error_on_top']
                            else (error_handle, plot_handle)
                        )

        if len(masked_handles) > 0:
            handles[f'{domain}.masked'] = masked_handles[0]

        self.histograms[domain] = histogram
        self.update_legend_handles(handles)

    def draw_comparison_data(
        self,
        ax: Axes,
        reference : str,
        target: str,
        mode: Union[HistComparisonMode, str] = 'ratio',
        plot_format: Union[PlotFormat, str] = 'hist',
        error_format: Union[ErrorDisplayFormat, str] = 'shade',
        styles: Optional[Dict[str, Any]] = None,
        error_styles: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """
        Draw comparison data on the plot.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis on which to draw the comparison data.
        reference : str
            The reference histogram key.
        target : str
            The target histogram key.
        mode : Union[HistComparisonMode, str], optional
            Comparison mode, by default "ratio".
        plot_format : Union[PlotFormat, str], optional
            Format for plotting the comparison data, by default 'errorbar'.
        error_format : Union[ErrorDisplayFormat, str], optional
            Format for plotting the error, by default 'errorbar'.
        styles : Dict, optional
            Styling options for the plot, by default None.
        error_styles : Dict, optional
            Styling options for the error representation, by default None.

        Raises
        ------
        ValueError
            If the histogram data for the reference or target is not set.
        """

        histogram = self.get_comparison_data(
            reference=reference,
            target=target,
            mode=mode
        )

        domain = self.config['comparison_object_id'].format(reference=reference,
                                                            target=target)
        self.histograms[domain] = histogram

        self.draw_histogram_data(
            ax=ax,
            histogram=histogram,
            plot_format=plot_format,
            error_format=error_format,
            styles=styles,
            error_styles=error_styles,
            domain=domain,
        )
        
        if histogram.has_errors():
            ylim = (
                np.nanmin(histogram.rel_bin_errlo),
                np.nanmax(histogram.rel_bin_errhi)
            )
        else:
            y = histogram.bin_content
            ylim = (np.nanmin(y), np.nanmax(y))
        if not (np.isnan(ylim[0]) or np.isnan(ylim[1])):
            self.stretch_axis(ax, ylim=ylim)

    def resolve_xlabel(
        self,
        xlabel: Optional[str] = None,
        unit: Optional[str] = None
    ):
        if (xlabel is None) or (unit is None):
            return xlabel
        return f'{xlabel} [{unit}]'

    def resolve_ylabel(
        self,
        ylabel: Optional[str] = None,
        unit: Optional[str] = None,
        normalize: bool = False,
        divide_bin_width: bool = False,
        reference: Optional[str] = None,
    ) -> str:
        """Resolves the y-axis label based on provided parameters and histogram configuration.
        
        Args:
            ylabel: Custom y-axis label that takes precedence if provided
            unit: Unit of measurement (optional)
            normalize: Whether the histogram is normalized
            divide_bin_width: Whether the histogram is divided by bin width
            reference: Name of reference histogram to consider the binning
            
        Returns:
            Formatted y-axis label string
            
        Raises:
            ValueError: If histograms aren't initialized when needed
            PlottingError: If reference histograms can't be accessed
            RuntimeError: If histograms have different binnings
        """
        ylabel = ylabel or self.config['default_ylabel'].get(
            'normalized' if normalize else 'unnormalized', ''
        )
        field_names = get_field_names(ylabel)
        if (not field_names) or (('unit' not in field_names) and ('bin_width' not in field_names)):
            return ylabel
        unit = unit or ''
        if 'bin_width' not in field_names:
            return ylabel.format(unit=unit)
        space = ' ' if unit else ''
        if divide_bin_width:
            return ylabel.format(unit=unit, bin_width='' if unit else '1', space=space)
    
        if not self.histograms:
            raise ValueError('Failed to deduce bin width for ylabel: histograms not initialized')
    
        try:
            histograms = (
                [self.histograms[reference]]
                if reference
                else list(self.histograms.values())
            )
        except Exception as e:
            raise PlottingError(f"Failed to get reference histogram: {str(e)}") from e
    
        if not all(h.uniform_binning for h in histograms):
            return ylabel.format(unit=unit, bin_width='bin', space=space)
    
        first_hist = histograms[0]
        if all(first_hist.binning == h.binning for h in histograms[1:]):
            return ylabel.format(unit=unit, bin_width=first_hist.bin_widths[0], space=space)

        self.stdout.warning(
            'Attempting to deduce bin width for ylabel but the '
            'plotted histograms have different binnings. Please '
            'use the "primary_target" option to set the target '
            'histogram used for binning inference.'
        )
        return None
        
    def draw(
        self,
        targets: Optional[List[str]] = None,
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
        
        self.reset_metadata()

        plot_options = self.resolve_plot_options(targets)
        comparison_options = self.resolve_comparison_options(comparison_options, plot_options)
        
        if comparison_options is not None:
            ax, ax_ratio = self.draw_frame(frametype='ratio', logx=logx, logy=logy)
        else:
            ax = self.draw_frame(frametype='single', logx=logx, logy=logy)
            ax_ratio = None

        hist_options = {
            'normalize': normalize,
            'divide_bin_width': divide_bin_width,
            'remove_errors': not show_error,
            'mask_condition': mask_condition
        }
        for target, options in plot_options.items():
            histogram = self.get_histogram_data(
                target=target,
                **hist_options
            )
            self.draw_histogram_data(
                ax, 
                histogram=histogram,
                domain=target,
                **options
            )

        xlabel = self.resolve_xlabel(
            xlabel=xlabel,
            unit=unit
        )
        ylabel = self.resolve_ylabel(
            ylabel=ylabel,
            unit=unit,
            normalize=normalize,
            divide_bin_width=divide_bin_width,
            reference=primary_target
        )
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)        
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, ypad=ypad)
        self.finalize()
            
        if self.config['draw_legend']:
            if legend_order is None:
                legend_order = self.get_labelled_legend_domains()
            self.draw_legend(ax, targets=legend_order)

        if comparison_options is not None:
            inputs = self.get_comparison_inputs(comparison_options)
            for target in inputs:
                if target not in self.histograms:
                    self.histograms[target] = self.get_histogram_data(
                        target=target,
                        **hist_options
                    )
            components = comparison_options.pop('components')
            for options in components:
                self.draw_comparison_data(
                    ax_ratio,
                    **options
                )
        
            self.decorate_comparison_axis(ax, ax_ratio, **comparison_options)
            return ax, ax_ratio

        return ax