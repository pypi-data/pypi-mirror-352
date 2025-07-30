from __future__ import annotations

from typing import (
    Optional, Union, Dict, List, Tuple, Any
)
from dataclasses import dataclass
import re
from enum import Enum
from itertools import repeat
from contextlib import contextmanager
import warnings

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.axes import Axes 
from matplotlib.axis import Axis
from matplotlib.artist import Artist
from matplotlib.patches import Patch, Rectangle, Polygon, Ellipse
from matplotlib.lines import Line2D
from matplotlib.container import (
    Container,
    ErrorbarContainer,
    BarContainer
)
from matplotlib.image import AxesImage
from matplotlib.text import Text
from matplotlib.collections import (
    Collection,
    PolyCollection,
    LineCollection,
    PathCollection,
)
from matplotlib.ticker import (
    Locator,
    MaxNLocator,
    AutoLocator,
    AutoMinorLocator,
    ScalarFormatter,
    Formatter,
    LogFormatterSciNotation,
)
from matplotlib.legend_handler import (
    HandlerLineCollection,
    HandlerPathCollection,
    HandlerTuple,
)

import quickstats
from quickstats import DescriptiveEnum
from quickstats.core import mappings as mp
from quickstats.core.typing import is_indexable_sequence
from .colors import ColorType, ColormapType
from .settings import AXES_DOMAIN_FMT
from .core import AxisType
from . import template_styles

class TransformType(str, Enum):
    """Valid transform types for matplotlib coordinates."""
    FIGURE = "figure"
    AXIS = "axis"
    DATA = "data"

# Custom exceptions for better error handling
class PlottingError(Exception):
    """Base exception for plotting-related errors."""
    pass

class TransformError(PlottingError):
    """Exception raised for transform-related errors."""
    pass

class StyleError(PlottingError):
    """Exception raised for style-related errors."""
    pass

class ResultStatus(DescriptiveEnum):
    """
    Enumeration for different result statuses with descriptions and display texts.
    
    Attributes
    ----------
    value : int
        The enumeration value
    description : str
        Detailed description of the status
    display_text : str
        Short text for display purposes
    """
    
    FINAL = (0, "Finalised results", "")
    INT = (1, "Internal results", "Internal")
    WIP = (2, "Work in progress results", "Work in Progress")
    PRELIM = (3, "Preliminary results", "Preliminary")
    OPENDATA = (4, "Open data results", "Open Data")
    SIM = (5, "Simulation results", "Simulation")
    SIMINT = (6, "Simulation internal results", "Simulation Internal")
    SIMPRELIM = (7, "Simulation preliminary results", "Simulation Preliminary")

    def __new__(cls, value: int, description: str = "", display_text: str = "") -> ResultStatus:
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.display_text = display_text
        return obj

class NumericFormatter(ScalarFormatter):
    """
    Enhanced numeric formatter for matplotlib axis ticks.
    
    This formatter improves readability by displaying small integers without 
    decimal places while maintaining scientific notation for large numbers.
    """
    
    def __call__(self, x: float, pos: Optional[int] = None) -> str:
        original_format = self.format
        if x.is_integer() and abs(x) < 1e3:
            self.format = re.sub(r"1\.\d+f", r"1.0f", self.format)
        result = super().__call__(x, pos)
        self.format = original_format
        return result


class LogNumericFormatter(LogFormatterSciNotation):
    """Enhanced log formatter with improved handling of special cases."""
    
    def __call__(self, x: float, pos: Optional[int] = None) -> str:
        """Format the log-scale tick value."""
        result = super().__call__(x, pos)
        # result = result.replace('10^{1}', '10').replace('10^{0}', '1')
        return result


class CustomHandlerLineCollection(HandlerLineCollection):
    """Enhanced handler for line collections in legends."""
    
    def create_artists(
        self,
        legend: Any,
        orig_handle: Any,
        xdescent: float,
        ydescent: float,
        width: float,
        height: float,
        fontsize: float,
        trans: transforms.Transform
    ) -> List[Line2D]:
        """Create artists for legend entries with improved centering."""
        artists = super().create_artists(
            legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
        )
        
        # Center lines in legend box
        for artist in artists:
            size = len(artist.get_ydata())
            artist.set_ydata([height / 2.0] * size)
        
        return artists


class CustomHandlerPathCollection(HandlerPathCollection):
    """Enhanced handler for path collections in legends."""
    
    def create_artists(
        self,
        legend: Any,
        orig_handle: Any,
        xdescent: float,
        ydescent: float,
        width: float,
        height: float,
        fontsize: float,
        trans: transforms.Transform
    ) -> List[Collection]:
        """Create artists for legend entries with improved centering."""
        artists = super().create_artists(
            legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
        )
        
        # Center markers in legend box
        for artist in artists:
            artist.set_offsets([(width / 2.0, height / 2.0)])
            
        return artists

class CustomHandlerTuple(HandlerTuple):

    def __init__(self, clip_to_patch: bool = True, **kwargs):
        super().__init__(**kwargs)
        self._clip_to_patch = clip_to_patch

    def create_artists(
        self,
        legend: Any,
        orig_handle: Any,
        xdescent: float,
        ydescent: float,
        width: float,
        height: float,
        fontsize: float,
        trans: transforms.Transform
    ) -> List[Collection]:

        artists = super().create_artists(
            legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
        )

        patch_artist = None
        line_artists = []
        for artist in artists:
            if isinstance(artist, Patch):
                patch_artist = artist
            if isinstance(artist, Line2D):
                line_artists.append(artist)

        if self._clip_to_patch:
            if patch_artist is not None:
                clip_path = patch_artist.get_path(), patch_artist.get_transform()
                for line in line_artists:
                    line.set_clip_path(*clip_path)
                    size = len(line.get_ydata())
                    line.set_ydata([height / 2.0 - ydescent] * size)
                    
        return artists

# Constants
CUSTOM_HANDLER_MAP = {
    LineCollection: CustomHandlerLineCollection(),
    PathCollection: CustomHandlerPathCollection(),
    tuple: CustomHandlerTuple(),
}

AXIS_LOCATOR_MAP = {
    "auto": AutoLocator,
    "maxn": MaxNLocator
}

# Special text formatting patterns with improved regex
SPECIAL_TEXT_PATTERNS = {
    r"\\bolditalic\{(.*?)\}": {"weight": "bold", "style": "italic"},
    r"\\italic\{(.*?)\}": {"style": "italic"},
    r"\\bold\{(.*?)\}": {"weight": "bold"},
}

SPECIAL_TEXT_REGEX = re.compile(
    "|".join(f"({pattern.replace('(', '').replace(')', '')})" for pattern in SPECIAL_TEXT_PATTERNS.keys())
)

def parse_transform(
    target: Optional[TransformType] = None,
    ax: Optional[Axes] = None
) -> Optional[transforms.Transform]:
    """Parse transform objects for coordinate system transformations."""
    try:
        if target == TransformType.FIGURE:
            fig = plt.gcf()
            if fig is None:
                raise TransformError("No current figure available")
            return fig.transFigure
            
        elif target == TransformType.AXIS:
            if ax is None:
                ax = plt.gca()
            if ax is None:
                raise TransformError("No current axes available")
            return ax.transAxes
            
        elif target == TransformType.DATA:
            if ax is None:
                ax = plt.gca()
            if ax is None:
                raise TransformError("No current axes available")
            return ax.transData
            
        elif target is None:
            return None
            
        raise TransformError(f"Invalid transform target: '{target}'")
        
    except Exception as e:
        raise TransformError(f"Failed to create transform: {str(e)}")


def create_transform(
    transform_x: Optional[TransformType] = TransformType.AXIS,
    transform_y: Optional[TransformType] = TransformType.AXIS,
    ax: Optional[Axes] = None
) -> transforms.Transform:
    """
    Create a blended transform from x and y components.
    
    Parameters
    ----------
    transform_x : TransformType
        Transform for x-axis
    transform_y : TransformType
        Transform for y-axis
    ax : Optional[Axes]
        Axes instance to use for transforms
        
    Returns
    -------
    transforms.Transform
        Blended transform object
    """
    return transforms.blended_transform_factory(
        parse_transform(transform_x, ax),
        parse_transform(transform_y, ax)
    )

@contextmanager
def change_axis(axis: Axes) -> None:
    """
    Context manager for temporarily changing the current axis.
    
    Parameters
    ----------
    axis : matplotlib.axes.Axes
        The axis to temporarily set as current
    """
    prev_axis = plt.gca()
    try:
        plt.sca(axis)
        yield
    finally:
        plt.sca(prev_axis)


def handle_has_label(handle: Artist) -> bool:
    """
    Check if an artist handle has a valid label.
    
    Parameters
    ----------
    handle : matplotlib.artist.Artist
        Artist to check for label
        
    Returns
    -------
    bool
        True if handle has a valid label
    """
    try:
        label = handle.get_label()
        return bool(label and not label.startswith('_'))
    except AttributeError:
        return False


def suggest_markersize(nbins: int) -> float:
    """
    Calculate suggested marker size based on number of bins.
    
    Parameters
    ----------
    nbins : int
        Number of bins
        
    Returns
    -------
    float
        Suggested marker size
    """
    BIN_MAX = 200
    BIN_MIN = 40
    SIZE_MAX = 8
    SIZE_MIN = 2
    
    if nbins <= BIN_MIN:
        return SIZE_MAX
    
    if nbins <= BIN_MAX:
        slope = (SIZE_MIN - SIZE_MAX) / (BIN_MAX - BIN_MIN)
        return slope * (nbins - BIN_MIN) + SIZE_MAX
    
    return SIZE_MIN


def format_axis_ticks(
    ax: Axes,
    x_axis: bool = True,
    y_axis: bool = True,
    major_length: int = 16,
    minor_length: int = 8,
    spine_width: int = 2,
    major_width: int = 2,
    minor_width: int = 1,
    direction: str = "in",
    label_bothsides: bool = False,
    tick_bothsides: bool = False,
    labelsize: Optional[int] = None,
    offsetlabelsize: Optional[int] = None,
    x_axis_styles: Optional[Dict[str, Any]] = None,
    y_axis_styles: Optional[Dict[str, Any]] = None,
    xtick_styles: Optional[Dict[str, Any]] = None,
    ytick_styles: Optional[Dict[str, Any]] = None,
) -> None:
    """Format axis ticks with comprehensive styling options."""
    try:
        if x_axis:
            _format_x_axis(
                ax, major_length, minor_length, major_width, minor_width,
                direction, label_bothsides, tick_bothsides, labelsize,
                x_axis_styles, xtick_styles
            )
        
        if y_axis:
            _format_y_axis(
                ax, major_length, minor_length, major_width, minor_width,
                direction, label_bothsides, tick_bothsides, labelsize,
                y_axis_styles, ytick_styles
            )
        
        # Format spines
        for spine in ax.spines.values():
            spine.set_linewidth(spine_width)
        
        _handle_offset_labels(ax, offsetlabelsize or labelsize)
        
    except Exception as e:
        warnings.warn(f"Error formatting axis ticks: {str(e)}")


def _format_x_axis(
    ax: Axes,
    major_length: int,
    minor_length: int,
    major_width: int,
    minor_width: int,
    direction: str,
    label_bothsides: bool,
    tick_bothsides: bool,
    labelsize: Optional[int],
    x_axis_styles: Optional[Dict[str, Any]],
    xtick_styles: Optional[Dict[str, Any]]
) -> None:
    """Helper function for formatting x-axis ticks."""
    if ax.get_xaxis().get_scale() != "log":
        ax.xaxis.set_minor_locator(AutoMinorLocator())
    
    x_styles = {
        "labelsize": labelsize,
        "labeltop": label_bothsides,
        "top": tick_bothsides,
        "bottom": True,
        "direction": direction,
    }

    x_axis_styles = mp.concat((x_axis_styles,), copy=True)
    if 'major_length' in x_axis_styles:
        major_length = x_axis_styles.pop('major_length')
    if 'minor_length' in x_axis_styles:
        minor_length = x_axis_styles.pop('minor_length')
    if 'major_width' in x_axis_styles:
        major_width = x_axis_styles.pop('major_width')
    if 'minor_width' in x_axis_styles:
        minor_width = x_axis_styles.pop('minor_width')
    
    if x_axis_styles:
        x_styles.update(x_axis_styles)
    
    ax.tick_params(
        axis="x",
        which="major",
        length=major_length,
        width=major_width,
        **x_styles
    )
    ax.tick_params(
        axis="x",
        which="minor",
        length=minor_length,
        width=minor_width,
        **x_styles
    )
    
    set_axis_tick_styles(ax.xaxis, xtick_styles)


def _format_y_axis(
    ax: Axes,
    major_length: int,
    minor_length: int,
    major_width: int,
    minor_width: int,
    direction: str,
    label_bothsides: bool,
    tick_bothsides: bool,
    labelsize: Optional[int],
    y_axis_styles: Optional[Dict[str, Any]],
    ytick_styles: Optional[Dict[str, Any]]
) -> None:
    """Helper function for formatting y-axis ticks."""
    if ax.get_yaxis().get_scale() != "log":
        ax.yaxis.set_minor_locator(AutoMinorLocator())
    
    y_styles = {
        "labelsize": labelsize,
        "labelleft": True,
        "left": True,
        "right": tick_bothsides,
        "direction": direction,
    }

    y_axis_styles = mp.concat((y_axis_styles,), copy=True)
    major_length = y_axis_styles.pop('major_length', major_length)
    minor_length = y_axis_styles.pop('minor_length', minor_length)
    major_width = y_axis_styles.pop('major_width', major_width)
    minor_width = y_axis_styles.pop('minor_width', minor_width)
    
    if y_axis_styles:
        y_styles.update(y_axis_styles)

    ax.tick_params(
        axis="y",
        which="major",
        length=major_length,
        width=major_width,
        **y_styles
    )
    ax.tick_params(
        axis="y",
        which="minor",
        length=minor_length,
        width=minor_width,
        **y_styles
    )
    
    set_axis_tick_styles(ax.yaxis, ytick_styles)


def _handle_offset_labels(ax: Axes, offsetlabelsize: Optional[int]) -> None:
    """Helper function for handling offset labels."""
    if offsetlabelsize is None:
        return
    
    for axis in (ax.xaxis, ax.yaxis):
        offset_text = axis.get_offset_text()
        if offset_text.get_text():
            offset_text.set_fontsize(offsetlabelsize)
            axis.labelpad += offset_text.get_fontsize()
    
    if (ax.xaxis.get_offset_text().get_text() or 
        ax.yaxis.get_offset_text().get_text()):
        if not isinstance(plt.gca(), plt.Subplot):
            plt.tight_layout()


def set_axis_tick_styles(axis: Axis, styles: Optional[Dict[str, Any]] = None) -> None:
    """
    Set advanced tick styles for an axis.
    
    Parameters
    ----------
    axis : matplotlib.axis.Axis
        The axis to style
    styles : Optional[Dict[str, Any]]
        Style specifications
    """
    if not styles:
        return
    
    try:
        _set_axis_formatter(axis, styles.get("format"))
        if axis.get_scale() != "log":
            _set_axis_locator(axis, styles)
    except Exception as e:
        raise StyleError(f"Failed to apply axis styles: {str(e)}")


def _set_axis_formatter(
    axis: Axis, 
    fmt: Optional[Union[str, Formatter]]
) -> None:
    """Helper function to set axis formatter."""
    if fmt is None:
        return
    
    if isinstance(fmt, str):
        if fmt == "numeric":
            formatter = (
                LogNumericFormatter()
                if axis.get_scale() == "log"
                else NumericFormatter()
            )
        else:
            raise ValueError(f"Unsupported format string: '{fmt}'")
    elif isinstance(fmt, Formatter):
        formatter = fmt
    else:
        raise ValueError(f"Invalid formatter type: {type(fmt)}")
    
    axis.set_major_formatter(formatter)


def _set_axis_locator(axis: Axis, styles: Dict[str, Any]) -> None:
    """Helper function to set axis locator."""
    locator_type = styles.get("locator", "").lower()
    if not locator_type:
        return
    
    new_locator_class = AXIS_LOCATOR_MAP.get(locator_type)
    if not new_locator_class:
        raise ValueError(f"Unknown locator type: {locator_type}")
    
    new_locator = new_locator_class()
    
    locator_params = {
        param: styles[param]
        for param in getattr(new_locator, "default_params", [])
        if param in styles
    }
    
    if locator_params:
        new_locator.set_params(**locator_params)
    
    axis.set_major_locator(new_locator)

def multirow_frame(
    nrows: int = 1,
    sharex: bool = True,
    logxs: Union[bool, List[bool]] = False,
    logys: Union[bool, List[bool]] = False,
    main_styles: Optional[Union[Dict[str, Any], str]] = None,
    main_prop_cycle: Optional[List[str]] = None,
    styles_map: Optional[Dict[str, Union[Dict[str, Any], str]]] = None,
    prop_cycle_map: Optional[Dict[str, List[str]]] = None,
    analysis_label_options: Optional[Union[Dict[str, Any], str]] = None,
    figure_index: Optional[int] = None
) -> Tuple[Figure, Any]:
    """
    Create a figure with multi-row frame.
    
    Parameters
    ----------
    nrows: int, default = 1
        Number of rows (axes) in the figure frame.
    sharex: bool, default = True
        Share the x-axis for all rows.
    logxs : bool or list of bool, default = False
        Use logarithmic x-axis. Use list type for per-axis control.
    logy : bool or list of bool, default = False
        Use logarithmic y-axis.  Use list type for per-axis control.
    main_styles : Optional[Union[Dict[str, Any], str]]
        Main plot styles inherited by all frames.
    main_prop_cycle : Optional[List[str]]
        Main color cycle inherited by all frames.
    styles_map : Optional[Dict[str, Union[Dict[str, Any], str]]]
        Plot styles for individual frames. Axis specified by index in the form "axis_{index}"
    prop_cycle_map: Optional[Dict[str, List[str]]]
        Color cycle for individual frames. Axis specified by index in the form "axis_{index}"
    analysis_label_options : Optional[Union[Dict[str, Any], str]]
        Options for drawing analysis label
    figure_index : Optional[int]
        Figure number to use
    Returns
    -------
    Tuple[Figure, Array[Axes, ...]]
        Figure and the corresponding axes
    """
    if nrows <= 0:
        raise ValueError('`nrows` must be a positive integer')
        
    if figure_index is None:
        plt.clf()
    else:
        plt.figure(figure_index)
    
    main_styles = template_styles.parse(main_styles)
    styles_map = styles_map or {}
    prop_cycle_map = prop_cycle_map or {}

    gridspec_kw = main_styles.get('gridspec')
    figure_styles = main_styles.get('figure', {})
    figure, axes = plt.subplots(
        nrows=nrows,
        ncols=1,
        gridspec_kw=gridspec_kw,
        sharex=sharex,
        **figure_styles
    )

    if nrows == 1:
        axes = np.array([axes])

    def set_axes_logscale(
        axis_type: AxisType,
        logscales: Union[bool, List[bool]] = None
    ) -> None:
        if isinstance(logscales, bool):
            logscales = [logscales] * nrows
        logscale_str = 'logxs' if axis_type == AxisType.XAXIS else 'logys'
        if not is_indexable_sequence(logscales):
            raise TypeError(f'`{logscale_str}` must be an indexable sequence')
        func_str = 'set_xscale' if axis_type == AxisType.XAXIS else 'set_yscale'
        for axis, logscale in zip(axes, logscales):
            if logscale:
                getattr(axis, func_str)("log")
    
    set_axes_logscale(AxisType.XAXIS, logxs)
    set_axes_logscale(AxisType.YAXIS, logys)

    for index, axis in enumerate(axes):
        domain = AXES_DOMAIN_FMT.format(index=index)
        domain_styles = styles_map.get(domain, {})
        ax_styles = mp.concat((main_styles.get("axis"), domain_styles.get("axis")), copy=True)
        xtick_styles = mp.concat((main_styles.get("xtick"), domain_styles.get("xtick")), copy=True)
        ytick_styles = mp.concat((main_styles.get("ytick"), domain_styles.get("ytick")), copy=True)
        if (index != nrows - 1) and sharex:
            ax_styles.setdefault("x_axis_styles", {})
            ax_styles["x_axis_styles"].setdefault("labelbottom", False)
        format_axis_ticks(
            axis,
            x_axis=True,
            y_axis=True,
            xtick_styles=xtick_styles,
            ytick_styles=ytick_styles,
            **ax_styles
        )
        domain_prop_cycle = prop_cycle_map.get(domain, main_prop_cycle)
        if domain_prop_cycle is not None:
            axis.set_prop_cycle(domain_prop_cycle)

    if analysis_label_options is not None:
        draw_analysis_label(
            axes[0],
            text_options=main_styles.get("text"),
            **analysis_label_options
        )

    if nrows == 1:
        return figure, axes[0]
    return figure, axes

def single_frame(
    logx: bool = False,
    logy: bool = False,
    styles: Optional[Union[Dict[str, Any], str]] = None,
    analysis_label_options: Optional[Union[Dict[str, Any], str]] = None,
    prop_cycle: Optional[List[str]] = None,
    figure_index: Optional[int] = None,
) -> Tuple[Figure, Axes]:
    """
    Create a single plot frame with enhanced options.
    
    Parameters
    ----------
    logx : bool
        Use logarithmic x-axis
    logy : bool
        Use logarithmic y-axis
    styles : Optional[Union[Dict[str, Any], str]]
        Plot styles
    analysis_label_options : Optional[Union[Dict[str, Any], str]]
        Options for analysis label
    prop_cycle : Optional[List[str]]
        Color cycle
    figure_index : Optional[int]
        Figure number to use
        
    Returns
    -------
    Tuple[Figure, Axes]:
        The figure and axis created.
    """

    return multirow_frame(
        nrows=1,
        logxs=logx,
        logys=logy,
        main_styles=styles,
        main_prop_cycle=prop_cycle,
        analysis_label_options=analysis_label_options,
        figure_index=figure_index
    )

def ratio_frame(
    logx: bool = False,
    logy: bool = False,
    logy_lower: Optional[bool] = None,
    styles: Optional[Union[Dict[str, Any], str]] = None,
    styles_lower: Optional[Union[Dict[str, Any], str]] = None,
    analysis_label_options: Optional[Union[Dict[str, Any], str]] = None,
    prop_cycle: Optional[List[str]] = None,
    prop_cycle_lower: Optional[List[str]] = None,
    figure_index: Optional[int] = None,
) -> Tuple[Axes, Any]:
    """
    Create a ratio plot frame with shared x-axis.
    
    Parameters
    ----------
    logx : bool
        Use logarithmic x-axis
    logy : bool
        Use logarithmic y-axis for main plot
    logy_lower : Optional[bool]
        Use logarithmic y-axis for ratio plot
    styles : Optional[Union[Dict[str, Any], str]]
        Plot styles
    styles : Optional[Union[Dict[str, Any], str]]
        Plot styles for the ratio plot
    analysis_label_options : Optional[Union[Dict[str, Any], str]]
        Options for analysis label
    prop_cycle : Optional[List[str]]
        Color cycle for main plot
    prop_cycle_lower : Optional[List[str]]
        Color cycle for ratio plot
    figure_index : Optional[int]
        Figure number to use
        
    Returns
    -------
    Tuple[Axes, Axes]
        Main plot axes and ratio plot axes
    """
    if logy_lower is None:
        logy_lower = logy
    logys = (logy, logy_lower)
    ratio_axis_domain = AXES_DOMAIN_FMT.format(index=1)
    if styles_lower is not None:
        styles_map = {
            ratio_axis_domain: styles_lower
        }
    else:
        styles_map = None
    if prop_cycle_lower is not None:
        prop_cycle_map = {
            ratio_axis_domain: prop_cycle_lower
        }
    else:
        prop_cycle_map = None
    styles = mp.concat((styles, {"gridspec": styles.get("ratio_frame", {})}))
    return multirow_frame(
        nrows=2,
        sharex=True,
        logxs=logx,
        logys=logys,
        main_styles=styles,
        main_prop_cycle=prop_cycle,
        styles_map=styles_map,
        prop_cycle_map=prop_cycle_map,
        analysis_label_options=analysis_label_options,
        figure_index=figure_index
    )

@dataclass
class AnalysisLabelConfig:
    """Configuration for analysis labels."""
    loc: Tuple[float, float] = (0.05, 0.95)
    fontsize: float = 25
    status: Union[str, ResultStatus] = "int"
    energy: Optional[str] = None
    lumi: Optional[str] = None
    colab: Optional[str] = "ATLAS"
    main_text: Optional[str] = None
    extra_text: Optional[str] = None
    dy: float = 0.02
    dy_main: float = 0.01
    transform_x: TransformType = "axis"
    transform_y: TransformType = "axis"
    vertical_align: str = "top"
    horizontal_align: str = "left"
    text_options: Optional[Dict[str, Any]] = None


def draw_analysis_label(
    axis: Axes,
    **kwargs: Any
) -> None:
    """
    Draw analysis label with comprehensive options.
    
    Parameters
    ----------
    axis : matplotlib.axes.Axes
        The axes to draw on
    **kwargs : Any
        Configuration options (see AnalysisLabelConfig)
    """
    config = AnalysisLabelConfig(**kwargs)
    
    try:
        status_text = ResultStatus.parse(config.status).display_text
    except (ValueError, AttributeError):
        status_text = str(config.status)

    with change_axis(axis):
        x_pos, y_pos = config.loc
        
        # Draw main texts
        y_pos = _draw_main_texts(
            axis,
            x_pos,
            y_pos,
            config.main_text,
            config.colab,
            status_text,
            config
        )
        
        # Draw additional texts
        _draw_additional_texts(
            axis,
            x_pos,
            y_pos,
            config.energy,
            config.lumi,
            config.extra_text,
            config
        )


def _draw_main_texts(
    axis: Axes,
    x_pos: float,
    y_pos: float,
    main_text: Optional[str],
    colab: Optional[str],
    status_text: str,
    config: AnalysisLabelConfig
) -> float:
    """Helper function to draw main texts of analysis label."""
    main_texts = []
    
    if main_text:
        main_texts.extend(main_text.split("//"))
    
    if colab:
        colab_text = r"\bolditalic{" + colab + "}  " + status_text
        main_texts.append(colab_text)

    current_y = y_pos
    for text in main_texts:
        _, _, current_y, _ = draw_text(
            axis,
            x_pos,
            current_y,
            text,
            fontsize=config.fontsize,
            transform_x=config.transform_x,
            transform_y=config.transform_y,
            horizontalalignment=config.horizontal_align,
            verticalalignment=config.vertical_align
        )
        current_y -= config.dy_main
    
    return current_y

def _draw_additional_texts(
    axis: Axes,
    x_pos: float,
    y_pos: float,
    energy: Optional[str],
    lumi: Optional[str],
    extra_text: Optional[str],
    config: AnalysisLabelConfig
) -> None:
    """Helper function to draw additional texts of analysis label."""
    texts = []
    
    # Combine energy and luminosity
    elumi_parts = []
    if energy:
        elumi_parts.append(r"$\sqrt{s} = $" + energy)
    if lumi:
        elumi_parts.append(lumi)
    
    if elumi_parts:
        texts.append(", ".join(elumi_parts))
    
    # Add extra text
    if extra_text:
        texts.extend(extra_text.split("//"))
    
    # Draw all texts
    text_options = config.text_options or {}
    current_y = y_pos
    
    for text in texts:
        _, _, current_y, _ = draw_text(
            axis,
            x_pos,
            current_y - config.dy,
            text,
            **text_options
        )
        current_y -= config.dy


def draw_text(
    axis: Axes,
    x: float,
    y: float,
    text_str: str,
    transform_x: TransformType = "axis",
    transform_y: TransformType = "axis",
    **styles: Any
) -> Tuple[float, float, float, float]:
    """
    Draw formatted text with special styles.
    
    Parameters
    ----------
    axis : matplotlib.axes.Axes
        The axes to draw on
    x : float
        X-coordinate
    y : float
        Y-coordinate
    text_str : str
        Text to draw
    transform_x : TransformType
        X-coordinate transform
    transform_y : TransformType
        Y-coordinate transform
    **styles : Any
        Additional text styles
        
    Returns
    -------
    Tuple[float, float, float, float]
        Text dimensions (xmin, xmax, ymin, ymax)
    """
    with change_axis(axis):
        transform = create_transform(transform_x, transform_y)
        components = SPECIAL_TEXT_REGEX.split(text_str)
        current_x = x
        xmin = None
        ymin = y
        ymax = y
        
        for component in components:
            if not component:
                continue

            text = None
            if SPECIAL_TEXT_REGEX.match(component):
                for pattern, font_styles in SPECIAL_TEXT_PATTERNS.items():
                    match = re.match(pattern, component)
                    if match:
                        text = axis.text(
                            current_x,
                            y,
                            match.group(1),
                            transform=transform,
                            **styles,
                            **font_styles
                        )
                        break
            else:
                text = axis.text(
                    current_x,
                    y,
                    component,
                    transform=transform,
                    **styles
                )

            if text is not None:
                xmin_, current_x, ymin, ymax = get_artist_dimension(text)
            if xmin is None:
                xmin = xmin_
        
        return xmin, current_x, ymin, ymax


def draw_multiline_text(
    axis: Axes,
    x: float,
    y: float,
    text: str,
    dy: float = 0.01,
    transform_x: TransformType = "axis",
    transform_y: TransformType = "axis",
    **styles: Any
) -> None:
    """Draw multi-line text with special formatting."""

    current_y = y
    lines = re.split("//|\n", text)
    for line in lines:
        _, _, current_y, _ = draw_text(
            axis,
            x,
            current_y,
            line.strip(),
            transform_x=transform_x,
            transform_y=transform_y,
            **styles
        )
        current_y -= dy
        transform_x = transform_y = "axis"


def centralize_axis(
    ax: Axes,
    which: Literal["x", "y"] = "y",
    ref_value: float = 0,
    padding: float = 0.1
) -> None:
    """
    Centralize an axis around a reference value with padding.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to modify
    which : Literal["x", "y"]
        Which axis to centralize
    ref_value : float
        Reference value to center around
    padding : float
        Padding fraction
    """
    if which not in {"x", "y"}:
        raise ValueError('Axis must be either "x" or "y"')
    
    get_scale = ax.get_xscale if which == "x" else ax.get_yscale
    get_lim = ax.get_xlim if which == "x" else ax.get_ylim
    set_lim = ax.set_xlim if which == "x" else ax.set_ylim
    
    if get_scale() == "log":
        raise ValueError("Cannot centralize logarithmic axis")
    
    if not (0 <= padding < 1):
        raise ValueError("Padding must be between 0 and 1")
    
    lim = get_lim()
    delta = max(abs(ref_value - lim[0]), abs(lim[1] - ref_value))
    pad = (lim[1] - lim[0]) * padding if padding else 0.0
    new_lim = (ref_value - delta - pad, ref_value + delta + pad)
    set_lim(*new_lim)

def get_artist_dimension(
    artist: Artist, 
    transform: TransformType = 'axis'
) -> Tuple[float, float, float, float]:
    """
    Get dimensions of an artist's bounding box.
    
    Parameters
    ----------
    artist : matplotlib.artist.Artist
        The artist to measure
    transform : TransformType
        Coordinate transform for dimensions
        
    Returns
    -------
    Tuple[float, float, float, float]
        Dimensions (xmin, xmax, ymin, ymax)
    """

    axis = artist.axes or plt.gca()
    artist.figure.canvas.draw()
    
    bbox = artist.get_window_extent()
    
    if transform is not None:
        transform_obj = parse_transform(transform, ax=axis)
        if transform_obj is not None:
            bbox = bbox.transformed(transform_obj.inverted())
    
    return bbox.xmin, bbox.xmax, bbox.ymin, bbox.ymax


def draw_hatches(
    axis: Axes,
    ymax: float,
    height: float = 1.0,
    **styles: Any
) -> None:
    """
    Draw hatched pattern on axis.
    
    Parameters
    ----------
    axis : matplotlib.axes.Axes
        The axes to draw on
    ymax : float
        Maximum y-value
    height : float
        Height of hatch pattern
    **styles : Any
        Additional style options
    """

    y_values = np.arange(0, height * ymax, 2 * height) - height / 2
    transform = create_transform(transform_x="axis", transform_y="data")
    
    for y in y_values:
        axis.add_patch(
            Rectangle(
                (0, y),
                1,
                1,
                transform=transform,
                zorder=-1,
                **styles
            )
        )


def is_transparent_color(color: Optional[ColorType]) -> bool:
    """
    Check if a color is transparent.
    
    Parameters
    ----------
    color : Optional[ColorType]
        Color to check
        
    Returns
    -------
    bool
        True if color is transparent
    """
    if color is None:
        raise ValueError("Color cannot be None")
    
    try:
        rgba = mcolors.to_rgba(color)
        return rgba[3] == 0
    except ValueError as e:
        raise ValueError(f"Invalid color format: {color}") from e


def get_artist_colors(
    artist: Artist,
    index: int = 0
) -> Dict[str, Optional[ColorType]]:
    """
    Get color properties of an artist.
    
    Parameters
    ----------
    artist : matplotlib.artist.Artist
        The artist to analyze
    index : int
        Index for collections
        
    Returns
    -------
    Dict[str, Optional[ColorType]]
        Color properties
    """
    
    colors: Dict[str, Optional[ColorType]] = {}
    
    if isinstance(artist, ErrorbarContainer):
        colors["color"] = artist[0].get_color()
        if artist.has_yerr:
            colors["ecolor"] = artist[2][0].get_color()
        elif artist.has_xerr:
            colors["ecolor"] = artist[1][0].get_color()
        return colors

    if isinstance(artist, Container):
        children = artist.get_children()
        if not children:
            raise IndexError("Artist has no children")
        if index >= len(children):
            raise IndexError("Index out of bounds")
        artist = children[index]
    
    if not isinstance(artist, Artist):
        raise TypeError("Invalid artist type")
    
    if isinstance(artist, Collection):
        facecolors = artist.get_facecolor()
        edgecolors = artist.get_edgecolor()
        colors["facecolor"] = (
            facecolors[index] if len(facecolors) > index else None
        )
        colors["edgecolor"] = (
            edgecolors[index] if len(edgecolors) > index else None
        )
        if hasattr(artist, 'get_color'):
            colors_ = artist.get_color()
            colors["color"] = (
                colors_[index] if len(colors_) > index else None
            )
    elif isinstance(artist, Line2D):
        colors.update({
            "color": artist.get_color(),
            "markerfacecolor": artist.get_markerfacecolor(),
            "markeredgecolor": artist.get_markeredgecolor()
        })
    
    elif isinstance(artist, Patch):
        colors.update({
            "facecolor": artist.get_facecolor(),
            "edgecolor": artist.get_edgecolor()
        })
    
    elif isinstance(artist, AxesImage):
        colors["cmap"] = artist.get_cmap()
    
    elif isinstance(artist, Text):
        colors["textcolor"] = artist.get_color()
    
    return colors


def convert_size(size_str: str) -> float:
    """
    Convert size string to float value.
    
    Parameters
    ----------
    size_str : str
        Size string (e.g., "50%", "0.5")
        
    Returns
    -------
    float
        Converted size value
    """
    try:
        if size_str.endswith('%'):
            return float(size_str.strip('%')) / 100
        return float(size_str)
    except ValueError as e:
        raise ValueError(f"Invalid size format: {size_str}") from e

def is_edgy_polygon(handle: Polygon) -> bool:
    """
    Check if a legend handle represents a polygon with only edges and no fill.
    
    Parameters
    ----------
    handle : matplotlib.patches.Polygon
        The legend handle to be checked
        
    Returns
    -------
    bool
        True if the handle is an edgy polygon (only edges, no fill)
    """
    if not isinstance(handle, Polygon):
        return False
    
    edgecolor = handle.get_edgecolor()
    if np.all(edgecolor == 0):
        return False
    
    return not handle.get_fill()

def is_valid_label(label: Optional[str]):
    return label and not label.startswith('_')
    
def resolve_handle_label(
    handle: Any
) -> Tuple[Any, str]:
    """
    Resolve the artist handle and label for the legend.
    
    Parameters
    ----------
    handle : Any
        The artist handle
        
    Returns
    -------
    Tuple[Any, str]
        The resolved handle and its label
    """

    label = None
    if hasattr(handle, 'get_label'):
        label = handle.get_label()
    elif isinstance(handle, (list, tuple)):
        for handle_i in handle:
            _, label = resolve_handle_label(handle_i)
            if is_valid_label(label):
                break
    if not label:
        return handle, '_nolengend_'
    return handle, label

def remake_handles(
    handles: List[Any],
    polygon_to_line: bool = True,
    fill_border: bool = True,
    line2d_styles: Optional[Dict[str, Any]] = None,
    border_styles: Optional[Dict[str, Any]] = None,
) -> List[Any]:
    """
    Remake legend handles for better representation.
    
    Parameters
    ----------
    handles : List[Any]
        List of artist handles
    polygon_to_line : bool
        Convert polygon edges to lines in the legend
    fill_border : bool
        Add a border to filled patches in the legend
    line2d_styles : Optional[Dict[str, Any]]
        Styles for Line2D objects
    border_styles : Optional[Dict[str, Any]]
        Styles for border rectangles
        
    Returns
    -------
    List[Any]
        List of remade artist handles
    """

    new_handles = []
    for handle in handles:
        subhandles = handle if isinstance(handle, (list, tuple)) else [handle]
        new_subhandles = []
        for subhandle in subhandles:
            if polygon_to_line and is_edgy_polygon(subhandle):
                line_styles = line2d_styles or {}
                subhandle = Line2D(
                    [],
                    [],
                    color=subhandle.get_edgecolor(),
                    linestyle=subhandle.get_linestyle(),
                    label=subhandle.get_label(),
                    **line_styles
                )
            new_subhandles.append(subhandle)
            if fill_border and isinstance(subhandle, (PolyCollection, BarContainer)):
                border_style = border_styles or {}
                border_handle = Rectangle(
                    (0, 0),
                    1,
                    1,
                    facecolor="none",
                    **border_style
                )
                new_subhandles.append(border_handle)
        
        if isinstance(handle, Container):
            kwargs = {"label": handle.get_label()}
            if isinstance(handle, ErrorbarContainer):
                kwargs.update({
                    "has_xerr": handle.has_xerr,
                    "has_yerr": handle.has_yerr
                })
            new_handle = type(handle)(tuple(new_subhandles), **kwargs)
        else:
            new_handle = (
                new_subhandles[0] 
                if len(new_subhandles) == 1 
                else tuple(new_subhandles)
            )
        new_handles.append(new_handle)
        
    return new_handles


def isolate_contour_styles(
    styles: Dict[str, Any]
) -> Iterator[Dict[str, Any]]:
    """
    Convert contour or contourf keyword arguments to a list of styles for each level.
    
    Parameters
    ----------
    styles : Dict[str, Any]
        Dictionary of keyword arguments passed to contour or contourf
        
    Returns
    -------
    Iterator[Dict[str, Any]]
        Iterator of style dictionaries, one per contour level
        
    Raises
    ------
    ValueError
        If style sequences have inconsistent lengths
    """

    # Map input style names to matplotlib properties
    style_key_map = {
        "linestyles": "linestyle",
        "linewidths": "linewidth",
        "colors": "color",
        "alpha": "alpha",
    }
    
    # Extract relevant styles
    relevant_styles = {
        new_name: styles[old_name]
        for old_name, new_name in style_key_map.items()
        if old_name in styles
    }
    
    # Determine sizes
    sizes = []
    for style_value in relevant_styles.values():
        if isinstance(style_value, Sequence) and not isinstance(style_value, str):
            sizes.append(len(style_value))
        else:
            sizes.append(1)
    
    if not sizes:
        return repeat({})
    
    # Check for consistent sizes
    unique_sizes = np.unique([size for size in sizes if size != 1])
    if len(unique_sizes) > 1:
        raise ValueError("Contour styles have inconsistent sizes")
    
    # Get maximum size
    max_size = max(sizes)
    
    # Handle scalar case
    if max_size == 1:
        return repeat(relevant_styles)
    
    # Create style dictionaries for each level
    list_styles = []
    for i in range(max_size):
        level_styles = {
            key: value if sizes[idx] == 1 else value[i]
            for idx, (key, value) in enumerate(relevant_styles.items())
        }
        list_styles.append(level_styles)
    
    return list_styles
    
def get_axis_limits(
    ax: Axes,
    xmin: Optional[float] = None,
    xmax: Optional[float] = None,
    ymin: Optional[float] = None,
    ymax: Optional[float] = None,
    xpadlo: Optional[float] = None,
    xpadhi: Optional[float] = None,
    xpad: Optional[Union[float, Tuple[float, float], List[float]]] = None,
    ypadlo: Optional[float] = None,
    ypadhi: Optional[float] = None,
    ypad: Optional[Union[float, Tuple[float, float], List[float]]] = None,
) -> Tuple[List[float], List[float]]:
    """
    Calculate new axis limits with optional padding.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to calculate limits for.
    xmin, xmax : Optional[float]
        X-axis limits.
    ymin, ymax : Optional[float]
        Y-axis limits.
    xpadlo : Optional[float]
        Lower x-padding fraction.
    xpadhi : Optional[float]
        Upper x-padding fraction.
    xpad : Optional[float or sequence of two floats]
        Symmetric x-padding fraction (if scalar) or a two-element sequence
        representing (lower, upper) x-padding. In the latter case, xpadlo and
        xpadhi must be None.
    ypadlo : Optional[float]
        Lower y-padding fraction.
    ypadhi : Optional[float]
        Upper y-padding fraction.
    ypad : Optional[float or sequence of two floats]
        Symmetric y-padding fraction (if scalar) or a two-element sequence
        representing (lower, upper) y-padding. In the latter case, ypadlo and
        ypadhi must be None.

    Returns
    -------
    Tuple[List[float], List[float]]
        New x and y limits.

    Raises
    ------
    ValueError
        If invalid padding values are provided.
    """
    # Start with current limits
    xlim = list(ax.get_xlim())
    ylim = list(ax.get_ylim())

    # ----- Process x-axis padding -----
    if xpad is not None:
        if isinstance(xpad, (list, tuple)):
            if len(xpad) != 2:
                raise ValueError("'xpad' must be a scalar or a sequence of length 2.")
            if xpadlo is not None or xpadhi is not None:
                raise ValueError("When 'xpad' is given as a sequence, 'xpadlo' and 'xpadhi' must be None.")
            xpadlo, xpadhi = xpad[0], xpad[1]
        else:
            if xpadhi is not None:
                raise ValueError("Cannot set both 'xpad' and 'xpadhi'.")
            xpadhi = xpad

    if xpadlo is not None or xpadhi is not None:
        xpad_lo = xpadlo or 0
        xpad_hi = xpadhi or 0

        if not (0 <= xpad_lo <= 1):
            raise ValueError("'xpadlo' must be between 0 and 1")
        if not (0 <= xpad_hi <= 1):
            raise ValueError("'xpadhi' must be between 0 and 1")

        # Handle logarithmic scale for x-axis
        if ax.get_xaxis().get_scale() == "log":
            if xlim[0] <= 0:
                raise ValueError("X minimum must be positive in log scale")
            new_xmin = xlim[1] / (xlim[1] / xlim[0]) ** (1 + xpad_lo)
            new_xmax = xlim[0] * (xlim[1] / xlim[0]) ** (1 + xpad_hi)
        else:
            # Linear scale: compute the range and then add padding.
            x_range = xlim[1] - xlim[0]
            new_xmin = xlim[0] - x_range * xpad_lo / (1 - xpad_lo - xpad_hi)
            new_xmax = xlim[1] + x_range * xpad_hi / (1 - xpad_lo - xpad_hi)

        # Apply the computed padding if nonzero.
        if xpad_lo:
            xlim[0] = new_xmin
        if xpad_hi:
            xlim[1] = new_xmax

    # ----- Process y-axis padding -----
    if ypad is not None:
        if isinstance(ypad, (list, tuple)):
            if len(ypad) != 2:
                raise ValueError("'ypad' must be a scalar or a sequence of length 2.")
            if ypadlo is not None or ypadhi is not None:
                raise ValueError("When 'ypad' is given as a sequence, 'ypadlo' and 'ypadhi' must be None.")
            ypadlo, ypadhi = ypad[0], ypad[1]
        else:
            if ypadhi is not None:
                raise ValueError("Cannot set both 'ypad' and 'ypadhi'.")
            ypadhi = ypad

    if ypadlo is not None or ypadhi is not None:
        ypad_lo = ypadlo or 0
        ypad_hi = ypadhi or 0

        if not (0 <= ypad_lo <= 1):
            raise ValueError("'ypadlo' must be between 0 and 1")
        if not (0 <= ypad_hi <= 1):
            raise ValueError("'ypadhi' must be between 0 and 1")

        # Handle logarithmic scale for y-axis
        if ax.get_yaxis().get_scale() == "log":
            if ylim[0] <= 0:
                raise ValueError("Y minimum must be positive in log scale")
            new_ymin = ylim[1] / (ylim[1] / ylim[0]) ** (1 + ypad_lo)
            new_ymax = ylim[0] * (ylim[1] / ylim[0]) ** (1 + ypad_hi)
        else:
            y_range = ylim[1] - ylim[0]
            new_ymin = ylim[0] - y_range * ypad_lo / (1 - ypad_lo - ypad_hi)
            new_ymax = ylim[1] + y_range * ypad_hi / (1 - ypad_lo - ypad_hi)

        if ypad_lo:
            ylim[0] = new_ymin
        if ypad_hi:
            ylim[1] = new_ymax

    # Finally, if explicit limits were provided, override the padded values.
    if xmin is not None:
        xlim[0] = xmin
    if xmax is not None:
        xlim[1] = xmax
    if ymin is not None:
        ylim[0] = ymin
    if ymax is not None:
        ylim[1] = ymax

    return xlim, ylim

def contour_to_shapes(
    contour: "QuadContourSet",
    alpha:float = 0.1
):
    from quickstats.core.modules import require_module
    require_module("alphashape")
    from alphashape import alphashape
    shapes = []
    for path in contour.get_paths():
        shape = alphashape(path.vertices, alpha)
        shapes.append(shape)
    return shapes

def ellipse_to_shape(
    ellipse_patch: "Ellipse",
    num_points: int = 1000
):
    from quickstats.core.modules import require_module
    require_module("shapely")
    from shapely.geometry import Polygon
    
    t = np.linspace(0, 2 * np.pi, num_points)
    
    # Ellipse parameters
    width, height = ellipse_patch.width, ellipse_patch.height
    angle_rad = np.deg2rad(ellipse_patch.angle)
    cx, cy = ellipse_patch.center
    
    # Parametric equation of ellipse before rotation
    x = (width / 2) * np.cos(t)
    y = (height / 2) * np.sin(t)
    
    # Rotation matrix
    R = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad),  np.cos(angle_rad)]
    ])
    
    # Apply rotation and translation
    points = np.column_stack((x, y)) @ R.T + np.array([cx, cy])

    return Polygon(points)