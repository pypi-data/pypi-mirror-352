from typing import Optional, Union, List, Dict
import numpy as np

from quickstats import semistaticmethod, cached_import
from quickstats.core.typing import ArrayLike
from .TObject import TObject
from .TTree import TTree
from .TFile import TFile
from .RooDataSet import RooDataSet
from .TH1 import TH1

class TChain(TTree):
    
    def __init__(self, source: Optional[Union[str, List[str], Dict[str, str], "ROOT.TTree"]] = None,
                 default_treename: str=None, **kwargs):
        TObject.__init__(self, source=source, default_treename=default_treename, **kwargs)
        
    @staticmethod
    def _from_specs(specs:Dict[str, str]):
        ROOT = cached_import("ROOT")
        chain = ROOT.TChain()
        for filename, treename in specs.items():
            chain.AddFile(filename, ROOT.TTree.kMaxEntries, treename)
        return chain

    @staticmethod
    def _get_specs(source: Optional[Union[str, List[str], Dict[str, str]]] = None,
                   default_treename: str = None):
        if source is None:
            return {}
        def get_filename_treename(name:str):
            attributes = TChain.parse_tree_filename(name)
            filename = attributes['filename']
            treename = attributes['treename'] or default_treename or TFile._get_main_treename(filename)
            return filename, treename
                
        specs = {}
        if isinstance(source, str):
            source = [source]
        if isinstance(source, list):
            for name in source:
                filename, treename = get_filename_treename(name)
                specs[filename] = treename
        elif isinstance(source, dict):
            specs = source.copy()
        else:
            raise TypeError(f'unsupported source type: {type(source)}')
        return specs
        
    def initialize(self, source: Optional[Union[str, List[str], Dict[str, str]]] = None,
                   default_treename: str = None):
        ROOT = cached_import("ROOT")
        if isinstance(source, ROOT.TTree):
            self.obj = source
        else:
            specs = self._get_specs(source=source, default_treename=default_treename)
            self.obj = self._from_specs(specs)
        self.default_treename = default_treename

    def add(self, source: Union[str, List[str], Dict[str, str]]):
        ROOT = cached_import("ROOT")
        specs = self._get_specs(specs)
        chain = self.obj
        for filename, treename in specs.items():
            chain.AddFile(filename, ROOT.TTree.kMaxEntries, treename)