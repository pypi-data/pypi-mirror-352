from typing import Optional, Union, Dict, List, Callable

import numpy as np
import pandas as pd

import matplotlib.patches as patches
import matplotlib.lines as lines

from quickstats.plots import AbstractPlot
from quickstats.utils.common_utils import combine_dict
from quickstats.maths.interpolation import get_intervals_between_curves

class UpperLimit2DPlot(AbstractPlot):
    
    STYLES = {
        'axis':{
            'tick_bothsides': False
        },
        'errorbar': {
            "linewidth": 1,
            "markersize": 5,
            "marker": 'o',
        },
        'annotate': {
            "fontsize": 18
        }
    }
    
    COLOR_PALLETE = {
        '2sigma': '#FDC536',
        '1sigma': '#4AD9D9',
        'expected': 'k',
        'observed': 'k'
    }
    
    COLOR_PALLETE_EXTRA = {
        '2sigma': '#FDC536',
        '1sigma': '#4AD9D9',
        'expected': 'r',
        'observed': 'r'
    }
    
    LABELS = {
        '2sigma': r'Expected limit $\pm 2\sigma$',
        '1sigma': r'Expected limit $\pm 1\sigma$',
        'expected': 'Expected limit (95% CL)',
        'observed': 'Observed limit (95% CL)',
        'theory'  : 'Theory prediction'
    }
    
    LABELS_EXTRA = {
        '2sigma': r'Expected limit $\pm 2\sigma$',
        '1sigma': r'Expected limit $\pm 1\sigma$',
        'expected': 'Expected limit (95% CL)',
        'observed': 'Observed limit (95% CL)'
    }

    CONFIG = {
        'primary_hatch'  : '\\\\\\',
        'secondary_hatch': '///',
        'primary_alpha'  : 0.9,
        'secondary_alpha': 0.8,
        'theory_granularity': 1000,
        'curve_line_styles': {
            'color': 'darkred' 
        },
        'curve_fill_styles':{
            'color': 'hh:darkpink'
        },
        'highlight_styles': {
            'linewidth' : 0,
            'marker' : '*',
            'markersize' : 20,
            'color' : '#E9F1DF',
            'markeredgecolor' : 'black'
        },
        'errorband_plot_styles':{
            'alpha': 1
        },
        'expected_plot_styles': {
            'marker': 'None',
            'linestyle': '--',
            'alpha': 1,
            'linewidth': 1
        },
        'observed_plot_styles': {
            'marker': 'o',
            'alpha': 1,
            'linewidth': 1
        },
        'constraint_options': {
            'loc': (0.05, 0.25),
            'dy': 0.06,
            'decimal_place': 2,
            'use_signal_strength': True,
            'expected_interval_fmt': r'Expected: {xlabel}$\in [{lower_interval:.{decimal_place}f}'
                                     r', {upper_interval:.{decimal_place}f}]$',
            'observed_interval_fmt': r'Observed: {xlabel}$\in [{lower_interval:.{decimal_place}f}'
                                     r', {upper_interval:.{decimal_place}f}]$',
            'expected_length_fmt': r'Allowed range: {length:.{decimal_place}f}',
            'observed_length_fmt': r'Allowed range: {length:.{decimal_place}f}'
        }
    }
    
    @property
    def theory_func(self):
        return self._theory_func
    
    def __init__(self, data:pd.DataFrame,
                 additional_data:Optional[List[Dict]]=None,
                 theory_func:Callable=None,
                 color_map:Optional[Dict]=None,
                 labels:Optional[Dict]=None,
                 config:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Union[Dict, str]]='default'):
        super().__init__(color_map=color_map,
                         config=config,
                         styles=styles,
                         analysis_label_options=analysis_label_options)
        self.data = self._process_data(data)
        
        self.additional_data = []
        if additional_data is not None:
            for _data in additional_data:
                self.add_data(**_data)
        
        self.labels = combine_dict(self.LABELS, labels)
 
        self.set_theory_function(theory_func)
        
        self.curve_data     = None
        self.highlight_data = None
        
    def _process_data(self, data:pd.DataFrame):
        data = data.copy()
        data.index = data.index.astype(float)
        data = data.sort_index()
        return data
        
    def get_default_legend_order(self):
        return ['observed', 'expected', '1sigma', '2sigma', 'curve', 'highlight']
    
    def set_theory_function(self, func:Optional[Callable]=None):
        if func is None:
            self._theory_func = None
            return
        if not isinstance(func, Callable):
            raise TypeError('theory function must be callable')
        self._theory_func = func
        
    def get_theory_prediction(self, x:np.ndarray):
        if self.theory_func is None:
            raise RuntimeError('theory function not set')
        prediction = self.theory_func(x)
        if not isinstance(prediction, tuple):
            return np.array(x), prediction, None, None
        if len(prediction) == 2:
            return prediction[0], prediction[1], None, None
        elif len(prediction) == 4:
            return prediction[0], prediction[1], prediction[2], prediction[3]
        raise RuntimeError('invalid return format from theory function')
    
    def add_curve(self, x:np.ndarray, y:np.ndarray,
                  yerrlo:Optional[np.ndarray]=None,
                  yerrhi:Optional[np.ndarray]=None,
                  label:str="Theory prediction",
                  line_styles:Optional[Dict]=None,
                  fill_styles:Optional[Dict]=None):
        curve_data = {
            'x'     : x,
            'y'     : y,
            'yerrlo'  : yerrlo,
            'yerrhi'  : yerrhi,
            'label' : label,
            'line_styles': line_styles,
            'fill_styles': fill_styles,
        }
        self.curve_data = curve_data
                        
    def add_highlight(self, x:float, y:float, label:str="SM prediction",
                      styles:Optional[Dict]=None):
        highlight_data = {
            'x'     : x,
            'y'     : y,
            'label' : label,
            'styles': styles
        }
        self.highlight_data = highlight_data        
    
    def draw_curve(self, ax, option:Dict):
        line_styles = option['line_styles']
        fill_styles = option['fill_styles']
        if line_styles is None:
            line_styles = self.config['curve_line_styles']
        if fill_styles is None:
            fill_styles = self.config['curve_fill_styles']
        x, y, label = option['x'], option['y'], option['label']
        yerrlo, yerrhi = option['yerrlo'], option['yerrhi']
        if (yerrlo is None) and (yerrhi is None):
            line_styles['color'] = fill_styles['color']
        line_handle = ax.plot(x, y, label=label, **line_styles)
        handles = line_handle[0]
        if (yerrlo is not None) and (yerrhi is not None):
            fill_handle = ax.fill_between(x, yerrlo, yerrhi, label=label, **fill_styles)
            handles = (fill_handle, line_handle[0])
        self.update_legend_handles({'curve': handles})
        
    def draw_highlight(self, ax, option):
        styles = option['styles']
        if styles is None:
            styles = self.config['highlight_styles']
        x, y, label = option['x'], option['y'], option['label']
        handle = ax.plot(x, y, label=label, **styles)
        self.update_legend_handles({'highlight': handle[0]})
        
    def draw_single_data(self, ax, data:pd.DataFrame,
                         column:Optional[str]=None,
                         scale_theory:bool=False,
                         logx:bool=False,
                         logy:bool=False,
                         draw_expected:bool=True,
                         draw_observed:bool=True,
                         color_pallete:Optional[Dict]=None,
                         labels:Optional[Dict]=None,
                         sigma_band_hatch:Optional[str]=None,
                         draw_errorband:bool=True,
                         config:Optional[Dict]=None,
                         domain:Optional[str]=None):
        if config is None:
            config = self.config
        else:
            config = combine_dict(self.config, config)
            
        if color_pallete is None:
            color_pallete = self.color_pallete
            
        if labels is None:
            labels = self.labels
       
        if column is None:
            x = data.index.astype(float).values
        else:
            x = data[column].values
            
        if (not scale_theory) or (self.theory_func is None):
            scale_factor = 1.0
        else:
            _, scale_factor, _, _ = self.get_theory_prediction(x)

        handles_map = {}
        
        # draw +- 1, 2 sigma bands 
        if draw_errorband:
            y_n1sigma = data['-1'].values * scale_factor
            y_n2sigma = data['-2'].values * scale_factor
            y_p1sigma = data['1'].values  * scale_factor
            y_p2sigma = data['2'].values  * scale_factor
            handle_2sigma = ax.fill_between(x, y_n2sigma, y_p2sigma, 
                                            facecolor=color_pallete['2sigma'],
                                            label=labels['2sigma'],
                                            hatch=sigma_band_hatch,
                                            **config["errorband_plot_styles"])
            handle_1sigma = ax.fill_between(x, y_n1sigma, y_p1sigma, 
                                            facecolor=color_pallete['1sigma'],
                                            label=labels['1sigma'],
                                            hatch=sigma_band_hatch,
                                            **config["errorband_plot_styles"])
            handles_map['1sigma'] = handle_1sigma
            handles_map['2sigma'] = handle_2sigma
        
        if (not logx) and (not logy):
            draw_fn = ax.plot
        elif logy and (not logx):
            draw_fn = ax.semilogy
        elif logx and (not logy):
            draw_fn = ax.semilogx
        else:
            draw_fn = ax.loglog
 
        if draw_observed:
            y_obs = data['obs'].values * scale_factor
            handle_observed = draw_fn(x, y_obs, color=color_pallete['observed'], 
                                      label=labels['observed'], 
                                      **config["observed_plot_styles"])
            handles_map['observed'] = handle_observed[0]
        
        if draw_expected:
            y_exp = data['0'].values  * scale_factor
            handle_expected = draw_fn(x, y_exp, color=color_pallete['expected'],
                                      label=labels['expected'],
                                      **config["expected_plot_styles"])
            handles_map['expected'] = handle_expected[0]

        self.update_legend_handles(handles_map, domain=domain)
        
    def add_data(self, data:pd.DataFrame, color_pallete:Optional[Dict]=None,
                 labels:Optional[Dict]=None, draw_expected:bool=True,
                 draw_observed:bool=False,
                 draw_errorband:bool=False,
                 config:Optional[Dict]=None):
        config = {
            "data": self._process_data(data),
            "color_pallete": combine_dict(self.COLOR_PALLETE_EXTRA, color_pallete),
            "labels": combine_dict(self.LABELS_EXTRA, labels),
            "draw_observed": draw_observed,
            "draw_expected": draw_expected,
            "draw_errorband": draw_errorband,
            "config": config
        }
        self.additional_data.append(config)
            
    def get_interval_and_length(self, x, y, scale_theory:bool=False):
        theo_x = np.linspace(np.min(x), np.max(x), self.config['theory_granularity'])
        use_signal_strength = self.config['constraint_options']['use_signal_strength']
        if (not use_signal_strength) and (scale_theory and (self.theory_func is not None)):
            _, scale_y, _, _ = self.get_theory_prediction(x)
            _, theo_y, _, _ = self.get_theory_prediction(theo_x)
            interval = get_intervals_between_curves(x, y * scale_y, theo_x, theo_y)
        else:
            interval = get_intervals_between_curves(x, y, theo_x, np.ones(theo_x.shape))
        if len(interval) == 0:
            return None, None
        if np.isfinite(interval).all():
            length = (interval[1] - interval[0])
        else:
            length = None
        return interval, length
    
    def draw_constraint(self, ax, data:pd.DataFrame,
                        xlabel:str="",
                        scale_theory:bool=False,
                        draw_expected:bool=True,
                        draw_observed:bool=True,
                        draw_interval:bool=True,
                        draw_length:bool=True,
                        option:Optional[Dict]=None):
        if option is None:
            option = self.config['constraint_options']
        decimal_place = option['decimal_place']
        loc = option['loc']
        dy  = option['dy']
        texts = []
        x = data.index.values
        for flag, column, key in [(draw_expected, '0', 'expected'),
                                  (draw_observed, 'obs', 'observed')]:
            if not flag:
                continue
            y = data[column].values
            interval, length = self.get_interval_and_length(x, y, scale_theory=scale_theory)
            if draw_interval and (interval is not None):
                interval_str = option[f'{key}_interval_fmt'].format(xlabel=xlabel,
                                                                    lower_interval=interval[0],
                                                                    upper_interval=interval[1],
                                                                    decimal_place=decimal_place)
                interval_str = interval_str.replace('-inf', r'N.A.').replace('inf', 'N.A.')
                texts.append(interval_str)
            if draw_length and (length is not None):
                interval_str = option[f'{key}_length_fmt'].format(length=length, decimal_place=decimal_place)
                texts.append(interval_str)
        for i, text in enumerate(texts):
            ax.annotate(text, (loc[0], loc[1] - i * dy), xycoords='axes fraction',
                        **self.styles['annotate'])
    
    def _get_candidate_columns(self, data:pd.DataFrame):
        cols = [col for col in data.columns if col not in ['-2', '-1', '0', '1', '2', 'obs', 'inj']]
        return cols
    
    def draw(self, column:Optional[str]=None, xlabel:str="", ylabel:str="",
             ylim=None, xlim=None, scale_theory:bool=False, logx:bool=False,
             logy:bool=False, draw_expected:bool=True, draw_observed:bool=True,
             draw_errorband:bool=True, draw_hatch:bool=True,
             draw_theory_curve:bool=False, draw_interval:bool=False,
             draw_length:bool=False):
        
        ax = self.draw_frame()
        
        if len(self.additional_data) > 0:
            if draw_hatch:
                sigma_band_hatch = self.config['secondary_hatch']
                alpha = self.config['secondary_alpha']
            else:
                sigma_band_hatch = None
                alpha = 1.
            for idx, config in enumerate(self.additional_data):
                data_i = config["data"].copy().sort_index()
                domain = f'extra_data_{idx + 1}'
                self.draw_single_data(ax, data_i, column=column,
                                      logx=logx, logy=logy,
                                      scale_theory=scale_theory,
                                      draw_expected=config["draw_expected"],
                                      draw_observed=config["draw_observed"],
                                      color_pallete=config["color_pallete"],
                                      labels=config["labels"],
                                      sigma_band_hatch=sigma_band_hatch,
                                      draw_errorband=config["draw_errorband"],
                                      domain=domain,
                                      config=config["config"])
            if draw_hatch:
                sigma_band_hatch = self.config['primary_hatch']
                alpha = self.config['primary_alpha']
            else:
                sigma_band_hatch = None
                alpha = 1.
        else:
            sigma_band_hatch = None
            alpha = 1.
            
        self.draw_single_data(ax, self.data, column=column,
                              logx=logx, logy=logy,
                              scale_theory=scale_theory,
                              draw_expected=draw_expected,
                              draw_observed=draw_observed,
                              color_pallete=self.color_pallete,
                              labels=self.labels,
                              sigma_band_hatch=sigma_band_hatch,
                              draw_errorband=draw_errorband)
        
        if draw_theory_curve and (self.theory_func is not None) and (self.curve_data is None):
            x = self.data.index.values
            xmin, xmax = np.min(x), np.max(x)
            theo_x = np.linspace(xmin, xmax, self.config['theory_granularity'] + 1)
            theo_x, theo_y, theo_yerrlo, theo_yerrhi = self.get_theory_prediction(theo_x)
            self.add_curve(theo_x, theo_y, theo_yerrlo, theo_yerrhi,
                           label=self.labels['theory'])
            
        if self.curve_data is not None:
            self.draw_curve(ax, self.curve_data)
            
        if self.highlight_data is not None:
            self.draw_highlight(ax, self.highlight_data)
            
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        
        if ylim is not None:
            ax.set_ylim(*ylim)
        if xlim is not None:
            ax.set_xlim(*xlim)

        legend_domains = self.get_legend_domains()
        
        # border for the legend
        border_leg = patches.Rectangle((0, 0), 1, 1, facecolor = 'none', edgecolor = 'black', linewidth = 1)
        
        for domain in legend_domains:
            self.add_legend_decoration(border_leg, ['1sigma', '2sigma'], domain=domain)

        if self.curve_data is not None:
            if isinstance(self.get_handle('curve'), tuple):
                self.add_legend_decoration(border_leg, ['curve'])
        
        if draw_interval or draw_length:
            self.draw_constraint(ax, self.data, xlabel=xlabel,
                                 scale_theory=scale_theory,
                                 draw_expected=draw_expected,
                                 draw_observed=draw_observed,
                                 draw_interval=draw_interval,
                                 draw_length=draw_length)

        self.draw_legend(ax, domains=legend_domains)

        return ax
