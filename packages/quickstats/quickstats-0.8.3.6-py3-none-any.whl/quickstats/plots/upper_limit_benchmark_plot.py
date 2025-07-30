from typing import Optional, Union, Dict, List, Callable, Sequence

from matplotlib.lines import Line2D
from matplotlib.container import ErrorbarContainer
from matplotlib.legend_handler import HandlerErrorbar
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd

from quickstats.plots.template import create_transform, remake_handles
from quickstats.plots import AbstractPlot
from quickstats.utils.common_utils import combine_dict
from quickstats.maths.histograms import HistComparisonMode

class UpperLimitBenchmarkPlot(AbstractPlot):
    
    STYLES = {
        'figure':{
            'figsize': (11.111, 8.333),
            'dpi': 72,
            'facecolor': "#FFFFFF"
        },
        'ylabel':{
            'labelpad': 0
        },
        'errorbar': {
            'linestyle': 'none',
            'marker': 'o',
            'capsize': 0.0,
            'markersize': 8
        }
    }
    
    COLOR_MAP = {
        '2sigma' : 'hh:darkyellow',
        '1sigma' : 'hh:lightturquoise',
        'expected' : 'k',
        'observed' : 'k',
        'alt.2sigma' : '#ffcc00',
        'alt.1sigma' : '#00cc00',
        'alt.expected': 'r',
        'alt.observed': 'r',
        'theory' : 'darkred',
        'theory_unc' : 'hh:darkpink'
    }
    
    LABELS = {
        '2sigma': r'Expected limit $\pm 2\sigma$',
        '1sigma': r'Expected limit $\pm 1\sigma$',
        'expected': r'Expected limit (95% CL)',
        'observed': r'Observed limit (95% CL)',
        'alt.2sigma': r'Alt. Expected limit $\pm 2\sigma$',
        'alt.1sigma': r'Alt. Expected limit $\pm 1\sigma$',
        'alt.expected': r'Alt. Expected limit (95% CL)',
        'alt.observed': r'Alt. Observed limit (95% CL)',
        'theory'  : r'Theory prediction'
    }

    CONFIG = {     
        'xmargin': 0.3,
        'sigma_width': 0.6,
        'hide_shaded_data': True,
        'shade_main_panel': True,
        'shade_comparison_panel': False
    }
    
    CUSTOM_STYLES = {
        '2sigma': {
            'alpha': 1
        },
        '1sigma': {
            'alpha': 1
        },
        'expected': {
            'elinestyle': 'None',
            'elinewidth': 1,
            'markerfacecolor': 'None',
            'marker': 'o'
        },
        'observed': {
            'elinestyle': 'None',
            'elinewidth': 1,
            'marker': 'o'
        },
        'theory': {
            'elinestyle': 'None',
            'elinewidth': 1,            
            'marker': 'P'
        },
        'theory_unc': {
            'alpha': 1
        },
        'shade': {
            'hatch': '/',
            'alpha': 0.5,
            'color': 'gray'
        }
    }
        
    CUSTOM_STYLES_EXTRA = {
        '2sigma': {
            'alpha': 1
        },
        '1sigma': {
            'alpha': 1
        },
        'expected': {
            'elinestyle': 'None',
            'elinewidth': 1,
            'markerfacecolor': 'None',
            'marker': '^'
        },
        'observed': {
            'elinestyle': 'None',
            'elinewidth': 1,
            'marker': '^'
        },
        'shade': {
            'hatch': '\\',
            'alpha': 0.5,
            'color': 'gray'
        }
    }
    
    @property
    def theory_func(self):
        return self._theory_func    
    
    def __init__(self, data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
                 theory_func:Callable=None,
                 color_map:Optional[Dict]=None,
                 label_map:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 config:Optional[Dict]=None,
                 custom_styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Union[Dict, str]]=None):
        """
        Parameters:
            df: pandas.DataFrame
                dataframe with columns ("-2", "-1", "0", "1", "2", "obs") representing
                the corresponding limit level and rows indexed by the benchmark names
        """
        super().__init__(color_map=color_map,
                         label_map=label_map,
                         styles=styles, config=config,
                         analysis_label_options=analysis_label_options)
        self.data = data.copy()
        self.set_theory_function(theory_func)        
        self.custom_styles = combine_dict(self.CUSTOM_STYLES, custom_styles)
        self.alt_data = {}
        self.alt_custom_styles = {}
        self.hline_data = []
        
    def add_alternative_data(self, data:Optional[pd.DataFrame],
                             key:str="alt",
                             custom_styles:Optional[Dict]=None):
        if key is None:
            raise RuntimeError('key can not be None')
        self.alt_data[key] = data
        self.alt_custom_styles[key] = combine_dict(self.CUSTOM_STYLES_EXTRA, custom_styles)
        
    def get_default_legend_order(self):
        return ['observed', 'expected', '1sigma', '2sigma', 'theory']
    
    def set_theory_function(self, func:Optional[Callable]=None):
        if func is None:
            self._theory_func = None
            return
        if not isinstance(func, Callable):
            raise TypeError('theory function must be callable')
        self._theory_func = func
        
    def get_theory_prediction(self, *x:np.ndarray):
        if self.theory_func is None:
            raise RuntimeError('theory function not set')
        prediction = self.theory_func(*x)
        if not isinstance(prediction, tuple):
            return *x, prediction, None, None
        if len(prediction) == (len(x) + 1):
            return *prediction, None, None
        elif len(prediction) == (len(x) + 3):
            return *prediction,
        raise RuntimeError('invalid return format from theory function')        
    
    def add_hline(self, y:float,
                  label:str="Theory prediction",
                  **styles):
        hline_data = {
            'y'     : y,
            'label' : label,
            'styles': styles
        }
        self.hline_data.append(hline_data)
        self.legend_order.append(label)
        
    def draw_hlines(self, ax):
        for data in self.hline_data:
            h = ax.axhline(data['y'], label=data['label'], **data['styles'])
            self.update_legend_handles({data['label']: h})
            
    def draw_single_data(self, ax, data:pd.DataFrame,
                         color_pallete:Dict,
                         labels:Dict,
                         custom_styles:Dict,
                         shade_index:Optional[List[int]]=None,
                         data_key:Optional[str]=None,
                         draw_expected:bool=True,
                         draw_observed:bool=True,
                         draw_errorband:bool=True,
                         update_handle:bool=True):
        if shade_index is None:
            shade_index = []
        hide_shaded = self.config['hide_shaded_data']
        df = data
        nbenchmark = len(df.index)
        eps = self.config['sigma_width'] / 2
        handle_keys = {}
        for handle_type in ['expected', 'observed', '1sigma', '2sigma']:
            handle_keys[handle_type] = handle_type if data_key is None else f"{handle_type}_{data_key}"
        for index, (benchmark, limit) in enumerate(df.iterrows()):
            if (index in shade_index) and (hide_shaded):
                continue
            if draw_errorband:
                h_2sigma = ax.fill_between([index - eps, index + eps], limit['-2'] , limit['2'],
                                           facecolor=color_pallete['2sigma'],
                                           label=labels['2sigma'],
                                           **custom_styles['2sigma'])
                h_1sigma = ax.fill_between([index - eps, index + eps], limit['-1'], limit['1'],
                                           facecolor=color_pallete['1sigma'],
                                           label=labels['1sigma'],
                                           **custom_styles['1sigma'])
                if update_handle:
                    self.update_legend_handles({handle_keys['2sigma']: h_2sigma,
                                                handle_keys['1sigma']: h_1sigma})
        x = np.arange(nbenchmark)
        if hide_shaded:
            x = np.delete(x, shade_index)
        for flag, column, key in [(draw_expected, '0', 'expected'),
                                  (draw_observed, 'obs', 'observed')]:
            if not flag:
                continue
            styles = combine_dict(self.styles['errorbar'], custom_styles[key])
            # overwrite marker and errorbar colors
            for color_key in ['markerfacecolor', 'markeredgecolor', 'ecolor']:
                if color_key not in styles:
                    styles[color_key] = color_pallete[key]
            # overwrite the errorbar linestyle
            elinestyle = styles.pop('elinestyle', None)
            y = df[column].values[x]
            if elinestyle in ['None', 'none', None]:
                handle = ax.errorbar(x=x, y=y,
                                     label=labels[key], **styles)
            else:
                handle = ax.errorbar(x=x, y=y, xerr=eps,
                                     label=labels[key], **styles)
                if elinestyle is not None:
                    handle[-1][0].set_linestyle(elinestyle)
            if update_handle:
                self.update_legend_handles({handle_keys[key]: handle})
        shade_main_panel = self.config['shade_main_panel']
        if (shade_index is not None) and (shade_main_panel):
            for index, (benchmark, limit) in enumerate(df.iterrows()):
                if index not in shade_index:
                    continue        
                ax.fill_between([index - eps, index + eps], limit['-2'] , limit['2'],
                                **custom_styles['shade'])
            
    def draw_comparison_data(self, ax,
                             reference_data:pd.DataFrame,
                             target_data:pd.DataFrame,
                             color_pallete:Dict,
                             labels:Dict,
                             custom_styles:Dict,
                             mode:Union[HistComparisonMode, str]="ratio",
                             ignore_index:bool=False,
                             compare_expected:bool=True,
                             compare_observed:bool=True,
                             compare_errorband:bool=False):
        mode = HistComparisonMode.parse(mode)
        comparison_data = target_data.copy()
        if ignore_index:
            comparison_data.index = reference_data.index
        cols = ['-2', '-1', '0', '1', '2', 'obs']
        if mode == HistComparisonMode.RATIO:
            if compare_errorband:
                raise ValueError('can not compare errorband when comparison mode is set to "ratio"')
            comparison_data.loc[:, cols] = comparison_data.loc[:, cols].divide(reference_data[cols], axis="index")
        elif mode == HistComparisonMode.DIFFERENCE:
            comparison_data.loc[:, cols] = comparison_data.loc[:, cols].subtract(reference_data[cols], axis="index")
        self.draw_single_data(ax, comparison_data,
                              color_pallete=color_pallete,
                              labels=labels,
                              custom_styles=custom_styles,
                              draw_expected=compare_expected,
                              draw_observed=compare_observed,
                              draw_errorband=compare_errorband,
                              update_handle=False)
        
        # expand ylim according to data range
        target_cols = []
        if compare_expected:
            target_cols.append('0')
        if compare_observed:
            target_cols.append('obs')
        if compare_errorband:
            target_cols.extend(['-2', '-1', '1', '2'])
        y = comparison_data[target_cols].values
        ylim = list(ax.get_ylim())
        if ylim[0] > np.min(y):
            ylim[0] = np.min(y)
        if ylim[1] < np.max(y):
            ylim[1] = np.max(y)
        ax.set_ylim(ylim)
        
    def get_theory_scale(self, df:Optional[pd.DataFrame]=None,
                         iloc:Optional[List[int]]=None, target:Optional[str]=None):
        if df is None:
            df = self.get_target_df(iloc=iloc, target=target)
        nbenchmark = len(df.index)
        nlevel = df.index.nlevels 
        values = np.array(sum(df.index.values, ())).reshape(nbenchmark, nlevel).T
        theory_scale = self.get_theory_prediction(*values)[-3]
        theory_errlo = self.get_theory_prediction(*values)[-2]
        theory_errhi = self.get_theory_prediction(*values)[-1]
        df_theory = df.drop(columns=df.columns)
        df_theory['theory_scale'] = theory_scale
        df_theory['theory_errlo'] = theory_errlo
        df_theory['theory_errhi'] = theory_errhi
        return df_theory
    
    def get_target_df(self, iloc:Optional[List[int]]=None, target:Optional[str]=None):
        if target is None:
            df = self.data.copy()
        else:
            df = self.alt_data[target].copy()
        if iloc is not None:
            df = df.iloc[iloc]
        return df
    
    def draw_theory_points(self, ax, df:Optional[pd.DataFrame]=None,
                           iloc:Optional[List[int]]=None,
                           target:Optional[str]=None,
                           shade_index:Optional[List[int]]=None,
                           styles:Optional[Dict]=None,
                           color:Optional[str]=None,
                           unc_styles:Optional[Dict]=None,
                           unc_color:Optional[str]=None,
                           label:Optional[str]=None):
        if styles is None:
            styles = combine_dict(self.CUSTOM_STYLES['theory'])
        if color is None:
            color = self.COLOR_PALLETE['theory']
        if unc_styles is None:
            unc_styles = combine_dict(self.CUSTOM_STYLES['theory_unc'])
        if unc_color is None:
            unc_color = self.COLOR_PALLETE['theory_unc']
        if label is None:
            label = self.LABELS['theory']
        if shade_index is None:
            shade_index = []
        df_theory = self.get_theory_scale(df=df, iloc=iloc, target=target)
        nbenchmark = len(df_theory.index)
        eps = self.config['sigma_width'] / 2
        x = np.arange(nbenchmark)
        hide_shaded = self.config['hide_shaded_data']
        if hide_shaded:
            x = np.delete(x, shade_index)
        styles = combine_dict(self.styles['errorbar'], styles)
        unc_styles = combine_dict(unc_styles)
        # overwrite marker and errorbar colors
        for color_key in ['markerfacecolor', 'markeredgecolor', 'ecolor']:
            if color_key not in styles:
                styles[color_key] = color
        # overwrite the errorbar linestyle
        elinestyle = styles.pop('elinestyle', None)
        y = df_theory['theory_scale'].values[x]
        yerrlo = df_theory['theory_errlo'].values[x]
        yerrhi = df_theory['theory_errhi'].values[x]
        # draw errorbands
        handle_fill = None
        if (yerrlo[0] is not None) or (yerrhi[0] is not None):
            unc_styles['color'] = unc_color
            for x_i, yerrlo_i, yerrhi_i in zip(x, yerrlo, yerrhi):
                handle_fill = ax.fill_between([x_i - eps, x_i + eps], yerrlo_i , yerrhi_i,
                                              label=label, **unc_styles)
        # draw values
        if elinestyle in ['None', 'none', None]:
            handle_line = ax.errorbar(x=x, y=y, label=label, **styles)
        else:
            handle_line = ax.errorbar(x=x, y=y, xerr=eps,
                                      label=label, **styles)
            if elinestyle is not None:
                handle_line[-1][0].set_linestyle(elinestyle)
        if handle_fill is None:
            handle = handle_line
        else:
            handle = (handle_fill, handle_line)
        self.update_legend_handles({'theory': handle})
    
    def draw(self, iloc:Optional[List[int]]=None,
             shade_index:Optional[List[int]]=None,
             xticklabels:Optional[List[str]]=None,
             logy:bool=False, xlabel:str="", ylabel:str="", ylim=None,
             scale_theory:bool=False, draw_expected:bool=True,
             draw_observed:bool=True, draw_errorband:bool=True,
             draw_theory:bool=False,
             alt_draw_options:Optional[Dict]=None,
             comparison_options:Optional[Dict]=None):
        # setup input data
        targets = [None]
        if alt_draw_options is not None:
            targets.extend(list(alt_draw_options.keys()))
        target_kwargs = {}
        nbenchmark = None
        for target in targets:
            target_kwargs[target] = {}
            df = self.get_target_df(iloc=iloc, target=target)
            if target is None:
                target_kwargs[target]['color_pallete']  = self.color_pallete
                target_kwargs[target]['labels']         = self.labels
                target_kwargs[target]['custom_styles']  = self.custom_styles
                target_kwargs[target]['draw_expected']  = draw_expected
                target_kwargs[target]['draw_observed']  = draw_observed
                target_kwargs[target]['draw_errorband'] = draw_errorband
                target_scale_theory = scale_theory
            else:
                draw_options = alt_draw_options[target]
                target_kwargs[target]['color_pallete']  = self.alt_color_pallete[target]
                target_kwargs[target]['labels']         = self.alt_labels[target]
                target_kwargs[target]['custom_styles']  = self.alt_custom_styles[target] 
                target_kwargs[target]['draw_expected']  = draw_options.get('draw_expected', draw_expected)
                target_kwargs[target]['draw_observed']  = draw_options.get('draw_observed', draw_observed)
                target_kwargs[target]['draw_errorband'] = draw_options.get('draw_errorband', draw_errorband)
                target_scale_theory = draw_options.get('scale_theory', scale_theory)
            if nbenchmark is None:
                nbenchmark = len(df.index)
            elif len(df.index) != nbenchmark:
                RuntimeError(f'main and alternative data ("{target}") have different number of benchmark points')
            if target_scale_theory:
                df_theory = self.get_theory_scale(df=df)
                df.loc[df_theory.index, ['scale']] = df_theory['theory_scale']
                cols = ['-2', '-1', '0', '1', '2', 'obs']
                df.loc[:, cols] = df.loc[:, cols].multiply(df.loc[:, 'scale'], axis="index")
            target_kwargs[target]['data'] = df
            
        if xticklabels is None:
            xticklabels = [str(i) for i in range(nbenchmark)]
        elif len(xticklabels) != nbenchmark:
            raise ValueError('number of xtick labels does not match the number of benchmark points')
        else:
            xticklabels = list(xticklabels)

        if comparison_options is not None:
            ax, ax_ratio = self.draw_frame(frametype='ratio', logy=logy)
        else:
            ax = self.draw_frame(frametype='single', logy=logy)
            ax_ratio = None
            
        eps = self.config['sigma_width'] / 2
        xmargin = self.config['xmargin']
        xlim = (0 - eps - xmargin, nbenchmark - 1 + eps + xmargin)
        self.draw_axis_components(ax, ylabel=ylabel, xlabel=xlabel, ylim=ylim, xlim=xlim)
        
        for data_key, kwargs in target_kwargs.items():
            self.draw_single_data(ax, **kwargs, data_key=data_key,
                                  shade_index=shade_index)

        self.draw_hlines(ax)
        
        if comparison_options is not None:
            components = comparison_options.pop('components')
            for component in components:
                reference = component.pop('reference')
                target    = component.pop('target')
                kwargs    = {k:v for k,v in target_kwargs[target].items() \
                             if k in ['color_pallete', 'labels', 'custom_styles']}
                kwargs    = combine_dict(kwargs, component)
                if ('mode' not in kwargs) and ('mode' in comparison_options):
                    kwargs['mode'] = comparison_options['mode']
                self.draw_comparison_data(ax_ratio,
                                          target_kwargs[reference]['data'],
                                          target_kwargs[target]['data'],
                                          **kwargs)
            self.decorate_comparison_axis(ax, ax_ratio, **comparison_options)
            
            shade_comparison_panel = self.config['shade_comparison_panel']
            if (shade_index is not None) and shade_comparison_panel:
                transform = create_transform(transform_x='data', transform_y='axis')
                fill_styles = target_kwargs[None]['custom_styles']['shade']
                for index in shade_index:
                    ax_ratio.fill_between([index - eps, index + eps], 0, 1,
                                          **fill_styles,
                                          transform=transform)
        if draw_theory:
            theory_styles = target_kwargs[None]['custom_styles']['theory']
            theory_label  = target_kwargs[None]['labels']['theory']
            theory_color  = target_kwargs[None]['color_pallete']['theory']
            theory_unc_styles = target_kwargs[None]['custom_styles']['theory_unc']
            theory_unc_color = target_kwargs[None]['color_pallete']['theory_unc']
            self.draw_theory_points(ax, shade_index=shade_index,
                                    styles=theory_styles,
                                    color=theory_color,
                                    label=theory_label,
                                    unc_styles=theory_unc_styles,
                                    unc_color=theory_unc_color)
        ax.set_xticks(np.arange(nbenchmark))
        ax.set_xticklabels(xticklabels)
        
        handles, labels = self.get_legend_handles_labels()
        handles = remake_handles(handles, polygon_to_line=False, fill_border=True,
                                 border_styles=self.styles['legend_border'])
        handler_map = {ErrorbarContainer: HandlerErrorbar(xerr_size=1)}
        self.draw_legend(ax, handles, labels, handler_map=handler_map)
        
        if comparison_options is not None:
            return ax, ax_ratio
        
        return ax