from typing import Optional, Union, Dict

from .registry import Registry

REGISTRY = Registry()

REGISTRY['default'] = {
    'figure':{
        'figsize': (11.111, 8.333),
        'dpi': 72,
        'facecolor': "#FFFFFF"
    },
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.gridspec.GridSpec.html
    'gridspec': {
        'height_ratios': None,
        'width_ratios': None,
        'wspace': None,
        'hspace': 0.05
    },
    'legend_Line2D': {
        'linewidth': 3
    },
    'legend_border': {
        'edgecolor' : 'black',
        'linewidth' : 1
    },        
    'annotate':{
        'fontsize': 20
    },
    'axis': {
        'major_length': 16,
        'minor_length': 8,
        'major_width': 2,
        'minor_width': 1,
        'spine_width': 2,
        'labelsize': 20,
        'offsetlabelsize': 20,
        'tick_bothsides': True,
        'x_axis_styles': {},
        'y_axis_styles': {}
    },
    'xtick':{
        'format': 'numeric',
        'locator': 'auto',
        'steps': None,
        'prune': None,
        'integer': False
    },
    'ytick':{
        'format': 'numeric',
        'locator': 'auto',
        'steps': None,
        'prune': None,
        'integer': False
    },        
    'xlabel': {
        'fontsize': 22,
        'loc' : 'right',
        'labelpad': 10
    },
    'ylabel': {
        'fontsize': 22,
        'loc' : 'top',
        'labelpad': 10
    },
    'title':{
        'fontsize': 20,
        'loc': 'center',
        'pad': 10
    },
    'text':{
        'fontsize': 20,
        'verticalalignment': 'top',
        'horizontalalignment': 'left'
    },
    'plot':{
        'linewidth': 2
    },
    'point': {
        'marker': 'o',
        'linestyle': 'none',
        'markersize': 10,
        'linewidth': 0
    },
    'hist': {
        'linewidth': 2
    },
    'errorbar': {
        "marker": 'x',
        "linewidth": 0,
        "markersize": 0,
        "elinewidth": 1,
        "capsize": 2,
        "capthick": 1
    },
    'fill_between': {
        "alpha": 0.5
    },
    'legend':{
        "fontsize": 20,
        "columnspacing": 0.8,
        "borderaxespad": 1
    },
    'ratio_frame':{
        'height_ratios': (3, 1),
        'hspace': 0.07            
    },
    'barh': {
        'height': 0.5
    },
    'bar': {
    },
    'colorbar': {
        'fraction': 0.15, 
        'shrink': 1.
    },
    'contour':{
        'linestyles': 'solid',
        'linewidths': 3            
    },
    'contourf':{
        'alpha': 0.5,
        'zorder': 0
    },
    'colorbar_axis': {
        'labelsize': 20,
        'y_axis_styles': {
            'labelleft': False,
            'labelright': True,
            'left': False,
            'right': True,
            'direction': 'out'
        }
    },
    'colorbar_label': {
        'fontsize': 22,
        'labelpad': 0
    },
    'clabel': {
        'inline': True,
        'fontsize': 10            
    },
    'line': {
    },
    'vline': {
    },
    'hline': {
    },
    'line_collection': {
    },
    'ellipse': {
    }
}

REGISTRY.use('default')

get = REGISTRY.get
use = REGISTRY.use
parse = REGISTRY.parse
chain = REGISTRY.chain