from typing import Optional, Union, Dict

from .registry import Registry

REGISTRY = Registry()

REGISTRY['default'] = {
    'status': 'int',
    'loc': (0.05, 0.95),
    'fontsize': 25
}

REGISTRY.use('default')

REGISTRY['atlas'] = REGISTRY.data & {
    'colab': 'ATLAS'
}

REGISTRY['atlas_run2'] = REGISTRY.data & {
    'colab': 'ATLAS',
    'energy' : '13 TeV', 
    'lumi' : "140 fb$^{-1}$",    
}

REGISTRY['atlas_run3'] = REGISTRY.data & {
    'colab': 'ATLAS',
    'energy' : '13.6 TeV'  
}

REGISTRY['cms'] = REGISTRY.data & {
    'colab': 'CMS'
}

get = REGISTRY.get
use = REGISTRY.use
parse = REGISTRY.parse
chain = REGISTRY.chain