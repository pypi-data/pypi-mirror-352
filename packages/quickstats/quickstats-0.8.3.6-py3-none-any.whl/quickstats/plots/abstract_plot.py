"""
Enhanced plotting utilities with customizable styles, colors, labels, and annotations.

This module provides a flexible base class for creating plots with rich customization
options for styles, colors, labels, and annotations. It supports both single plots
and ratio plots with comprehensive configuration capabilities.
"""

from __future__ import annotations

from typing import (
    Optional, Union, Dict, List, Tuple, Callable, Sequence, Any,
    ClassVar, TypeVar, cast
)
from dataclasses import dataclass
from collections import defaultdict
from itertools import cycle
from copy import deepcopy

import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.legend import Legend

from quickstats import AbstractObject, NamedTreeNode
from quickstats.core import mappings as mp
from quickstats.core.typing import ArrayLike
from quickstats.utils.common_utils import insert_periodic_substr
from quickstats.utils.string_utils import unique_string
from quickstats.maths.histograms import HistComparisonMode

from . import template_styles, template_analysis_label_options
from .core import PlotFormat, ErrorDisplayFormat, FrameType
from .colors import (
    ColorType,
    ColormapType,
    get_color_cycle,
    get_cmap,
)
from .template import (
    single_frame,
    ratio_frame,
    multirow_frame,
    format_axis_ticks,
    centralize_axis,
    remake_handles,
    draw_multiline_text,
    resolve_handle_label,
    get_axis_limits,
    CUSTOM_HANDLER_MAP,
    TransformType,
    CustomHandlerTuple,
)
from .artists import (
    LazyArtist,
    Point,
    VLine,
    HLine,
    FillBetween,
    ErrorBand,
    Annotation,
    Text,
    Ellipse
)

# Type variables for better type hints
T = TypeVar('T')
StylesType = Union[Dict[str, Any], str]
DomainType = Union[List[str], str]

class PlottingError(Exception):
    """Base exception for plotting-related errors."""
    pass


@dataclass
class LegendEntry:
    """Data structure for legend entries."""
    handle: Any  # Could be Artist, tuple/list of Artists, Collection, etc.
    label: str
    axis_index: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary format."""
        return {
            "handle": self.handle,
            "label": self.label
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LegendEntry":
        """Create entry from dictionary format."""
        return cls(
            handle=data["handle"],
            label=data["label"]
        )
        
    def has_valid_label(self) -> bool:
        """Check if entry has a valid label for legend."""
        return bool(self.label and not self.label.startswith('_'))

class AbstractPlot(AbstractObject):
    """
    A base class for creating plots with customizable styles, colors, labels, and annotations.

    This class provides a foundation for creating plots with rich customization options,
    supporting both single plots and ratio plots. It handles styles, colors, labels,
    and annotations with comprehensive configuration capabilities.

    Parameters
    ----------
    color_map : Optional[Dict[str, ColorType]], default None
        Mapping of labels to colors
    color_cycle : Optional[ColormapType], default None
        Color cycle for sequential coloring
    label_map : Optional[Dict[str, str]], default None
        Mapping of internal labels to display labels
    styles : Optional[StylesType], default None
        Global styles for plot elements
    config : Optional[Dict[str, Any]], default None
        Plot configuration parameters
    styles_map : Optional[Dict[str, StylesType]], default None
        Target-specific style updates
    config_map : Optional[Dict[str, Dict[str, Any]]], default None
        Target-specific configuration updates
    analysis_label_options : Optional[Union[str, Dict[str, Any]]], default None
        Options for analysis labels
    figure_index : Optional[int], default None
        Index for the figure
    verbosity : Union[int, str], default "INFO"
        Logging verbosity level

    Attributes
    ----------
    COLOR_MAP : Dict[str, ColorType]
        Default color mapping
    COLOR_CYCLE : str
        Default color cycle name
    LABEL_MAP : Dict[str, str]
        Default label mapping
    STYLES : Dict[str, Any]
        Default styles
    CONFIG : Dict[str, Any]
        Default configuration

    Examples
    --------
    >>> # Create a basic plot
    >>> plot = AbstractPlot()
    >>> plot.set_color_cycle('viridis')
    >>> plot.add_point(1, 1, label='Point 1')
    >>> ax = plot.draw_frame()
    >>> plot.finalize()
    >>> plot.draw_legends()

    >>> # Create a ratio plot with custom styles
    >>> plot = AbstractPlot(styles={'figure': {'figsize': (10, 8)}})
    >>> ax_main, ax_ratio = plot.draw_frame(frametype="ratio")
    >>> plot.draw_axis_labels(ax_main, xlabel='X', ylabel='Y')
    """

    COLOR_MAP: Dict[str, ColorType] = {}
    COLOR_CYCLE: str = "default"
    LABEL_MAP: Dict[str, str] = {}
    STYLES: Dict[str, Any] = {
        "reference_line": {
            "color": "gray",
            "linestyle": "--",
            "zorder": 0,            
        }
    }
    CONFIG: Dict[str, Any] = {
        "xlabellinebreak": 50,
        "ylabellinebreak": 50,
        'draw_legend': True,
        'draw_reference_line': True,
        'fill_polygon_border': False,
        'clip_legend_patch': True
    }
    STYLES_MAP = {}
    CONFIG_MAP = {}
    COLOR_CYCLE_MAP = {}

    def __init__(
        self,
        color_map: Optional[Dict[str, ColorType]] = None,
        color_cycle: Optional[ColormapType] = None,
        color_cycle_map: Optional[Dict[str, ColormapType]] = None,
        label_map: Optional[Dict[str, str]] = None,
        styles: Optional[StylesType] = None,
        config: Optional[Dict[str, Any]] = None,
        styles_map: Optional[Dict[str, StylesType]] = None,
        config_map: Optional[Dict[str, Dict[str, Any]]] = None,
        analysis_label_options: Optional[Union[str, Dict[str, Any]]] = None,
        figure_index: Optional[int] = None,
        verbosity: Union[int, str] = "INFO",
    ) -> None:
        """Initialize the AbstractPlot with customization options."""
        super().__init__(verbosity=verbosity)

        self._artists: Dict[str, LazyArtist] = {}
        self._artist_axis_indices: Dict[str, int] = {}
        self._figure: Optional[plt.Figure] = None
        
        # Initialize properties with validation
        self._color_index = 0
        self._init_color_map(color_map)
        self._init_color_cycle_map(color_cycle, color_cycle_map)
        self._init_label_map(label_map)
        self._init_styles_map(styles, styles_map)
        self._init_config_map(config, config_map)
        self._init_analysis_options(analysis_label_options)
        self.figure_index = figure_index

        self.reset()

    def _init_color_map(
        self, 
        color_map: Optional[Dict[str, ColorType]]
    ) -> None:
        """Initialize color map with validation."""
        try:
            data = mp.merge_classattr(type(self), 'COLOR_MAP', copy=True)
            data &= color_map
            self._color_map = NamedTreeNode.from_mapping(data)
        except Exception as e:
            raise PlottingError(f"Failed to initialize color map: {str(e)}") from e

    def _parse_color_cycle(
        self,
        color_cycle: Optional[ColormapType]
    ):
        color_cycle = color_cycle or self.COLOR_CYCLE
        cmap = get_cmap(color_cycle)
        # Check if colormap has colors attribute
        if hasattr(cmap, 'colors'):
            color_cycle = cycle(cmap.colors)
        else:
            # For continuous colormaps that don't have colors attribute
            # Sample N colors from the colormap
            N = 256  # or some other appropriate number
            color_cycle = cycle(self.cmap(np.linspace(0, 1, N)))
        return cmap, color_cycle
                
    def _init_color_cycle_map(
        self, 
        color_cycle: Optional[ColormapType] = None,
        color_cycle_map: Optional[Dict[str, ColormapType]] = None,
    ) -> None:
        """Initialize color cycle map with validation."""
        try:
            cmap, color_cycle = self._parse_color_cycle(color_cycle)
            self._cmap_map = NamedTreeNode(data=cmap)
            self._color_cycle_map = NamedTreeNode(data=color_cycle)
            # domain-specific coloy cycles
            domain_data = mp.merge_classattr(
                type(self), 
                'COLOR_CYCLE_MAP', 
                copy=True,
            )
            self.update_color_cycle_map(domain_data)
            self.update_color_cycle_map(color_cycle_map)
            self.reset_color_index()
        except Exception as e:
            raise PlottingError(f"Failed to set color cycle: {str(e)}") from e

    def _init_label_map(
        self, 
        label_map: Optional[Dict[str, str]] = None
    ) -> None:
        """Initialize label map with validation."""
        try:
            data = mp.merge_classattr(type(self), 'LABEL_MAP', copy=True)
            if label_map is not None:
                data &= label_map
            self._label_map = NamedTreeNode.from_mapping(data)
        except Exception as e:
            raise PlottingError(f"Failed to initialize label map: {str(e)}") from e

    def _init_styles_map(
        self, 
        styles: Optional[StylesType] = None,
        styles_map: Optional[Dict[str, StylesType]] = None
    ) -> None:
        """Initialize styles map with validation."""
        try:
            # global styles
            data = template_styles.get()
            data &= mp.merge_classattr(
                type(self), 
                'STYLES', 
                copy=True,
                parse=template_styles.parse
            )
            data &= template_styles.parse(styles)
            self._styles_map = NamedTreeNode(data=data)
            # domain-specific styles
            domain_data = mp.merge_classattr(
                type(self), 
                'STYLES_MAP', 
                copy=True,
            )
            self.update_styles_map(domain_data)
            self.update_styles_map(styles_map)
        except Exception as e:
            raise PlottingError(f"Failed to initialize styles map: {str(e)}") from e

    def _init_config_map(
        self, 
        config: Optional[Dict[str, Any]] = None,
        config_map: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize configuration map with validation."""
        try:
            # global config
            data = mp.merge_classattr(type(self), 'CONFIG', copy=True)
            data &= config
            self._config_map = NamedTreeNode(data=data)
            # domain-specific config
            domain_data = mp.merge_classattr(
                type(self), 
                'CONFIG_MAP', 
                copy=True,
            )
            self.update_config_map(domain_data)
            self.update_config_map(config_map)
        except Exception as e:
            raise PlottingError(f"Failed to initialize config map: {str(e)}") from e

    def _init_analysis_options(
        self,
        options: Optional[Union[str, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """Initialize analysis label options with validation."""
        if options is None:
            self._analysis_label_options = None
            return
        try:
            self._analysis_label_options = template_analysis_label_options.parse(options)
        except Exception as e:
            raise PlottingError(
                f"Failed to initialize analysis label options: {str(e)}"
            ) from e

    @property
    def color_map(self) -> NamedTreeNode:
        return self._color_map

    @property
    def cmap(self):
        return self._cmap_map.data    

    @property
    def color_cycle(self):
        return self._color_cycle_map.data

    @property
    def cmap_map(self) -> NamedTreeNode:
        return self._cmap_map
        
    @property
    def color_cycle_map(self) -> NamedTreeNode:
        return self._color_cycle_map

    @property
    def label_map(self) -> NamedTreeNode:
        return self._label_map

    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration dictionary."""
        return self._config_map.data

    @property
    def styles(self) -> Dict[str, Any]:
        """Get the styles dictionary."""
        return self._styles_map.data

    @property
    def config_map(self) -> NamedTreeNode:
        return self._config_map

    @property
    def styles_map(self) -> NamedTreeNode:
        return self._styles_map

    @property
    def analysis_label_options(self) -> Optional[Dict[str, Any]]:
        return self._analysis_label_options

    @property
    def color_index(self) -> int:
        return self._color_index

    @property
    def handles(self) -> Dict[str, Artist]:
        handles = {}
        for domain in self.legend_data.domains:
            handles[domain] = self.legend_data[domain].handle
        return handles

    @property
    def labels(self) -> Dict[str, Artist]:
        labels = {}
        for domain in self.legend_data.domains:
            labels[domain] = self.legend_data[domain].label
        return labels

    @property
    def figure(self):
        return self._figure

    @property
    def axes(self) -> Optional[List[Axes]]:
        if self._figure is None:
            return None
        return self._figure.get_axes()

    @property
    def artists(self) -> Dict[str, ArtistData]:
        return self._artists
        
    @property
    def artist_axis_indices(self) -> Dict[str, int]:
        return self._artist_axis_indices
        
    def update_color_cycle_map(
        self, 
        data: Optional[Dict[str, ColormapType]] = None
    ) -> None:
        """
        Update the color cycle map with additional color cycles.

        Parameters
        ----------
        data : Optional[Dict[str, StylesType]], default None
            Additional color cycle mappings to apply

        Raises
        ------
        PlottingError
            If update fails
        """
        if not data:
            return
            
        try:
            for domain, domain_data in data.items():
                domain_cmap, domain_color_cycle = self._parse_color_cycle(domain_data)
                self._cmap_map[domain] = domain_cmap
                self._color_cycle_map[domain] = domain_color_cycle
        except Exception as e:
            raise PlottingError(
                f"Failed to update color cycle map: {str(e)}"
            ) from e
        
    def update_styles_map(
        self, 
        data: Optional[Dict[str, StylesType]] = None
    ) -> None:
        """
        Update the styles map with additional styles.

        Parameters
        ----------
        data : Optional[Dict[str, StylesType]], default None
            Additional style mappings to apply

        Raises
        ------
        PlottingError
            If style update fails
        """
        if not data:
            return
            
        try:
            for domain, domain_data in data.items():
                self._styles_map[domain] = template_styles.parse(domain_data)
        except Exception as e:
            raise PlottingError(
                f"Failed to update styles map: {str(e)}"
            ) from e

    def update_config_map(
        self, 
        data: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """
        Update the configuration map with additional settings.

        Parameters
        ----------
        data : Optional[Dict[str, Dict[str, Any]]], default None
            Additional configuration settings to apply

        Raises
        ------
        PlottingError
            If configuration update fails
        """
        if not data:
            return
            
        try:
            for domain, domain_data in data.items():
                self._config_map[domain] = mp.concat((domain_data,), copy=True)
        except Exception as e:
            raise PlottingError(
                f"Failed to update config map: {str(e)}"
            ) from e

    def get_target_styles(
        self,
        artist: Optional[str] = None,
        target: Optional[str] = None,
        merge: bool = True,
    ) -> Dict[str, Any]:
        """
        Get styles for a specific target.

        Parameters
        ----------
        ...

        Returns
        -------
        Dict[str, Any]
            ...
        """
        components = []
        if merge and target is not None:
            components.append(
                self.styles if artist is None
                else self.styles.get(artist, {})
            )
        styles = self.styles_map.get(target, {})
        components.append(
            styles if artist is None
            else styles.get(artist, {})
        )
        return defaultdict(dict, mp.concat(components, copy=True))

    def get_target_config(
        self,
        key: str,
        target: Optional[str] = None,
        fallback: bool = True,
    ) -> Dict[str, Any]:
        config = self.config_map.get(target)
        if (config is None) or (key not in config) and fallback:
            config = self.config
        if key not in config:
            raise ValueError(f'config option not set: {key}')
        return config[key]

    def get_target_color(
        self,
        name: str,
        target: Optional[str] = None,
        fallback: bool = True
    ) -> Optional[str]:
        """
        Get color for a domain.

        Parameters
        ----------
        name : str
            The name to get the color for
        ...
        fallback : bool, default False
            Whether to fall back to name-only lookup

        Returns
        -------
        Optional[str]
            The target color if found
        """
        domain = self.color_map.format(target, name)
        if domain not in self.color_map and fallback:
            return self.color_map.get(name)
        return self.color_map.get(domain)

    def get_target_cmap(
        self,
        target: Optional[str] = None,
        fallback: bool = True
    ) -> Any:
        """
        Get cmap for a target.

        Parameters
        ----------
        ...

        Returns
        -------
        """
        default = self.cmap if fallback else None
        return self.cmap_map.get(target, default)

    def get_target_label(
        self,
        name: str,
        target: Optional[str] = None,
        fallback: bool = True
    ) -> Optional[str]:
        """
        Get label for a domain.

        Parameters
        ----------
        name : str
            The name to get label for
        ...
        fallback : bool, default False
            Whether to fall back to name-only lookup

        Returns
        -------
        Optional[str]
            The target label if found
        """
        domain = self.label_map.format(target, name)
        if domain not in self.label_map and fallback:
            return self.label_map.get(name)
        return self.label_map.get(domain)

    def add_artist(
        self,
        artist: LazyArtist,
        name: Optional[str] = None,
        axis_index: int = 0
    ) -> None:
        if not isinstance(artist, LazyArtist):
            raise TypeError(f'`artist` must be an instance of LazyArtist.')
        name = name or f'_{unique_string()}'
        if (name in self._artists):
            raise PlottingError(f"Artist redeclared with name: {name}")
        self._artists[name] = artist
        self._artist_axis_indices[name] = axis_index

    def add_point(
        self,
        x: float,
        y: float,
        label: Optional[str] = None,
        name: Optional[str] = None,
        axis_index: int = 0,
        **kwargs
    ) -> None:
        """
        Add a point to the plot.

        Parameters
        ----------
        x : float
            X-coordinate
        y : float
            Y-coordinate
        label : Optional[str], default None
            Point label
        name : Optional[str], default None
            Point name for legend
        styles : Optional[Dict[str, Any]], default None
            Point styles

        Raises
        ------
        PlottingError
            If point with same name already exists
        """
        artist = Point(x=x, y=y, label=label, styles=kwargs)
        self.add_artist(artist, name=name or label, axis_index=axis_index)

    def add_fill_between(
        self,
        x: ArrayLike,
        y1: ArrayLike,
        y2: ArrayLike=0,
        label: Optional[str] = None,
        name: Optional[str] = None,
        axis_index: int = 0,
        **kwargs
    ) -> None:
        artist = FillBetween(x=x, y1=y1, y2=y2, label=label, styles=kwargs)
        self.add_artist(artist, name=name or label, axis_index=axis_index)

    def add_ellipse(
        self,
        xy: Tuple[float, float],
        width: float,
        height: float,
        angle: float = 0,
        label: Optional[str] = None,
        name: Optional[str] = None,
        axis_index: int = 0,
        **kwargs
    ) -> None:
        artist = Ellipse(xy=xy, width=width, height=height, angle=angle, label=label, styles=kwargs)
        self.add_artist(artist, name=name or label, axis_index=axis_index)

    def add_errorband(
        self,
        x: ArrayLike,
        y: ArrayLike,
        yerrlo: ArrayLike,
        yerrhi: ArrayLike,        
        xerr: Optional[ArrayLike] = None,
        label: Optional[str] = None,
        name: Optional[str] = None,
        plot_styles: Optional[Dict[str, Any]]=None,
        fill_styles: Optional[Dict[str, Any]]=None,
        axis_index: int = 0,
    ) -> None:
        styles_map = {
            'plot': plot_styles,
            'fill_between': fill_styles
        }
        artist = ErrorBand(x=x, y=y, yerrlo=yerrlo, yerrhi=yerrhi, xerr=xerr, label=label, styles_map=styles_map)
        self.add_artist(artist, name=name or label, axis_index=axis_index)

    def add_vline(
        self,
        x: float,
        ymin:float=0,
        ymax:float=1,
        label: Optional[str] = None,
        name: Optional[str] = None,
        axis_index: int = 0,
        **kwargs
    ) -> None:
        artist = VLine(x=x, ymin=ymin, ymax=ymax, label=label, styles=kwargs)
        self.add_artist(artist, name=name or label, axis_index=axis_index)

    def add_hline(
        self,
        y: float,
        xmin:float=0,
        xmax:float=1,
        label: Optional[str] = None,
        name: Optional[str] = None,
        axis_index: int = 0,
        **kwargs
    ) -> None:
        artist = HLine(y=y, xmin=xmin, xmax=xmax, label=label, styles=kwargs)
        self.add_artist(artist, name=name or label, axis_index=axis_index)

    def add_annotation(
        self, 
        text: str,
        xy: Tuple[float, float],
        label: Optional[str] = None,
        name: Optional[str] = None,
        axis_index: int = 0,
        **kwargs
    ) -> None:
        """
        Add an annotation to the plot.

        Parameters
        ----------
        text : str
            Annotation text
        **kwargs : Any
            Additional annotation options
        """
        artist = Annotation(text=text, xy=xy, label=label, styles=kwargs)
        self.add_artist(artist, name=name or label, axis_index=axis_index)

    def add_text(
        self,
        text: str,
        x: float,
        y: float,
        dy: float = 0.01,
        transform_x: TransformType = "axis",
        transform_y: TransformType = "axis",
        label: Optional[str] = None,
        name: Optional[str] = None,
        axis_index: int = 0,
        **kwargs
    ) -> None:
        artist = Text(text=text, x=x, y=y, dy=dy,
                      transform_x=transform_x,
                      transform_y=transform_y,
                      label=label, styles=kwargs)
        self.add_artist(artist, name=name or label, axis_index=axis_index)
        
    def set_color_cycle(self, color_cycle: Optional[ColormapType] = None) -> None:
        """
        Set the color cycle for the plot.
    
        Parameters
        ----------
        color_cycle : Optional[ColormapType], default None
            The color cycle to use. Can be:
            - A string name of a colormap
            - A Colormap instance
            - A list of colors
    
        Raises
        ------
        PlottingError
            If colormap creation fails or colormap has no colors
        """
        try:
            self.update_color_cycle_map({None: color_cycle})
            self.reset_color_index()
        except Exception as e:
            raise PlottingError(f"Failed to set color cycle: {str(e)}") from e

    def get_axis_index(self, ax: Axes, raise_error: bool = False) -> Optional[int]:
        if (self.axes is None):
            return None
        if (ax not in self.axes):
            if raise_error:
                raise ValueError('`ax` is not an axis in the current figure')
            return None
        return self.axes.index(ax)

    def get_colors(self) -> List[CorlorType]:
        """
        Get the list of colors from the current color cycle.

        Returns
        -------
        List[CorlorType]
            List of colors
        """
        return get_color_cycle(self.cmap).by_key()["color"]

    def get_next_color(self) -> CorlorType:
        colors = self.get_colors()
        n_colors = len(colors)
        if self._color_index == n_colors:
            self.stdout.warning(
                'Number of artists exceeds available colors in the color map. Colors will be recycled.'
            )
        color = colors[self._color_index % n_colors]
        self._color_index += 1
        return color

    def reset_color_index(self) -> None:
        self._color_index = 0
        
    def get_default_legend_order(self) -> List[str]:
        """
        Get the default legend order.

        Returns
        -------
        List[str]
            Default legend order
        """
        return []

    def reset_legend_data(self) -> None:
        """Reset legend data and order."""
        self.legend_data = NamedTreeNode()
        self.legend_order = self.get_default_legend_order()
        
    def get_labelled_legend_domains(self) -> List[str]:
        """
        Get list of domains that have valid legend labels.
    
        Returns
        -------
        List[str]
            List of domain names with valid legend labels
        """
        try:
            return [
                domain for domain in self.legend_data.domains
                if cast(LegendEntry, self.legend_data.get(domain)).has_valid_label()
            ]
        except Exception as e:
            raise PlottingError(
                f"Failed to get labelled legend domains: {str(e)}"
            ) from e

    def get_handle(self, domain: str) -> Optional[Artist]:
        """
        Get legend handle for a domain.
    
        Parameters
        ----------
        domain : str
            The domain to get handle for
    
        Returns
        -------
        Optional[Artist]
            The legend handle if found
        """
        entry = self.legend_data.get(domain)
        return entry.handle if entry is not None else None

    def update_legend_handles(
        self,
        handles: Dict[str, Artist],
        domain: Optional[str] = None,
        ax: Optional[Axes] = None,
    ) -> None:
        """
        Update legend handles.
    
        Parameters
        ----------
        handles : Dict[str, Artist]
            Mapping of names to handles
        domain : Optional[str], default None
            The domain context
    
        Raises
        ------
        PlottingError
            If handle validation fails
        """
        try:
            resolved_handles = {}
            axis_index = self.get_axis_index(ax)
            for name, handle in handles.items():
                key = (
                    domain if name is None
                    else self.legend_data.format(domain, name) if domain
                    else name
                )
                handle, label = resolve_handle_label(handle)
                entry = LegendEntry(handle=handle, label=label, axis_index=axis_index)
                self.legend_data[key] = entry
                
        except Exception as e:
            raise PlottingError(f"Failed to update legend handles: {str(e)}") from e
            
    def get_legend_handles_labels(
        self,
        domains: Optional[DomainType] = None,
        targets: Optional[List[str]] = None,
        ax: Optional[Axes] = None
    ) -> Tuple[List[Artist], List[str]]:
        """
        Get handles and labels for legend creation.
    
        Parameters
        ----------
        domains : Optional[DomainType], default None
            Domains to include in the legend
        targets : Optional[List[str]], default None
            Custom targets to include in the result.
    
        Returns
        -------
        Tuple[List[Artist], List[str]]
            Tuple of (handles, labels) for creating the legend
    
        Notes
        -----
        If domains is None, all domains are included.
        Handles and labels are returned in the order specified by legend_order.
        """
        if domains is None:
            domains = [None]
        elif isinstance(domains, str):
            domains = [domains]
    
        handles: List[Artist] = []
        labels: List[str] = []

        if targets is None:
            targets = self.legend_order or self.get_labelled_legend_domains()

        axis_index = None if ax is None else self.get_axis_index(ax, raise_error=True)
        try:
            for name in targets:
                for domain in domains:
                    key = (
                        self.legend_data.format(domain, name)
                        if domain else name
                    )

                    entry = self.legend_data.get(key)
                    if entry is None:
                        continue
                        
                    if entry.label.startswith("_"):
                        continue

                    if ((entry.axis_index is not None) and
                        (axis_index is not None) and
                        (entry.axis_index != axis_index)):
                        continue
                        
                    handles.append(entry.handle)
                    labels.append(entry.label)
                        
            return handles, labels
                
        except Exception as e:
            raise PlottingError(
                f"Failed to get legend handles and labels: {str(e)}"
            ) from e

    def add_legend_decoration(
        self, 
        decorator: Artist,
        targets: List[str],
        domain: Optional[str] = None
    ) -> None:
        """
        Add a decorator to specified legend entries.
    
        Parameters
        ----------
        decorator : Artist
            The matplotlib artist to use as a decorator
        targets : List[str]
            List of legend entry names to decorate
        domain : Optional[str], default None
            Domain context for the targets
    
        Raises
        ------
        PlottingError
            If decoration fails for any target
        ValueError
            If decorator is not a valid Artist
        """
        if not isinstance(decorator, Artist):
            raise ValueError(f"Decorator must be an Artist, got {type(decorator)}")
    
        try:
            if domain is not None:
                targets = [
                    self.legend_data.format(domain, target) 
                    for target in targets
                ]
                    
            for target in targets:
                entry = self.legend_data.get(target)
                if entry is None:
                    continue
                        
                handle = entry.handle
                if isinstance(handle, (list, tuple)):
                    new_handle = (*handle, decorator)
                else:
                    new_handle = (handle, decorator)
                        
                # Update the entry with new handle
                self.legend_data[target] = LegendEntry(
                    handle=new_handle,
                    label=entry.label
                )
                    
        except Exception as e:
            raise PlottingError(
                f"Failed to add legend decoration: {str(e)}"
            ) from e

    def draw_frame(
        self, 
        frametype: Union[str, FrameType] = 'single',
        **kwargs: Dict[str, Any]
    ) -> Union[Axes, Tuple[Axes, ...]]:
        """
        Draw the plot frame.

        Parameters
        ----------
        frametype : str or FrameType, default "single"
            Type of frame to draw
        **kwargs : Any
            Additional frame options

        Returns
        -------
        Union[Axes, Tuple[Axes, ...]]
            The created axes
        """
        frametype = FrameType.parse(frametype)
        styles = mp.concat((self.styles, kwargs.pop('styles', None)))
        standard_kwargs = {
            "analysis_label_options" : self.analysis_label_options,
            "figure_index" : self.figure_index,
            **kwargs
        }
        if frametype == FrameType.SINGLE:
            figure, ax = single_frame(
                styles=styles,
                prop_cycle=get_color_cycle(self.cmap),
                **standard_kwargs
            )
        elif frametype == FrameType.DOUBLE:
            figure, ax = ratio_frame(
                styles=styles,
                prop_cycle=get_color_cycle(self.cmap),
                **standard_kwargs
            )
        elif frametype == FrameType.MULTIROW:
            figure, ax = multirow_frame(
                main_styles=styles,
                main_prop_cycle=get_color_cycle(self.cmap),
                styles_map=self.styles_map,
                prop_cycle_map=self.color_cycle_map,
                **standard_kwargs
            )
        else:
            raise ValueError(f'Unknown frame type: {frametype}')

        self._figure = figure
        return ax

    def draw_legends(
        self,
        handles: Optional[List[Artist]] = None,
        labels: Optional[List[str]] = None,
        handler_map: Optional[Dict[Any, Any]] = None,
        domains: Optional[DomainType] = None,
        targets: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[Optional[Legend]]:
        if not self.axes:
            return
        for ax in self.axes:
            self.draw_legend(
                ax,
                handles=handles,
                labels=labels,
                handler_map=handler_map,
                domains=domains,
                targets=targets,
                **kwargs
            )
    
    def draw_legend(
        self,
        ax: Axes,
        handles: Optional[List[Artist]] = None,
        labels: Optional[List[str]] = None,
        handler_map: Optional[Dict[Any, Any]] = None,
        domains: Optional[DomainType] = None,
        targets: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Optional[Legend]:
        """
        Draw the plot legend.

        Parameters
        ----------
        ax : Axes
            The axes to draw on
        handles : Optional[List[Artist]], default None
            Legend handles
        labels : Optional[List[str]], default None
            Legend labels
        handler_map : Optional[Dict[Any, Any]], default None
            Custom handler mappings
        domains : Optional[DomainType], default None
            Domains to include
        **kwargs : Any
            Additional legend options

        Returns
        -------
        Optional[Legend]
            The created legend if handles exist
        """
        if handles is None and labels is None:
            handles, labels = self.get_legend_handles_labels(domains, targets=targets, ax=ax)
        if not handles:
            return None

        handler_map = handler_map or {}
        clip_legend_patch = self.config.get('clip_legend_patch', True)
        if (tuple not in handler_map):
            handler_map[tuple] = CustomHandlerTuple(clip_to_patch=clip_legend_patch)
        handler_map = mp.concat((CUSTOM_HANDLER_MAP, handler_map))
        styles = mp.concat((self.styles["legend"], kwargs), copy=True)
        styles["handler_map"] = handler_map

        handles = remake_handles(
            handles,
            polygon_to_line=not self.config.get('box_legend_handle', True),
            fill_border=self.config.get('fill_polygon_border', False),
            border_styles=self.get_target_styles('legend_border'),
        )

        return ax.legend(handles, labels, **styles)

    def draw_axis_labels(
        self,
        ax: Axes,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        xlabellinebreak: Optional[int] = None,
        ylabellinebreak: Optional[int] = None,
        combined_styles: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
    ) -> None:
        """
        Draw axis labels and title.

        Parameters
        ----------
        ax : Axes
            The axes to draw on
        xlabel : Optional[str], default None
            X-axis label
        ylabel : Optional[str], default None
            Y-axis label
        xlabellinebreak : Optional[int], default None
            Character limit for x-label line breaks
        ylabellinebreak : Optional[int], default None
            Character limit for y-label line breaks
        combined_styles : Optional[Dict[str, Any]], default None
            Combined styles for labels
        title : Optional[str], default None
            Plot title
        """
        combined_styles = combined_styles or self.styles
        
        if xlabel is not None:
            if (xlabellinebreak is not None and 
                xlabel.count("$") < 2):  # Don't break LaTeX
                xlabel = insert_periodic_substr(xlabel, xlabellinebreak)
            ax.set_xlabel(xlabel, **combined_styles["xlabel"])
            
        if ylabel is not None:
            if (ylabellinebreak is not None and 
                ylabel.count("$") < 2):  # Don't break LaTeX
                ylabel = insert_periodic_substr(ylabel, ylabellinebreak)
            ax.set_ylabel(ylabel, **combined_styles["ylabel"])
            
        if title is not None:
            ax.set_title(title, **self.styles["title"])

    def draw_axis_components(
        self,
        ax: Axes,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        ylim: Optional[Tuple[float, float]] = None,
        xlim: Optional[Tuple[float, float]] = None,
        xticks: Optional[List[float]] = None,
        yticks: Optional[List[float]] = None,
        xticklabels: Optional[List[str]] = None,
        yticklabels: Optional[List[str]] = None,
        combined_styles: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
    ) -> None:
        """
        Draw axis components including labels, ticks, and limits.

        Parameters
        ----------
        ax : Axes
            The axes to draw on
        xlabel : Optional[str], default None
            X-axis label
        ylabel : Optional[str], default None
            Y-axis label
        ylim : Optional[Tuple[float, float]], default None
            Y-axis limits
        xlim : Optional[Tuple[float, float]], default None
            X-axis limits
        xticks : Optional[List[float]], default None
            X-axis tick positions
        yticks : Optional[List[float]], default None
            Y-axis tick positions
        xticklabels : Optional[List[str]], default None
            X-axis tick labels
        yticklabels : Optional[List[str]], default None
            Y-axis tick labels
        combined_styles : Optional[Dict[str, Any]], default None
            Combined styles for components
        title : Optional[str], default None
            Plot title
        """
        combined_styles = combined_styles or self.styles
        
        # Draw labels
        self.draw_axis_labels(
            ax,
            xlabel,
            ylabel,
            xlabellinebreak=self.config["xlabellinebreak"],
            ylabellinebreak=self.config["ylabellinebreak"],
            combined_styles=combined_styles,
            title=title,
        )

        # Format ticks
        try:
            format_axis_ticks(
                ax,
                **combined_styles["axis"],
                xtick_styles=combined_styles["xtick"],
                ytick_styles=combined_styles["ytick"],
            )
        except Exception as e:
            raise PlottingError(f"Failed to format axis ticks: {str(e)}") from e

        # Set limits and ticks
        if ylim is not None:
            ax.set_ylim(*ylim)
        if xlim is not None:
            ax.set_xlim(*xlim)
        if xticks is not None:
            ax.set_xticks(xticks)
        if yticks is not None:
            ax.set_yticks(yticks)
        if xticklabels is not None:
            ax.set_xticklabels(xticklabels)
        if yticklabels is not None:
            ax.set_yticklabels(yticklabels)

    def set_axis_range(
        self,
        ax: Axes,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        ymin: Optional[float] = None,
        ymax: Optional[float] = None,
        xpadlo: Optional[float] = None,
        xpadhi: Optional[float] = None,
        xpad: Optional[float] = None,
        ypadlo: Optional[float] = None,
        ypadhi: Optional[float] = None,
        ypad: Optional[float] = None,
    ) -> None:
        """
        Set axis ranges with optional padding.

        Parameters
        ----------
        ax : Axes
            The axes to modify
        xmin : Optional[float], default None
            Minimum x-value
        xmax : Optional[float], default None
            Maximum x-value
        ymin : Optional[float], default None
            Minimum y-value
        ymax : Optional[float], default None
            Maximum y-value
        xpadlo : Optional[float], default None
            Lower x-padding fraction
        xpadhi : Optional[float], default None
            Upper x-padding fraction
        xpad : Optional[float], default None
            Symmetric x-padding fraction
        ypadlo : Optional[float], default None
            Lower y-padding fraction
        ypadhi : Optional[float], default None
            Upper y-padding fraction
        ypad : Optional[float], default None
            Symmetric y-padding fraction
        """
        try:
            xlim, ylim = get_axis_limits(
                ax,
                xmin=xmin,
                xmax=xmax,
                ymin=ymin,
                ymax=ymax,
                xpadlo=xpadlo,
                xpadhi=xpadhi,
                xpad=xpad,
                ypadlo=ypadlo,
                ypadhi=ypadhi,
                ypad=ypad,
            )
            ax.set_xlim(*xlim)
            ax.set_ylim(*ylim)
        except Exception as e:
            raise PlottingError(f"Failed to set axis range: {str(e)}") from e

    def decorate_comparison_axis(
        self,
        ax: Axes,
        ax_ratio: Axes,
        mode: Union[HistComparisonMode, str, Callable] = "ratio",
        ylabel: str = "",
        ylim: Optional[Sequence[float]] = None,
        ypad: Optional[float] = 0.1
    ) -> None:
        """
        Decorate a comparison axis (ratio or difference plot).

        Parameters
        ----------
        ax : Axes
            The axes to decorate
        xlabel : str, default ""
            X-axis label
        ylabel : str, default ""
            Y-axis label
        mode : Union[HistComparisonMode, str, Callable], default "ratio"
            Comparison mode
        ylim : Optional[Sequence[float]], default None
            Y-axis limits
        ypad : Optional[float], default 0.1
            Centralization padding
        """
        if ylim is not None:
            ax_ratio.set_ylim(ylim)

        xlabel = ax.get_xlabel()
        do_centralize = ylim is None
        if not callable(mode):
            mode = HistComparisonMode.parse(mode)
            draw_reference_line = self.config.get('draw_reference_line')
            if mode == HistComparisonMode.RATIO:
                if do_centralize:
                    centralize_axis(ax_ratio, which="y", ref_value=1, padding=ypad)
                if draw_reference_line:
                    ax_ratio.axhline(1, **self.styles["reference_line"])
                ylabel = ylabel or "Ratio"
            elif mode == HistComparisonMode.DIFFERENCE:
                if do_centralize:
                    centralize_axis(ax_ratio, which="y", ref_value=0, padding=ypad)
                if draw_reference_line:
                    ax_ratio.axhline(0, **self.styles["reference_line"])
                ylabel = ylabel or "Difference"
        self.draw_axis_components(ax_ratio, xlabel=xlabel, ylabel=ylabel)
        ax.set(xlabel=None)
        ax.tick_params(axis="x", labelbottom=False)
        
    def reset_color_cycle(self) -> None:
        """
        Reset the color cycle to its initial state.

        This method restarts the color cycle from the beginning of the colormap,
        useful when you want to reuse the same color sequence.
        """
        self.color_cycle = cycle(self.cmap.colors)

    def reset_metadata(self) -> None:
        """
        Reset all metadata including legend data and order.

        This method clears all legend-related information and should be called
        when starting a new plot or clearing the current one.
        """
        self._color_index = 0
        self.reset_legend_data()

    def reset_artists(self) -> None:
        self._artists.clear()
        self._artist_axis_indices.clear()

    def reset(self) -> None:
        """Reset all plot data."""
        self.reset_metadata()
        self.reset_artists()

    def draw_artists(self, ax: Axes) -> None:
        axis_index = self.get_axis_index(ax, raise_error=True)
        handles = {}
        for name, artist in self._artists.items():
            if self.artist_axis_indices.get(name, 0) != axis_index:
                continue
            handle = artist.draw(ax, self.styles)
            if not name.startswith('_'):
                handles[name] = handle
        self.update_legend_handles(handles, ax=ax)

    def finalize(self) -> None:
        """
        Finalize the plot by drawing points and annotations.

        Parameters
        ----------
        ax : Axes
            The axes to finalize
        """
        if self.axes is None:
            return
        for ax in self.axes:
            self.draw_artists(ax)
        
    def stretch_axis(
        self,
        ax: Axes,
        xlim: Optional[Tuple[float, float]] = None,
        ylim: Optional[Tuple[float, float]] = None,
    ) -> None:
        """
        Stretch axis limits to encompass new ranges.

        This method extends the current axis limits to include new ranges
        without shrinking the existing view.

        Parameters
        ----------
        ax : Axes
            The axes to modify
        xlim : Optional[Tuple[float, float]], default None
            New x-axis range to include
        ylim : Optional[Tuple[float, float]], default None
            New y-axis range to include

        Raises
        ------
        PlottingError
            If axis stretching fails
        """
        try:
            if xlim is not None:
                curr_xlim = ax.get_xlim()
                ax.set_xlim(
                    min(xlim[0], curr_xlim[0]),
                    max(xlim[1], curr_xlim[1])
                )
                
            if ylim is not None:
                curr_ylim = ax.get_ylim()
                ax.set_ylim(
                    min(ylim[0], curr_ylim[0]),
                    max(ylim[1], curr_ylim[1])
                )
                
        except Exception as e:
            raise PlottingError(
                f"Failed to stretch axis limits: {str(e)}"
            ) from e        

    @staticmethod
    def close_all_figures() -> None:
        """Close all open matplotlib figures."""
        plt.close("all")


    def draw(
        self,
        xlabel:Optional[str]=None,
        ylabel:Optional[str]=None,
        xmin: Optional[float] = None,
        xmax: Optional[float] = None,
        ymin: Optional[float] = None,
        ymax: Optional[float] = None,
        xpad:Optional[float]=None,
        ypad:Optional[float]=None,
        logx:bool=False,
        logy:bool=False,
        legend_order:Optional[List[str]]=None,
    ):
        self.reset_metadata()
        ax = self.draw_frame(logx=logx, logy=logy)

        self.finalize()
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, xpad=xpad, ypad=ypad)
        
        if legend_order is None:
            self.legend_order = list(self.handles)
        else:
            self.legend_order = list(legend_order)
            
        self.draw_legend(ax, targets=legend_order)
        
        return ax