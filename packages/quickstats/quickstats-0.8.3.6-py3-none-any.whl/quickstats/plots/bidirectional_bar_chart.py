from typing import Optional, Union, Dict, List

import numpy as np
import pandas as pd
from matplotlib import lines, patches

from quickstats.plots import AbstractPlot
from quickstats.utils.common_utils import combine_dict

class BidirectionalBarChart(AbstractPlot):
    
    STYLES = {
        'figure':{
            'figsize': (15.111, 4.333),
            'dpi': 200
        },
        'legend':{
          'loc': (0.02, 0.75),
          "fontsize": 15
        },
        'axis': {
            'major_length': 12,
            'minor_length': 0,
            'major_width': 1,
            'minor_width': 0,
            'spine_width': 2,
            'labelsize': 15,
            'offsetlabelsize': 20,
            'tick_bothsides': False,
            'direction': 'out'
        },
        'ylabel': {
            'fontsize': 15,
            'loc' : 'top',
            'labelpad': 10
        }
    }
    
    CONFIG = {
        "primary_up": {
            "linewidth" : 2,
            "linestyle" : '-',
            "alpha"     : 1,
            "edgecolor" : '#F16767',
            "color"     : '#F16767',
            "fill"      : False
        },
        "primary_down": {
            "linewidth" : 2,
            "linestyle" : '-',
            "alpha"     : 1,
            "edgecolor" : '#537FE7',
            "color"     : '#537FE7',
            "fill"      : False        
        },
        "secondary_up": {
            "linewidth" : 2,
            "linestyle" : '--',
            "alpha"     : 1,
            "edgecolor" : '#F16767',
            "color"     : '#F16767',
            "fill"      : False        
        },
        "secondary_down": {
            "linewidth" : 2,
            "linestyle" : '--',
            "alpha"     : 1,
            "edgecolor" : '#537FE7',
            "color"     : '#537FE7',
            "fill"      : False
        },
        "primary_errup": {
            "linewidth" : 0,
            "color"     : '#F16767',
            "alpha"     : 0.7
        },
        "primary_errdown": {
            "linewidth" : 0,
            "color"     : '#537FE7',
            "alpha"     : 0.7
        },
        "secondary_errup": {
            "linewidth" : 0,
            "color"     : '#F16767',
            "alpha"     : 0.4 
        },
        "secondary_errdown": {
            "linewidth" : 0,
            "color"     : '#537FE7',
            "alpha"     : 0.4  
        },
        "legend_updown":{
            "colorup": '#F16767',
            "labelup": r'+1$\sigma$',
            "colordown": '#537FE7',
            "labeldown": r'-1$\sigma$',
            "lw": 2.5,
            "loc": "upper right",
            "fontsize": 15
            
        },
        'xticklabel_rotation': 90
    }
    
    def __init__(self, collective_data:Union[Dict, "pandas.DataFrame"],
                 color_cycle:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Union[Dict, str]]=None,
                 config:Optional[Dict]=None):
        super().__init__(color_cycle=color_cycle,
                         styles=styles,
                         label_map=label_map,
                         analysis_label_options=analysis_label_options,
                         config=config)
        if isinstance(collective_data, dict):
            self.collective_data = {key:data.copy() for key, data in collective_data.items()}
            assert len(self.collective_data) > 0
        else:
            self.collective_data = collective_data.copy()
        
    def draw_single_data(self, ax, width:float,
                         x:np.ndarray,
                         yup:np.ndarray,
                         ydown:np.ndarray,
                         yup_styles:Dict,
                         ydown_styles:Dict,
                         yuperr:Optional[np.ndarray]=None,
                         ydownerr:Optional[np.ndarray]=None,
                         yuperr_styles:Optional[Dict]=None,
                         ydownerr_styles:Optional[Dict]=None):
        handle_up = ax.bar(x, yup, width=width, **yup_styles)
        handle_down = ax.bar(x, ydown, width=width, **ydown_styles)
        if (yuperr is not None) and (ydownerr is not None):
            handle_uperr = ax.bar(x, height=yuperr * 2,
                   bottom=yup - yuperr, width=width,
                   **yuperr_styles, zorder=-1)
            handle_downerr = ax.bar(x, height=ydownerr * 2,
                   bottom=ydown - ydownerr, width=width,
                   **ydownerr_styles, zorder=-1)
        else:
            handle_uperr, handle_downerr = None, None
        return handle_up, handle_down, handle_uperr, handle_downerr
    
    def get_selected_data(self, xattrib:str,
                          yupattrib:str, ydownattrib:str,
                          yuperrattrib:Optional[str]=None,
                          ydownerrattrib:Optional[str]=None,                          
                          targets:Optional[List[str]]=None,
                          merge_option:str="intersection"):
        selected_data = []
        yattributes = [yupattrib, ydownattrib]
        if (yuperrattrib is not None) and (ydownerrattrib is not None):
            yattributes.extend([yuperrattrib, ydownerrattrib])
        def get_slim_df(df):
            return df.reset_index().set_index(xattrib)[yattributes]
        if targets is not None:
            if not isinstance(self.collective_data, dict):
                raise RuntimeError('can not specify targets: input data is not a dictionary')
            n_target = len(targets)
            if n_target not in [1, 2]:
                raise ValueError('only one or two target(s) should be given')
            for target in targets:
                if target not in self.collective_data:
                    raise RuntimeError(f'target "{target}" not found in input data')
            selected_data.append([targets[0], get_slim_df(self.collective_data[targets[0]])])
            if n_target == 2:
                selected_data.append([targets[1], get_slim_df(self.collective_data[targets[1]])])
        else:
            if isinstance(self.collective_data, dict):
                n_data = len(self.collective_data)
                if n_data > 2:
                    raise RuntimeError('targets must be specified for input data with more than 2 keys')
                for key, data in self.collective_data.items():
                    selected_data.append([key, get_slim_df(data)])
            else:
                selected_data.append(["", get_slim_df(self.collective_data)])
        if len(selected_data) == 2:
            if merge_option == "intersection":
                common_index = selected_data[0][1].index.intersection(selected_data[1][1].index)
                selected_data[0][1] = selected_data[0][1].loc[common_index]
                selected_data[1][1] = selected_data[1][1].loc[common_index]
            elif merge_option == "union":
                diff_index = selected_data[0][1].index.difference(selected_data[1][1].index)
                selected_data[1][1] = pd.concat([selected_data[1][1], selected_data[0][1].loc[diff_index]])
                selected_data[1][1].loc[diff_index, yattributes] = 0
                diff_index = selected_data[1][1].index.difference(selected_data[0][1].index)
                selected_data[0][1] = pd.concat([selected_data[0][1], selected_data[1][1].loc[diff_index]])
                selected_data[0][1].loc[diff_index, yattributes] = 0
                selected_data[1][1] = selected_data[1][1].sort_index()
                selected_data[0][1] = selected_data[0][1].sort_index()
            else:
                raise ValueError(f"unknwon merge option: {merge_option}")
        return selected_data
    
    def draw(self, xattrib:str,
             yupattrib:str, ydownattrib:str,
             yuperrattrib:Optional[str]=None,
             ydownerrattrib:Optional[str]=None,
             width:float=1,
             xlabel: Optional[str] = None,
             ylabel: Optional[str] = None,
             ymax=None, ymin=None,
             xticklabel_rotation:float=90,
             targets:Optional[List[str]]=None,
             merge_option:str="intersection"):
        selected_data = self.get_selected_data(xattrib, yupattrib, ydownattrib,
                                               yuperrattrib=yuperrattrib,
                                               ydownerrattrib=ydownerrattrib,
                                               targets=targets,
                                               merge_option=merge_option)
        labels = selected_data[0][1].index.values
        n_label = len(labels)
        x = np.arange(0, width * n_label, width) + width
        xmin = 0
        xmax = x[-1] + width
        
        ax = self.draw_frame()
        
        target_labels = []
        for i, (label, data) in enumerate(selected_data):
            yup, ydown = data[yupattrib].values, data[ydownattrib].values
            if (yuperrattrib is not None) and (ydownerrattrib is not None):
                yuperr, ydownerr = data[yuperrattrib].values, data[ydownerrattrib].values
            else:
                yuperr, ydownerr = None, None
            key = 'primary' if i == 0 else 'secondary'
            yup_styles = self.config[f'{key}_up']
            ydown_styles = self.config[f'{key}_down']
            yuperr_styles = self.config[f'{key}_errup']
            ydownerr_styles = self.config[f'{key}_errdown']
            self.draw_single_data(ax, width, x,
                                  yup=yup,
                                  ydown=ydown,
                                  yuperr=yuperr,
                                  ydownerr=ydownerr,
                                  yup_styles=yup_styles,
                                  ydown_styles=ydown_styles,
                                  yuperr_styles=yuperr_styles,
                                  ydownerr_styles=ydownerr_styles)
            target_labels.append(label)
            
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=self.config['xticklabel_rotation'])
        
        # legend for up down variation
        leg_config = self.config['legend_updown']
        handles_updown = [lines.Line2D([0], [0], color=leg_config['colorup'],
                                       lw=leg_config['lw']),
                          lines.Line2D([0], [0], color=leg_config['colordown'],
                                       lw=leg_config['lw'])]
        labels_updown  = [leg_config['labelup'], leg_config['labeldown']] 
        legend_updown = ax.legend(handles_updown, labels_updown,
                                  loc=leg_config['loc'], frameon=False,
                                  fontsize=leg_config['fontsize'])
        if len(target_labels) == 2:
            primary_styles = {k:v for k,v in self.config['primary_up'].items() \
                              if 'color' not in k and 'fill' not in k}
            primary_styles['color'] = 'k'
            secondary_styles = {k:v for k,v in self.config['secondary_up'].items() \
                              if 'color' not in k and 'fill' not in k}
            secondary_styles['color'] = 'k'
            target_handles = [lines.Line2D([0], [0], **primary_styles),
                              lines.Line2D([0], [0], **secondary_styles)]
            self.draw_legend(ax, handles=target_handles, labels=target_labels)
            ax.add_artist(legend_updown)
        return ax