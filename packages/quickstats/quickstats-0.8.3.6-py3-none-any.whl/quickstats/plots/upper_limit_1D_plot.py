from typing import Optional, Union, Dict, List, Tuple, Any

import matplotlib.patches as patches
import matplotlib.lines as lines
import numpy as np
import pandas as pd

from quickstats import mappings as mp
from quickstats.core.typing import ArrayLike, Real
from quickstats.utils.string_utils import unique_string
from .abstract_plot import AbstractPlot
from .template import (
    create_transform,
    remake_handles
)
from .artists import (
    ErrorBand
)
from .colors import (
    ColorType
)

class UpperLimit1DPlot(AbstractPlot):

    STYLES = {
        'figure': {
            'figsize': (11.111, 10.333),
            'dpi': 72,
            'facecolor': "#FFFFFF"
        },
        'axis': {
            'tick_bothsides': False,
            'spine_width': 2,
            'y_axis_styles': {
                'minor_width': 0,
            }
        },
        'legend': {
            'fontsize': 22
        },
        'plot': {
            'linestyle': '-',
            'marker': 'none',
            'markersize': 10.
        },
        'hline': {
            'ls': '--',
            'lw': 1
        }
    }

    STYLES_MAP = {
        'expected': {
            'plot': {
                'linestyle': '--',
                'marker': 'none',
                'zorder': 1.1
            }
        },
        'observed': {
            'plot': {
                'linestyle': '-',
                'marker': 'o',
                'zorder': 1.1
            }
        },
        '1sigma': {
            'fill_between': {
                'alpha': 1,
                'zorder': 0.95
            }
        },
        '2sigma': {
            'fill_between': {
                'alpha': 1,
                'zorder': 0.9
            }
        },
        'header': {
            'text': {
                'fontsize': 22,
                'verticalalignment': 'center',
                'horizontalalignment': 'center'                
            }
        }
    }

    COLOR_MAP = {
        'artist.2sigma': 'hh:darkyellow',
        'artist.1sigma': 'hh:lightturquoise',
        'artist.expected': 'k',
        'artist.observed': 'k',
        'artist.hline': 'k',
    }

    LABEL_MAP = {
        'legend.2sigma': r'Expected limit $\pm 2\sigma$',
        'legend.1sigma': r'Expected limit $\pm 1\sigma$',
        'legend.expected': r'Expected limit (95% CL)',
        'legend.observed': r'Observed limit (95% CL)',
        'text.expected': 'Exp.',
        'text.observed': 'Obs.',
    }

    COLUMN_MAP = {
        'observed': 'obs',
        'expected': '0',
        '1sigma': ('-1', '1'),
        '2sigma': ('-2', '2')
    }

    CONFIG = {
        'top_margin': 2.2,
        'curve_line_styles': {
            'color': 'darkred'
        },
        'curve_fill_styles': {
            'color': 'hh:darkpink'
        },
        'box_legend_border': True
    }

    def __init__(
        self,
        df: pd.DataFrame,
        color_map: Optional[Dict[str, ColorType]] = None,
        label_map: Optional[Dict[str, str]] = None,
        column_map: Optional[Dict[str, str]] = None,
        styles: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        styles_map: Optional[Dict[str, Dict[str, Any]]] = None,
        analysis_label_options: Optional[Union[Dict, str]] = None
    ):       
        self.df = df
        self.column_map = mp.concat((self.COLUMN_MAP, column_map), copy=True)
        self._reference_limit_artists = []
        super().__init__(
            color_map=color_map,
            label_map=label_map,
            styles=styles,   
            config=config,
            styles_map=styles_map,
            analysis_label_options=analysis_label_options
        )

    def add_reference_limit(
        self,
        x: Real,
        xerrlo: Optional[Real] = None,
        xerrhi: Optional[Real] = None,
        label: Optional[str] = None,
        name: Optional[str] = None,
        plot_styles: Optional[Dict[str, Any]] = None,
        fill_styles: Optional[Dict[str, Any]] = None
    ) -> None:
        for key, value in [('x', x), ('xerrlo', xerrlo), ('xerrhi', xerrhi)]:
            if (value is not None) and (not isinstance(value, Real)):
                raise ValueError(f'`{key}` must be a real number (int or float).')
        if (xerrlo is None) and (xerrhi is None):
            xerr = None
            yerrlo = None
            yerrhi = None
        elif (xerrlo is not None) and (xerrhi is not None):
            xerr = [xerrlo, xerrhi]
            yerrlo = [0., 0.]
            yerrhi = [1., 1.]
        else:
            raise ValueError("Both 'xerrlo' and 'xerrhi' must be specified together, or both left as None.")
        artist = ErrorBand(
            x = [x, x],
            y = [0., 1.],
            xerr=xerr,
            yerrlo=yerrlo,
            yerrhi=yerrhi,
            label=label,
            styles_map={
                'plot': plot_styles,
                'fill_between': fill_styles
            }
        )
        name = name or label or f'_{unique_string()}'
        self.add_artist(artist, name=name)
        self._reference_limit_artists.append(name)

    def reset_artists(self) -> None:
        super().reset_artists()
        self._reference_limit_artists.clear()

    def reset_reference_limits(self) -> None:
        for name in self._reference_limit_artists:
            self._artists.pop(name, None)
        self._reference_limit_artists.clear()

    def _update_reference_limit_data(self, n_targets: int):
        for name in self._reference_limit_artists:
            artist = self._artists[name]
            artist.y = [0., float(n_targets)]
            if artist.yerrlo is not None:
                artist.yerrlo = [0., 0.]
            if artist.yerrhi is not None:
                artist.yerrhi = [n_targets, n_targets]            

    def resolve_targets(
        self,
        targets: Optional[List[str]]=None
    ) -> List[str]:
        if targets is None:
            return list(self.df.index)
        targets = list(targets)
        invalid_targets = list(set(targets) - set(self.df.index))
        if invalid_targets:
            raise RuntimeError(
                f'Target(s) not found: {", ".join(invalid_targets)}'
            )
        return targets

    def draw(
        self,
        targets: Optional[List[str]]=None,
        columns: Optional[Union[Tuple[str], List[str]]] = ('observed', 'expected', '1sigma', '2sigma'),
        value_columns: Optional[Union[Tuple[str], List[str]]] = ('observed', 'expected'),
        value_width:float = 0.15,
        value_fmt:str="{value:.2f}",
        line_indices:Optional[Union[Tuple[int], List[int]]]=(0,),
        xlabel:Optional[str]=None,
        xpad:Union[float, Tuple[float, float]]=0.3,
        ypad:Union[float, Tuple[float, float]]=0.35,
        logx:bool=False,
        legend_order:Optional[List[str]]=None,
    ):
        targets = self.resolve_targets(targets)
        if not targets:
            raise RuntimeError('No targets to draw')
        columns = columns or []
        value_columns = value_columns or []
        n_targets = len(targets)
        n_value_columns = len(value_columns)
        if (value_width * n_value_columns) > 1.0:
            raise RuntimeError(
                f'Total width of value columns ({value_width} * {n_value_columns} = {value_width * n_value_columns}) exceeds 1.'
            )
        text_boundaries = np.linspace(1. - (value_width * n_value_columns), 1., n_value_columns + 1)
        text_centers = (text_boundaries[:-1] + text_boundaries[1:]) / 2

        self.reset_metadata()
        ax = self.draw_frame(logx=logx)
        transform = create_transform(transform_x='axis', transform_y='data')

        handles = {}
        for i, target in enumerate(targets):
            data = self.df.loc[target].to_dict()
            for column in columns:
                resolved_column = self.column_map.get(column, column)
                label = self.label_map.get(f'legend.{column}', column)
                color = self.color_map.get(f'artist.{column}', None)
                # point limit
                if isinstance(resolved_column, str):
                    if resolved_column not in data:
                        raise ValueError(
                            f'Column not found: {resolved_column}'
                        )
                    x = [data[resolved_column]] * 3
                    y = [i, i + 0.5, i + 1]
                    styles = self.get_target_styles('plot', target=column)
                    styles.setdefault('label', label)
                    styles.setdefault('color', color)
                    handle = ax.plot(x, y, markevery=[1], **styles)[0]
                # range limit
                elif isinstance(resolved_column, (list, tuple)):
                    if len(resolved_column) != 2:
                        raise ValueError(
                            'Ranged limits must be specified as a tuple/list of columns in the form'
                            f'(lower_limit, higher_limit), not {resolved_column}'
                        )
                    x = [data[resolved_column[0]], data[resolved_column[1]]]
                    styles = self.get_target_styles('fill_between', target=column)
                    styles.setdefault('label', label)
                    styles.setdefault('color', color)
                    handle = ax.fill_between(x, i, i + 1, **styles)
                else:
                    raise ValueError(
                        f'Invalid format for `column_map` value: {type(resolved_column)}'
                    )
                if column not in handles:
                    handles[column] = handle

            # draw limit values
            for j, value_column in enumerate(value_columns):
                resolved_column = self.column_map.get(value_column, value_column)
                if not isinstance(resolved_column, str):
                    raise ValueError(
                        f'Value column must be a string, not {type(resolved_column)}.'
                    )
                if resolved_column not in data:
                    raise ValueError(
                        f'Column not found: {resolved_column}'
                    )
                x = text_centers[j]
                text = value_fmt.format(value=data[resolved_column])
                text_styles = self.get_target_styles('text', target='header')
                ax.text(x, i + 0.5, text, transform=transform, **text_styles)

                # draw header
                if i == 0:
                    text = self.label_map.get(f'text.{value_column}', value_column)
                    ax.text(x, n_targets + 0.3, text, transform=transform, **text_styles)

        # draw horizonal separating lines
        for line_index in line_indices:
            ax.axhline(
                n_targets - line_index,
                color=self.color_map.get('artist.hline'),
                **self.styles['hline']
            )
        
        self.update_legend_handles(handles)

        self._update_reference_limit_data(n_targets)
        self.finalize()

        self.draw_axis_components(
            ax,
            xlabel=xlabel,
            yticks=np.arange(n_targets) + 0.5,
            yticklabels=[self.label_map.get(target, target) for target in targets]
        )
        
        self.set_axis_range(ax, xpad=xpad, ypad=ypad)

        if legend_order is None:
            self.legend_order = list(self.handles)
        else:
            self.legend_order = list(legend_order)

        handles, labels = self.get_legend_handles_labels()
        if self.config['box_legend_border']:
            handles = remake_handles(handles, polygon_to_line=False, fill_border=True,
                                     border_styles=self.styles['legend_border'])
            
        self.draw_legend(ax, handles, labels)
        
        return ax
