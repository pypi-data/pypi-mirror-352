from typing import Optional, Union, Dict, List, Sequence, Tuple, Any, Callable, TypeVar
from collections import defaultdict
from copy import deepcopy

import pandas as pd
import numpy as np

from matplotlib.axes import Axes

from quickstats.core import mappings as mp
from quickstats.core.typing import is_indexable_sequence
from quickstats.utils.common_utils import remove_duplicates
from quickstats.maths.histograms import HistComparisonMode
from quickstats.concepts import Histogram1D, StackedHistogram
from .core import PlotFormat, ErrorDisplayFormat
from .colors import ColorType, ColormapType
from .template import get_artist_colors
from .histogram_plot import HistogramPlot

T = TypeVar('T')

def _merge_styles(
    styles_map: Dict[str, Dict[str, Any]],
    primary_key: Optional[str] = None,
    use_sequence_options: bool = True
) -> Dict[str, Any]:
    """
    Merge style dictionaries from multiple targets into a single style dictionary.

    Parameters
    ----------
    styles_map : Dict[str, Dict[str, Any]]
        A mapping from target names to their style dictionaries
    primary_key : Optional[str], optional
        The key of the primary target whose styles should be prioritized
    use_sequence_options : bool, optional
        Whether to collect sequence options (like 'color', 'label') into lists

    Returns
    -------
    Dict[str, Any]
        A merged style dictionary

    Raises
    ------
    ValueError
        If inconsistent style values or missing required options are found
    """
    sequence_options = ["color", "label"]
    
    if primary_key is not None:
        merged_styles = deepcopy(styles_map[primary_key])
    else:
        merged_styles = {}
        for target, styles in styles_map.items():
            styles = deepcopy(styles)
            for key, value in styles.items():
                if key in sequence_options:
                    continue
                if key in merged_styles and merged_styles[key] != value:
                    targets = list(styles_map)
                    raise ValueError(
                        f"Inconsistent values for option '{key}' among targets: "
                        f"{', '.join(targets)}"
                    )
                merged_styles[key] = value

    if use_sequence_options:
        for option in sequence_options:
            merged_styles[option] = [styles.get(option) for styles in styles_map.values()]
            if None in merged_styles[option]:
                missing_targets = [
                    target for target, styles in styles_map.items() 
                    if styles.get(option) is None
                ]
                raise ValueError(
                    f"Missing '{option}' for targets: {', '.join(missing_targets)}"
                )
    
    return merged_styles

class VariableDistributionPlot(HistogramPlot):
    """
    Class for plotting variable distributions with advanced features.
    """

    DATA_TYPE: T = pd.DataFrame

    COLOR_CYCLE = "default"

    STYLES = {
        "hist": {
            'histtype': 'step',
            'linestyle': '-',
            'linewidth': 2
        },
        'errorbar': {
            'marker': 'o',
            'markersize': 10,
            'linestyle': 'none',
            'linewidth': 0,
            'elinewidth': 2,
            'capsize': 0,
            'capthick': 0
        },
        'fill_between': {
            'alpha': 0.5,
            'color': 'gray'
        },
        "bar": {
            'linewidth': 0,
            'alpha': 0.5,
            'color': 'gray'
        },
        'ratio_line': {
            'color': 'gray',
            'linestyle': '--',
            'zorder': 0
        }
    }

    CONFIG = {
        'plot_format': 'hist',
        'error_format': 'shade',
        'comparison_mode': 'ratio',
        'error_on_top': True,
        'inherit_color': True,
        'combine_stacked_error': False,
        'box_legend_handle': False,
        'isolate_error_legend': False,
        'stacked_object_id': 'stacked_{index}',
    }

    CONFIG_MAP = {
        'comparison': {
            'plot_format': 'errorbar',
            'error_format': 'errorbar'
        }
    }

    def __init__(
        self,
        data_map: Union[pd.DataFrame, Dict[str, pd.DataFrame]],        
        plot_options: Optional[Dict[str, Dict[str, Any]]] = None,
        color_map: Optional[Dict[str, ColorType]] = None,  
        color_cycle: Optional[ColormapType] = None,
        label_map: Optional[Dict[str, str]] = None,
        styles: Optional[Union[Dict[str, Any], str]] = None,
        styles_map: Optional[Dict[str, Union[Dict[str, Any], str]]] = None,
        analysis_label_options: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        verbosity: Union[int, str] = 'INFO'
    ) -> None:
        """
        Initialize the VariableDistributionPlot.

        Parameters
        ----------
        data_map : Union[pd.DataFrame, Dict[str, pd.DataFrame]]
            Input dataframe(s). If dictionary, maps sample names to dataframes
        plot_options : Optional[Dict[str, Dict[str, Any]]], optional
            A dictionary containing the plot options for various group of samples.
            It should be of the form
            { <sample_group>:
              {
                "samples": <list of sample names>,
                "weight_scale": <scale factor>,
                "styles" : <matplotlib artist options>,
                "error_styles": <matplotlib artist options>,
                "plot_format": "hist" or "errorbar",
                "error_format": "errorbar", "fill" or "shade"
                "show_error": True or False,
                "primary": True or False,
                "stack_index": <stack index>,
                "mask_condition": <callable or tuple of 2 floats>
              }
            }
            
            "styles" should match the options available in mpl.hist if
            `plot_format` = "hist" or mpl.errorbar if `plot_format` = "errorbar"
            
            "error_styles" should match the options available in mpl.errorbar if
            `error_format` = "errorbar", mpl.bar if `error_format` = "shade" or
            mpl.fill_between if `error_format` = "fill"
            
            (optional) "weight_scale" is used to scale the weights of the given
            group of samples by the given factor

            (optional) "plot_format" is used to indicate which matplotlib artist
            is used to draw the variable distribution; by default the internal
            value from config['plot_format'] is used; allowed formats are
            "hist" or "errorbar"

            (optional) "error_format" is used to indicate which matplotlib artist
            is used to draw the error information; by default the internal
            value from config['error_format'] is used; allowed formats are
            "errorbar", "fill" or "shade"
            
            (optional) "show_error" is used to specify whether to show the errorbar/
            errorbands for this particular target
            
            (optional) "stack_index" is used when multiple stacked plots are made;
            sample groups with the same stack index will be stacked; this option
            is only used when `plot_format` = "hist" and the draw method is called
            with the `stack` option set to True; by default a stack index of 0 will
            be assigned

            (optional) "mask_condition" defines the condition to mask portion(s)
            of the data in the plot; in case of a 2-tuple, it specifies the 
            (start, end) bin range of data that should be hidden; in case of a
            callable, it is a function that takes as input the bin_centers (x)
            and bin_content (y) of the histogram, and outputs a boolean
            array indicating the locations of the histogram that should be hidden

            Note: If "samples" is not given, it will default to [<sample_group>]
            
            Note: If both `plot_format` and `error_format` are errorbar, "styles"
            will be used instead of "error_styles" for the error styles
        label_map : Optional[Dict[str, str]], optional
            Mapping from target names to display labels
        color_cycle : Optional[ColormapType], optional
            Color cycle for plotting
        styles : Optional[Union[Dict[str, Any], str]], optional
            Global styles for plot artists
        analysis_label_options : Optional[Dict[str, Any]], optional
            Options for analysis labels
        config : Optional[Dict[str, Any]], optional
            Configuration parameters
        verbosity : Union[int, str], optional
            Logging verbosity level, by default 'INFO'
        """
        self.plot_options = plot_options
        super().__init__(
            data_map=data_map,
            color_map=color_map,
            color_cycle=color_cycle,
            styles=styles,
            styles_map=styles_map,
            label_map=label_map,
            analysis_label_options=analysis_label_options,
            config=config,
            verbosity=verbosity
        )

    def resolve_targets(
        self,
        targets: Optional[List[str]] = None,
        plot_options: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> List[Optional[str]]:
        """
        Resolve the targets to be plotted.

        Parameters
        ----------
        targets : Optional[List[str]], optional
            List of target names
        plot_options : Optional[Dict[str, Dict[str, Any]]], optional
            Plot options dictionary

        Returns
        -------
        List[Optional[str]]
            List of resolved target names

        Raises
        ------
        ValueError
            If targets are specified when only a single data set is present
        """
        if self.is_single_data():
            if targets is not None:
                raise ValueError(
                    'No targets should be specified if only one set of input data is given'
                )
            return [None]
            
        if targets is None:
            all_samples = list(self.data_map.keys())
            if plot_options is None:
                return all_samples
            
            targets = []
            grouped_samples = set()
            for key, options in plot_options.items():
                targets.append(key)
                samples = options.get("samples", [key])
                grouped_samples |= set(samples)
            
            targets.extend([sample for sample in all_samples if sample not in grouped_samples])
        
        return targets

    def resolve_plot_options(
        self,
        plot_options: Optional[Dict[str, Dict[str, Any]]] = None,
        targets: Optional[List[str]] = None,
        stacked: bool = False,
        show_error: bool = True,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Resolve plot options for the given targets.

        Parameters
        ----------
        plot_options : Optional[Dict[str, Dict[str, Any]]], optional
            Plot options dictionary
        targets : Optional[List[str]], optional
            List of target names
        stacked : bool, optional
            Whether to stack the plots

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Resolved plot options

        Raises
        ------
        RuntimeError
            If no targets to draw
        ValueError
            If no samples specified for a target or duplicate samples found
        """
        targets = self.resolve_targets(targets, plot_options)
        if not targets:
            raise RuntimeError('No targets to draw')
            
        plot_options = plot_options or {}
        resolved_plot_options = {}
        for target in targets:
            options = deepcopy(plot_options.get(target, {}))
            options.setdefault('samples', [target])
            options.setdefault('primary', False)
            options.setdefault('weight_scale', None)
            options.setdefault('stack_index', 0)
            options.setdefault('mask_condition', None)
            options.setdefault('show_error', show_error)
            
            if not options['samples']:
                raise ValueError(f'No samples specified for target "{target}"')
            if len(set(options['samples'])) != len(options['samples']):
                raise ValueError(f'Found duplicated samples for target "{target}": {options["samples"]}')
                
            plot_format = PlotFormat.parse(
                options.get('plot_format', self.config['plot_format'])
            )
            styles = options.get('styles', {})
            styles['color'] = styles.get('color') or self.color_map.get(target) or self.get_next_color()
            styles.setdefault('label', self.label_map.get(target) or target)
                
            error_format = ErrorDisplayFormat.parse(
                options.get(
                    'error_format',
                    'errorbar' if plot_format == 'errorbar' else self.config['error_format']
                )
            )
            
            error_styles = options.get('error_styles', {})
            # Reuse color of the plot for the error if not specified
            error_styles['color'] = error_styles.get('color') or styles['color']
            error_target = self.label_map.format(target, 'error')
            error_styles.setdefault('label', self.label_map.get(error_target) or error_target)
                
            options.update({
                'plot_format': plot_format,
                'error_format': error_format,
                'styles': styles,
                'error_styles': error_styles
            })
            resolved_plot_options[target] = options

        final_plot_options = {}
        if not stacked:
            for target in targets:
                options = {'components': {}}
                for key in ['plot_format', 'error_format', 'styles', 'error_styles', 'show_error']:
                    options[key] = resolved_plot_options[target].pop(key)
                options['components'][target] = resolved_plot_options.pop(target)
                final_plot_options[target] = options
            return final_plot_options

        target_map = defaultdict(list)
        for target in targets:
            stack_index = resolved_plot_options[target]['stack_index']
            target_map[stack_index].append(target)

        for index, targets_group in target_map.items():
            options = {}
            components = {target: resolved_plot_options.pop(target) for target in targets_group}
            options['components'] = components
            
            if len(targets_group) == 1:
                primary_target = targets_group[0]
            else:
                primary_target = next(
                    (t for t in targets_group if components[t]['primary']), 
                    None
                )

            if len([t for t in targets_group if components[t]['primary']]) > 1:
                raise RuntimeError(
                    f'Multiple primary targets found with stack index: {index}'
                )

            for format_type in ['plot', 'error']:
                key = f'{format_type}_format'
                format_map = {t: components[t].pop(key) for t in targets_group}
                if primary_target is None:
                    if len(set(format_map.values())) > 1:
                        raise RuntimeError(
                            f'Inconsistent {format_type} format for targets with stack index: {index}'
                        )
                    options[key] = next(iter(format_map.values()))
                else:
                    options[key] = format_map[primary_target]
                    
            # Only one target, no need to stack
            if len(components) == 1:
                target = targets_group[0]
            else:
                target = self.config["stacked_object_id"].format(index=index)

            styles_map = {t: components[t].pop('styles') for t in targets_group}
            combine_stacked_error = self.config['combine_stacked_error']
            use_sequence_options = len(components) > 1
            styles = _merge_styles(
                styles_map, primary_target,
                use_sequence_options=use_sequence_options
            )
            styles = mp.concat((styles, self.get_target_styles(options['plot_format'].artist, target, merge=False)))
            error_styles_map = {t: components[t].pop('error_styles') for t in targets_group}
            use_sequence_options &= not combine_stacked_error
            error_styles = _merge_styles(
                error_styles_map, primary_target,
                use_sequence_options=use_sequence_options
            )
            error_styles = mp.concat((error_styles, self.get_target_styles(options['error_format'].artist, target, merge=False)))
            if combine_stacked_error:
                error_styles['label'] = self.label_map.get(f'{target}.error', f'{target}.error')
            options.update({
                'styles': styles,
                'error_styles': error_styles
            })
            final_plot_options[target] = options
        return final_plot_options
        
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
            
        plot_options = plot_options or {}
        comparison_options = deepcopy(comparison_options)
        comparison_options.setdefault('mode', self.config['comparison_mode'])
        
        if not callable(comparison_options['mode']):
            comparison_options['mode'] = HistComparisonMode.parse(comparison_options['mode'])
            
        default_plot_format = comparison_options.get('plot_format', self.get_target_config('plot_format', 'comparison'))
        default_error_format = comparison_options.get('error_format', self.get_target_config('error_format', 'comparison'))
        
        components = comparison_options['components']
        if not isinstance(components, list):
            components = [components]
            comparison_options['components'] = components

        def get_target_color(target: str, style_type: str) -> Optional[str]:
            if target in plot_options:
                return plot_options[target][style_type].get('color')
            for _, options in plot_options.items():
                names = list(options['components'].keys())
                if target not in names:
                    continue
                color = options[style_type].get('color')
                if isinstance(color, list):
                    return color[names.index(target)]
                return color
            return None

        inherit_color = self.config['inherit_color']
        for component in components:
            component['mode'] = comparison_options['mode']
            plot_format = PlotFormat.parse(component.get('plot_format', default_plot_format))
            error_format = ErrorDisplayFormat.parse(component.get('error_format', default_error_format))
            
            component.update({
                'plot_format': plot_format,
                'error_format': error_format
            })
            if component['plot_format'] != PlotFormat.ERRORBAR:
                raise ValueError('`plot_format` must be ERRORBAR for comparison options')
            component.setdefault('styles', {})
            component.setdefault('error_styles', {})
            
            if inherit_color:
                for key in ['styles', 'error_styles']:
                    component[key].setdefault(
                        'color', 
                        get_target_color(component['target'], key)
                    )
                    if is_indexable_sequence(component[key]['color']):
                        component[key].pop('color')
                
        return comparison_options

    def get_relevant_samples(
        self,
        plot_options: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Get all relevant samples from the plot options.

        Parameters
        ----------
        plot_options : Dict[str, Dict[str, Any]]
            Plot options dictionary

        Returns
        -------
        List[str]
            List of relevant sample names
        """
        relevant_samples = []
        for options in plot_options.values():
            for component in options['components'].values():
                relevant_samples.extend(component['samples'])
        return remove_duplicates(relevant_samples)

    def resolve_legend_order(
        self,
        plot_options: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Resolve the order of legend entries.

        Parameters
        ----------
        plot_options : Dict[str, Dict[str, Any]]
            Plot options dictionary

        Returns
        -------
        List[str]
            List of legend keys in the desired order
        """
        legend_order = []
        combine_stacked_error = self.config['combine_stacked_error']
        isolate_error_legend = self.config['isolate_error_legend']
        
        for target, options in plot_options.items():
            if len(options['components']) == 1:
                legend_order.append(target)
                if isolate_error_legend:
                    legend_order.append(f'{target}.error')
            else:
                for subtarget in options['components'].keys():
                    legend_order.append(f'{target}.{subtarget}')
                    if isolate_error_legend:
                        legend_order.append(f'{target}.{subtarget}.error')
                if combine_stacked_error:
                    legend_order.append(f'{target}.error')
                    
        return legend_order

    def get_sample_data(
        self,
        samples: List[str],
        column_name: str,
        variable_scale: Optional[float] = None,
        weight_scale: Optional[float] = None,
        weight_name: Optional[str] = None,
        selection: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get sample data and weights for the given samples.

        Parameters
        ----------
        samples : List[str]
            List of sample names
        column_name : str
            Name of the variable column
        variable_scale : Optional[float], optional
            Factor to scale the variable values
        weight_scale : Optional[float], optional
            Factor to scale the weights
        weight_name : Optional[str], optional
            Name of the weight column
        selection : Optional[str], optional
            Selection query to filter the data

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Tuple containing the variable data and corresponding weights
        """
        df = pd.concat([self.data_map[sample] for sample in samples], ignore_index=True)
        
        if selection is not None:
            df = df.query(selection)
        
        x = df[column_name].values
        if variable_scale is not None:
            x = x * variable_scale
            
        weights = df[weight_name].values if weight_name is not None else np.ones_like(x)
        if weight_scale is not None:
            weights = weights * weight_scale
            
        return x, weights

    def deduce_bin_range(
        self,
        samples: List[str],
        column_name: str,
        variable_scale: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Deduce bin range based on variable ranges from multiple samples.

        Parameters
        ----------
        samples : List[str]
            List of sample names
        column_name : str
            Name of the variable column
        variable_scale : Optional[float], optional
            Factor to scale the variable values

        Returns
        -------
        Tuple[float, float]
            The minimum and maximum values across all samples
        """
        xmin, xmax = np.inf, -np.inf
        
        for sample in samples:
            df = self.data_map[sample]
            x = df[column_name].values
            if variable_scale is not None:
                x = x * variable_scale
            xmin = min(xmin, np.nanmin(x))
            xmax = max(xmax, np.nanmax(x))
            
        return xmin, xmax        

    def draw_single_target(
        self,
        ax: Axes,
        target: str,
        components: Dict[str, Dict[str, Any]],
        column_name: str,
        hist_options: Dict[str, Any],
        plot_format: Union[str, PlotFormat] = 'hist',
        error_format: Union[str, ErrorDisplayFormat] = 'shade',
        show_error: bool = True,
        styles: Optional[Dict[str, Any]] = None,
        masked_styles: Optional[Dict[str, Any]] = None,
        error_styles: Optional[Dict[str, Any]] = None,
        variable_scale: Optional[float] = None,
        weight_name: Optional[str] = None,
        selection: Optional[str] = None,
    ) -> None:
        """
        Draw a single target on the plot.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis on which to draw the plot.
        target : str
            The target name.
        components : Dict
            Components of the target.
        column_name : str
            Name of the variable column.
        hist_options : Dict
            Histogram options.
        plot_format : Union[PlotFormat, str], optional
            Format for plotting the histogram, by default 'hist'.
        error_format : Union[ErrorDisplayFormat, str], optional
            Format for plotting the error, by default 'shade'.
        styles : Dict, optional
            Styling options for the plot, by default None.
        error_styles : Dict, optional
            Styling options for the error representation, by default None.
        variable_scale : float, optional
            Factor to scale the variable values, by default None.
        weight_name : str, optional
            Name of the weight column, by default None.
        selection : str, optional
            Selection query to filter the data, by default None.
        """
        def get_histogram(options: Dict[str, Any]) -> Histogram1D:
            samples = options['samples']
            weight_scale = options.get('weight_scale')
            mask_condition = options.get('mask_condition')
            evaluate_error = options.get('show_error', True)
            x, weights = self.get_sample_data(
                samples,
                column_name,
                selection=selection,
                variable_scale=variable_scale,
                weight_scale=weight_scale,
                weight_name=weight_name
            )
            histogram = Histogram1D.create(
                x, weights,
                evaluate_error=show_error and evaluate_error,
                error_mode='auto',
                **hist_options
            )
            if mask_condition is not None:
                histogram.mask(mask_condition)
                
            return histogram

        # Handle stacked histograms
        if len(components) > 1:
            histograms = {
                subtarget: get_histogram(options)
                for subtarget, options in components.items()
            }
            histogram = StackedHistogram(histograms)
            
            if hist_options.get('normalize'):
                density = hist_options.get('divide_bin_width', False)
                histogram.normalize(density=density, inplace=True)
                
            self.histograms.update(histograms)
        else:
            options = next(iter(components.values()))
            histogram = get_histogram(options)

        self.draw_histogram_data(
            ax,
            histogram,
            plot_format=plot_format,
            error_format=error_format,
            styles=styles,
            masked_styles=masked_styles,
            error_styles=error_styles,
            domain=target
        )

    def draw(
        self,
        column_name: str,
        weight_name: Optional[str] = None,
        targets: Optional[List[str]] = None,
        selection: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        unit: Optional[str] = None,
        bins: Union[int, Sequence[float]] = 25,
        bin_range: Optional[Sequence[float]] = None,
        clip_weight: bool = True,
        underflow: bool = False,
        overflow: bool = False,
        divide_bin_width: bool = False,
        normalize: bool = True,
        show_error: bool = True,
        stacked: bool = False,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        ymin: Optional[float] = None,
        ymax: Optional[float] = None,
        ypad: float = 0.3,
        variable_scale: Optional[float] = None,
        logx: bool = False,
        logy: bool = False,
        comparison_options: Optional[Dict[str, Any]] = None,
        legend_order: Optional[List[str]] = None
    ) -> Union[Axes, Tuple[Axes, Axes]]:
        """
        Draw the plot with specified parameters.

        Parameters
        ----------
        column_name : str
            Name of the variable in the dataframe(s).
        weight_name : str, optional
            Name of the weight column, by default None.
        targets : List[str], optional
            List of target inputs to be included in the plot, by default None 
            (i.e. all inputs are included).
        selection : str, optional
            Filter the data with the given selection (a boolean expression), by default None.
            The selection is applied before any variable scaling.
        xlabel : str, optional
            Label of x-axis, by default "".
        ylabel : str, optional
            Label of y-axis, by default "Fraction of Events / {bin_width:.2f}{unit}".
        unit : str, optional
            Unit of the variable, by default None.
        bins : Union[int, Sequence], optional
            Number of bins or bin edges, by default 25.
        bin_range : Sequence, optional
            Range of histogram bins, by default None.
        clip_weight : bool
            If True, ignore data outside given range when evaluating total weight used in normalization, by default True.
        underflow : bool
            Include underflow data in the first bin, by default False.
        overflow : bool
            Include overflow data in the last bin, by default False.
        divide_bin_width : bool
            Divide each bin by the bin width, by default False.
        normalize : bool
            Normalize the sum of weights to one, by default True.
        show_error : bool
            Whether to display data error, by default False.
        stacked : bool
            Do a stacked plot, by default False.
        xmin : float, optional
            Minimum range of x-axis, by default None.
        xmax : float, optional
            Maximum range of x-axis, by default None.
        ymin : float, optional
            Minimum range of y-axis, by default None.
        ymax : float, optional
            Maximum range of y-axis, by default None.
        ypad : float, optional
            Fraction of the y-axis that should be padded, by default 0.3.
            This options will be ignored if ymax is set.
        variable_scale : float, optional
            Rescale variable values by a factor, by default None.
        logy : bool, optional
            Use log scale for y-axis, by default False.
        comparison_options : Union[Dict, List[Dict]], optional
            Instructions for making comparison plots, by default None.
        legend_order : List[str], optional
            Order of legend labels, by default None.

        Returns
        -------
        Axes or Tuple[Axes, Axes]
            Axes object(s) for the plot. If comparison is drawn, returns a tuple of axes.

        Raises
        ------
        RuntimeError
            If no targets to draw.
        """
        plot_options = self.resolve_plot_options(
            self.plot_options,
            targets=targets,
            stacked=stacked,
            show_error=show_error,
        )
        comparison_options = self.resolve_comparison_options(
            comparison_options,
            plot_options
        )
        
        relevant_samples = self.get_relevant_samples(plot_options)
        if not relevant_samples:
            raise RuntimeError('No targets to draw')

        if comparison_options is not None:
            ax, ax_ratio = self.draw_frame(frametype='ratio', logx=logx, logy=logy)
        else:
            ax = self.draw_frame(frametype='single', logx=logx, logy=logy)

        if bin_range is None and isinstance(bins, int):
            bin_range = self.deduce_bin_range(
                relevant_samples,
                column_name,
                variable_scale=variable_scale
            )
            self.stdout.info(
                f"Using deduced bin range ({bin_range[0]:.3f}, {bin_range[1]:.3f})"
            )

        self.reset_metadata()
        hist_options = {
            "bins": bins,
            "bin_range": bin_range,
            "underflow": underflow,
            "overflow": overflow,
            "normalize": normalize,
            "clip_weight": clip_weight,
            "divide_bin_width": divide_bin_width
        }
        
        data_options = {
            'column_name': column_name,
            'weight_name': weight_name,
            'variable_scale': variable_scale,
            'selection': selection
        }

        for target, options in plot_options.items():
            self.draw_single_target(
                ax,
                target=target,
                hist_options=hist_options,
                **options,
                **data_options
            )

        xlabel = self.resolve_xlabel(
            xlabel=xlabel,
            unit=unit
        )
        ylabel = self.resolve_ylabel(
            ylabel=ylabel,
            unit=unit,
            normalize=normalize,
            divide_bin_width=divide_bin_width
        )

        self.finalize()

        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, ypad=ypad)

        if self.config['draw_legend']:
            if legend_order is None:
                legend_order = self.get_labelled_legend_domains()
            self.draw_legend(ax, targets=legend_order)

        if comparison_options is not None:
            components = comparison_options.pop('components')
            for options in components:
                self.draw_comparison_data(
                    ax_ratio,
                    **options
                )
            self.decorate_comparison_axis(ax, ax_ratio, **comparison_options)
            return ax, ax_ratio

        return ax