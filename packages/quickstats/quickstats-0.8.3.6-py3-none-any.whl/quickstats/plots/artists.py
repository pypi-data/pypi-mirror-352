from typing import Optional, Union, Any, Dict, Tuple, Callable

from matplotlib.patches import Ellipse as Ellipse_mpl

from quickstats.core import mappings as mp
from quickstats.core.decorators import dataclass_ex
from quickstats.core.typing import ArrayLike
from .template import (
    TransformType,
    draw_multiline_text
)

StylesType = Dict[str, Any]
StylesMapType = Dict[str, StylesType]

def select_styles(
    styles_map: Optional[StylesMapType],
    keys: Union[str, Tuple[str, ...]]
) -> Tuple[Optional[StylesType], ...]:
    if styles_map is None:
        return (None,)
    if not keys:
        raise ValueError('Failed to selecte styles: no keys given')
    if isinstance(keys, str):
        keys = [keys]
    return (styles_map.get(key) for key in keys)

@dataclass_ex(kw_only=True)
class LazyArtist:

    label: Optional[str] = None

    def merge_styles(
        self,
        *components
    ) -> StylesType:
        styles = mp.concat(components, copy=True)
        if self.label:
            styles.setdefault('label', self.label)
        return styles
        
    def draw(
        self,
        ax,
        base_styles_map: Optional[StylesMapType]
    ):
        raise NotImplementedError

@dataclass_ex(kw_only=True)
class SingleArtist(LazyArtist):

    styles: Optional[StylesType] = None

    def resolve_styles(
        self,
        base_styles_map: Optional[StylesMapType],
        keys: Union[str, Tuple[str, ...]]
    ) -> Dict[str, Any]:
        base_components = select_styles(base_styles_map, keys)
        return self.merge_styles(*base_components, self.styles)

@dataclass_ex(kw_only=True)
class MixedArtist(LazyArtist):
    
    styles_map: Optional[StylesMapType] = None

    def resolve_styles(
        self,
        base_styles_map: Optional[StylesMapType],
        keys: Union[str, Tuple[str, ...]]
    ) -> Dict[str, Any]:
        base_components = select_styles(base_styles_map, keys)
        custom_components = select_styles(self.styles_map, keys)
        return self.merge_styles(*base_components, *custom_components)

@dataclass_ex(kw_only=True)
class Point(SingleArtist):
    """Data structure for plot points."""
    
    x: float
    y: float

    label: Optional[str] = None
    styles: Optional[StylesType] = None

    def draw(
        self,
        ax,
        base_styles_map: Optional[StylesMapType] = None
    ):
        styles = self.resolve_styles(base_styles_map, keys=('plot', 'point'))
        handle = ax.plot(
            self.x,
            self.y,
            **styles
        )[0]
        return handle

@dataclass_ex(kw_only=True)
class VLine(SingleArtist):
    
    x: float
    ymin: float
    ymax: float

    def draw(
        self,
        ax,
        base_styles_map: Optional[StylesMapType] = None
    ):
        styles = self.resolve_styles(base_styles_map, keys=('line', 'vline'))
        handle = ax.axvline(
            self.x,
            self.ymin,
            self.ymax,
            **styles
        )
        return handle

@dataclass_ex(kw_only=True)
class HLine(SingleArtist):
    
    y: float
    xmin: float
    xmax: float

    def draw(
        self,
        ax,
        base_styles_map: Optional[StylesMapType] = None
    ):
        styles = self.resolve_styles(base_styles_map, keys=('line', 'hline'))
        handle = ax.axhline(
            self.y,
            self.xmin,
            self.xmax,
            **styles
        )
        return handle

@dataclass_ex(kw_only=True)
class FillBetween(SingleArtist):
    
    x: ArrayLike
    y1: ArrayLike
    y2: ArrayLike

    def draw(
        self,
        ax,
        base_styles_map: Optional[StylesMapType] = None
    ):
        styles = self.resolve_styles(base_styles_map, keys='fill_between')
        handle = ax.fill_between(
            self.x,
            self.y1,
            self.y2,
            **styles
        )
        return handle

@dataclass_ex(kw_only=True)
class Ellipse(SingleArtist):
    
    xy: Tuple[float, float]
    width: float
    height: float
    angle: float

    def draw(
        self,
        ax,
        base_styles_map: Optional[StylesMapType] = None
    ):
        styles = self.resolve_styles(base_styles_map, keys='ellipse')
        handle = Ellipse_mpl(
            xy=self.xy,
            width=self.width,
            height=self.height,
            angle=self.angle,
            **styles
        )
        ax.add_patch(handle)
        return handle

@dataclass_ex(kw_only=True)
class ErrorBand(MixedArtist):

    x: ArrayLike
    y: ArrayLike
    yerrlo: Optional[ArrayLike] = None
    yerrhi: Optional[ArrayLike] = None
    xerr: Optional[ArrayLike] = None

    def draw(
        self,
        ax,
        base_styles_map: Optional[StylesMapType] = None
    ):
        plot_styles = self.resolve_styles(base_styles_map, keys='plot')
        fill_styles = self.resolve_styles(base_styles_map, keys='fill_between')
        handle_plot = ax.plot(
            self.x,
            self.y,
            **plot_styles
        )[0]
        
        if (self.yerrlo is None) and (self.yerrhi is None):
            return handle_plot
        xerr = self.xerr or self.x
        handle_fill = ax.fill_between(
            xerr,
            self.yerrlo,
            self.yerrhi,
            **fill_styles
        )
        handle = (handle_plot, handle_fill)
        return handle

@dataclass_ex(kw_only=True)
class Annotation(SingleArtist):
    """Data structure for plot annotations."""
    
    text: str
    xy: Tuple[float, float]

    def draw(
        self,
        ax,
        base_styles_map: Optional[StylesMapType] = None
    ):
        styles = self.resolve_styles(base_styles_map, keys='annotate')
        handle = ax.annotate(
            self.text,
            self.xy,
            **styles
        )
        # handle for annotation is not supported
        return None

@dataclass_ex(kw_only=True)
class Text(SingleArtist):
    """Data structure for plot texts."""
    
    text: str
    x: float
    y: float
    dy: float = 0.01
    transform_x: TransformType = "axis"
    transform_y: TransformType = "axis"

    def draw(
        self,
        ax,
        base_styles_map: Optional[StylesMapType] = None
    ):
        styles = self.resolve_styles(base_styles_map, keys='text')
        draw_multiline_text(
            axis=ax,
            x=self.x,
            y=self.y,
            text=self.text,
            dy=self.dy,
            transform_x=self.transform_x,
            transform_y=self.transform_y,
            **styles
        )
        return None