"""
Enhanced color utilities for matplotlib.

This module provides a comprehensive set of utilities for handling colors and colormaps
in matplotlib, including color validation, registration, and visualization tools.
"""

from typing import List, Dict, Optional, Union, Tuple, Any
import math

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import (
    to_rgba,
    get_named_colors_mapping,
    Colormap,
    ListedColormap,
    LinearSegmentedColormap,
)
from cycler import cycler

# Type aliases for better type checking
ColorType = Union[
    str,  # Named color, hex code, or grayscale
    Tuple[float, float, float],  # RGB tuple
    Tuple[float, float, float, float],  # RGBA tuple
]

ColormapType = Union[
    str,
    Colormap,
    List[ColorType],
]

# Custom exceptions for better error handling
class ColorError(Exception):
    """Base exception for color-related errors."""
    pass

class ColorValidationError(ColorError):
    """Exception raised for invalid color specifications."""
    pass

class ColormapError(ColorError):
    """Exception raised for colormap-related errors."""
    pass


def get_cmap(
    source: ColormapType,
    size: Optional[int] = None,
) -> Colormap:
    """
    Get a Matplotlib colormap from a name, list of colors, or an existing colormap.

    Parameters
    ----------
    source : ColormapType
        The source for the colormap. It can be:
        - A string name of the colormap.
        - A list of color specifications.
        - An existing Colormap instance.
    size : Optional[int], default None
        The number of entries in the colormap lookup table.
        If None, the original size is used.

    Returns
    -------
    Colormap
        A Matplotlib colormap.

    Raises
    ------
    ColormapError
        If source type is invalid or colormap creation fails.
    ValueError
        If size is negative.

    Examples
    --------
    >>> # Get a built-in colormap
    >>> cmap1 = get_cmap('viridis', size=10)
    
    >>> # Create from list of colors
    >>> colors = ['#FF0000', '#00FF00', '#0000FF']
    >>> cmap2 = get_cmap(colors, size=5)
    
    >>> # Use existing colormap
    >>> cmap3 = get_cmap(plt.cm.viridis, size=256)
    """
    try:
        # Validate size if provided
        if size is not None and size <= 0:
            raise ValueError("size must be positive")
            
        # Get colormap based on source type
        if isinstance(source, str):
            cmap = mpl.colormaps.get_cmap(source)
        elif isinstance(source, Colormap):
            cmap = source
        elif isinstance(source, list):
            # Validate all colors in the list
            for color in source:
                validate_color(color)
            cmap = ListedColormap(source)
        else:
            raise ColormapError(
                f"Invalid source type for colormap: {type(source)}. "
                "Expected string, Colormap, or list of colors."
            )
        
        # Resample if size is specified
        if size is not None:
            cmap = cmap.resampled(size)
            
        return cmap
        
    except (ValueError, TypeError) as e:
        raise ColormapError(f"Failed to create colormap: {str(e)}") from e


def get_cmap_rgba(
    source: ColormapType,
    size: Optional[int] = None,
) -> np.ndarray:
    """
    Retrieve the RGBA values from a colormap.

    Parameters
    ----------
    source : ColormapType
        The source for the colormap.
    size : Optional[int], default None
        The number of entries in the colormap lookup table.
        If None, the original size is used.

    Returns
    -------
    np.ndarray
        An array of RGBA values with shape (N, 4).

    Examples
    --------
    >>> # Get RGBA values from built-in colormap
    >>> rgba1 = get_cmap_rgba('viridis', size=10)
    >>> print(rgba1.shape)  # (10, 4)
    
    >>> # Get RGBA values from custom colors
    >>> colors = ['#FF0000', '#00FF00', '#0000FF']
    >>> rgba2 = get_cmap_rgba(colors, size=5)
    >>> print(rgba2.shape)  # (5, 4)
    """
    cmap = get_cmap(source, size=size)
    rgba_values = cmap(np.linspace(0, 1, cmap.N))
    return rgba_values


def get_rgba(
    color: ColorType,
    alpha: float = 1.0
) -> Tuple[float, float, float, float]:
    """
    Convert a color specification to an RGBA tuple with a specified alpha value.

    Parameters
    ----------
    color : ColorType
        A color specification (e.g., 'blue', '#00FF00', (1.0, 0.0, 0.0)).
    alpha : float, default 1.0
        The alpha (transparency) value, in range [0.0, 1.0].

    Returns
    -------
    Tuple[float, float, float, float]
        An RGBA tuple (R, G, B, A) with the specified alpha value.

    Raises
    ------
    ColorValidationError
        If color is invalid or alpha is out of range.

    Examples
    --------
    >>> get_rgba('blue', alpha=0.5)  # (0.0, 0.0, 1.0, 0.5)
    >>> get_rgba('#FF5733', alpha=0.8)  # (1.0, 0.341, 0.2, 0.8)
    >>> get_rgba((1.0, 0.0, 0.0))  # (1.0, 0.0, 0.0, 1.0)
    """
    try:
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between 0 and 1")
            
        rgba = to_rgba(color)
        return rgba[:3] + (alpha,)
        
    except ValueError as e:
        raise ColorValidationError(f"Invalid color or alpha value: {str(e)}") from e


def validate_color(color: ColorType) -> None:
    """
    Validate a color specification by attempting to convert it to RGBA.

    Parameters
    ----------
    color : ColorType
        The color specification to validate.

    Raises
    ------
    ColorValidationError
        If the color specification is invalid.

    Examples
    --------
    >>> validate_color('blue')  # OK
    >>> validate_color('#FF5733')  # OK
    >>> validate_color('not_a_color')  # Raises ColorValidationError
    """
    try:
        to_rgba(color)
    except ValueError as e:
        raise ColorValidationError(f"Invalid color value: {color}") from e


def register_colors(colors: Dict[str, Union[ColorType, Dict[str, ColorType]]]) -> None:
    """
    Register colors to Matplotlib's color registry.

    Parameters
    ----------
    colors : Dict[str, Union[ColorType, Dict[str, ColorType]]]
        A dictionary where keys are color labels and values are either:
        - Color specifications
        - Dictionaries mapping sub-labels to color specifications

    Raises
    ------
    ColorValidationError
        If any color specification is invalid.
    TypeError
        If the color values have invalid types.

    Examples
    --------
    >>> # Register simple colors
    >>> register_colors({
    ...     'primary': '#FF0000',
    ...     'secondary': '#00FF00'
    ... })
    
    >>> # Register color groups
    >>> register_colors({
    ...     'brand': {
    ...         'light': '#FFE4E1',
    ...         'main': '#FF4136',
    ...         'dark': '#85144B'
    ...     }
    ... })
    """
    try:
        grouped_colors = {}
        
        for label, color in colors.items():
            if isinstance(color, dict):
                for sublabel, subcolor in color.items():
                    validate_color(subcolor)
                    full_label = f"{label}:{sublabel}"
                    grouped_colors[full_label] = subcolor
            else:
                validate_color(color)
                grouped_colors[label] = color
        
        # Update the named colors mapping
        named_colors = get_named_colors_mapping()
        named_colors.update(grouped_colors)
        
    except (TypeError, AttributeError) as e:
        raise TypeError(
            "Colors must be color specifications or dictionaries of color specifications"
        ) from e


def register_cmaps(
    listed_colors: Dict[str, List[ColorType]],
    force: bool = True,
) -> None:
    """
    Register listed colormaps to the Matplotlib registry.

    Parameters
    ----------
    listed_colors : Dict[str, List[ColorType]]
        A dictionary mapping colormap names to lists of color specifications.
    force : bool, default True
        Whether to overwrite existing colormaps with the same name.

    Raises
    ------
    ColormapError
        If colormap creation fails.

    Examples
    --------
    >>> # Register simple sequential colormap
    >>> register_cmaps({
    ...     'red_to_blue': ['#FF0000', '#0000FF']
    ... })
    
    >>> # Register multiple colormaps
    >>> register_cmaps({
    ...     'sunset': ['#FF7E5F', '#FEB47B', '#FFE66D'],
    ...     'ocean': ['#1A2980', '#26D0CE']
    ... })
    """
    try:
        for name, colors in listed_colors.items():
            # Validate all colors before creating colormap
            for color in colors:
                validate_color(color)
                
            cmap = ListedColormap(colors, name=name)
            mpl.colormaps.register(cmap, name=name, force=force)
            
    except Exception as e:
        raise ColormapError(f"Failed to register colormaps: {str(e)}") from e

def get_color_brightness(r: float, g: float, b: float) -> float:
    """
    Returns a brightness measure (0.0 to 1.0) for an RGB color in [0, 1].
    
    This uses a weighted root-mean-square approach:
    
        brightness = sqrt(0.299*r^2 + 0.587*g^2 + 0.114*b^2)
    
    It roughly approximates how the human eye perceives brightness
    (placing more emphasis on green, less on blue, etc.).
    
    Args:
        r: Red component of the color (0.0 to 1.0).
        g: Green component of the color (0.0 to 1.0).
        b: Blue component of the color (0.0 to 1.0).
        
    Returns:
        A float representing the brightness, where 0.0 is darkest and 1.0 is brightest.
    """

    # Optionally, clamp the values if inputs might be out of [0,1]
    # r, g, b = sorted([0.0, r, 1.0])[1], sorted([0.0, g, 1.0])[1], sorted([0.0, b, 1.0])[1]

    return math.sqrt((0.299 * r * r) + (0.587 * g * g) + (0.114 * b * b))

def inverse_brightness_color(bg_brightness: float, min_contrast: float = 0.0) -> str:
    """
    Generates a grayscale color with inverse brightness to the input value.
    
    Creates a contrasting color: bright inputs produce dark outputs and vice versa.
    Useful for ensuring visibility of elements against varying background brightnesses.
    
    Args:
        bg_brightness: Input brightness value between 0.0 (black) and 1.0 (white)
        min_contrast: Minimum contrast offset (0.0-1.0) to enhance differentiation
                      Higher values push colors further from middle gray
    
    Returns:
        Hex color string (format: "#RRGGBB") representing the inverse brightness
    
    Examples:
        >>> inverse_brightness_color(0.9)  # High brightness input gets dark output
        '#191919'
        >>> inverse_brightness_color(0.1)  # Low brightness input gets light output
        '#E6E6E6'
    """
    # Ensure brightness is within valid range
    bg_brightness = max(0.0, min(1.0, bg_brightness))
    
    # Invert brightness for contrast
    inverted_brightness = 1.0 - bg_brightness
    
    # Apply minimum contrast if specified
    if min_contrast > 0:
        if inverted_brightness < 0.5:
            inverted_brightness = max(inverted_brightness - min_contrast, 0.0)
        else:
            inverted_brightness = min(inverted_brightness + min_contrast, 1.0)
    
    # Convert to 8-bit RGB value (0-255)
    rgb_value = int(round(inverted_brightness * 255))
    
    # Return hex color string
    return f"#{rgb_value:02X}{rgb_value:02X}{rgb_value:02X}"

def get_color_cycle(source: ColormapType) -> cycler:
    """
    Convert a color source to a Matplotlib cycler object.

    Parameters
    ----------
    source : ColormapType
        The source of colors. Can be:
        - A list of color specifications
        - A string name of a colormap
        - A Colormap instance

    Returns
    -------
    cycler
        A cycler object containing colors from the source.

    Examples
    --------
    >>> # Create from list of colors
    >>> cycle1 = get_color_cycle(['#FF0000', '#00FF00', '#0000FF'])
    >>> plt.rc('axes', prop_cycle=cycle1)
    
    >>> # Create from built-in colormap
    >>> cycle2 = get_color_cycle('viridis')
    >>> plt.rc('axes', prop_cycle=cycle2)
    """
    cmap = get_cmap(source)
    colors = cmap.colors if hasattr(cmap, "colors") else cmap(np.linspace(0, 1, cmap.N))
    return cycler(color=colors)


def plot_color_gradients(
    cmap_list: List[str],
    size: Optional[int] = None,
    figsize: Optional[Tuple[float, float]] = None,
) -> None:
    """
    Plot a series of color gradients for the given list of colormap names.

    Parameters
    ----------
    cmap_list : List[str]
        List of colormap names to visualize.
    size : Optional[int], default None
        The colormap will be resampled to have `size` entries.
    figsize : Optional[Tuple[float, float]], default None
        Custom figure size (width, height). If None, size is computed automatically.

    Examples
    --------
    >>> # Plot standard colormaps
    >>> plot_color_gradients(['viridis', 'plasma', 'inferno'])
    
    >>> # Plot custom sized gradients
    >>> plot_color_gradients(
    ...     ['Blues', 'Greens', 'Reds'],
    ...     size=128,
    ...     figsize=(8, 6)
    ... )
    """
    # Create gradient array
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    
    # Calculate figure dimensions
    nrows = len(cmap_list)
    if figsize is None:
        fig_height = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22
        figsize = (6.4, fig_height)
    
    # Create figure and subplots
    fig, axs = plt.subplots(nrows=nrows, figsize=figsize)
    if nrows == 1:
        axs = [axs]
    
    # Adjust layout
    fig.subplots_adjust(
        top=1 - 0.35 / figsize[1],
        bottom=0.15 / figsize[1],
        left=0.2,
        right=0.99,
        hspace=0.4,
    )
    
    # Plot each colormap
    for ax, name in zip(axs, cmap_list):
        cmap = get_cmap(name, size=size)
        ax.imshow(gradient, aspect="auto", cmap=cmap)
        ax.text(
            -0.01,
            0.5,
            name,
            va="center",
            ha="right",
            fontsize=10,
            transform=ax.transAxes,
        )
        ax.set_axis_off()