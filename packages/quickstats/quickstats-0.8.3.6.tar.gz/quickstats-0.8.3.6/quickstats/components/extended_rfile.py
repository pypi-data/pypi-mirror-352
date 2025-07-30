##################################################################################################
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
from typing import List, Optional, Union, Dict, Sequence

import numpy as np

import quickstats
from quickstats import AbstractObject, cached_import
from quickstats.interface.root import TH1, TFile
from quickstats.utils.root_utils import list_root_files
from quickstats.utils.string_utils import remove_whitespace

class ExtendedRFile(AbstractObject):
    
    def __init__(self, source:Union[str, Dict[str, np.ndarray], "pandas.DataFrame"],
                 tree_name:Optional[str]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.initialize(source, tree_name)
    
    @property
    def components(self):
        return self._components
    
    @property
    def rdf(self):
        return self._rdf
    
    @property
    def rdf_map(self):
        return self._rdf_map
    
    @property
    def cache(self):
        return self._cache
    
    @property
    def canvas(self):
        return self._canvas
        
    def initialize(self, source:Union[str, Dict[str, np.ndarray]], tree_name:Optional[str]=None):
        ROOT = cached_import("ROOT")
        
        self._rdf_map = {}
        self._rdf     = None
        self._canvas = None
        self._cache  = []
        self._components = []        
        
        # initialize from ROOT file
        if isinstance(source, (str, list)):
            filenames = TFile.list_files(source)
            self.filenames = filenames
            if tree_name is not None:
                self.set_tree(tree_name)
        elif isinstance(source, dict):
            if quickstats.root_version >= (6, 28, 0):
                self._rdf = ROOT.RDF.FromNumpy(source)
            else:
                self._rdf = ROOT.RDF.MakeNumpyDataFrame(source)
            self._rdf_map[None] = self._rdf
            self.filenames = None
        else:
            import pandas as pd
            if isinstance(source, pd.DataFrame):
                from quickstats.utils.data_conversion import dataframe2numpy
                source = dataframe2numpy(source)
                self.initialize(source)
            else:
                raise RuntimeError("invalid source")
        
    def create_canvas(self):
        if not self.canvas:
            ROOT = cached_import("ROOT")
            self._canvas = ROOT.TCanvas()
    
    def canvas_draw(self):
        self.create_canvas()
        self.canvas.Draw()
    
    def add_tree(self, tree_name:str):
        ROOT = cached_import("ROOT")
        if tree_name in self._rdf_map:
            self.stdout.info("Tree already added to the rdf collection.")
            return None
        rdf = ROOT.RDataFrame(tree_name, self.filenames)
        if not rdf:
            raise RuntimeError(f'failed to load tree "{tree_name}"')
        self._rdf_map[tree_name] = rdf
        self.stdout.info(f'Added tree "{tree_name}" to the rdf collection')
        
    def set_tree(self, tree_name:str):
        if tree_name not in self._rdf_map:
            self.add_tree(tree_name)
        self._rdf = self._rdf_map[tree_name]
        self.stdout.info(f'Set active tree to "{tree_name}"')
    
    def validate(self):
        if self._rdf is None:
            raise RuntimeError("active tree not set")
            
    def _get_column(self, expr:str):
        if expr is None:
            return None
        expr = remove_whitespace(expr)
        if self.rdf.HasColumn(expr):
            return expr
        hash_str = str(hash(expr)).replace("-", "n")
        column_name = f'col_{hash_str}'
        if self.rdf.HasColumn(column_name):
            return column_name
        # define column if not exist
        self._rdf = self.rdf.Define(column_name, expr)
        return column_name
            
    def get_Histo1D(self, column:str, weight:Optional[str]=None,
                    bins:Union[int, Sequence]=128,
                    bin_range:Optional[Sequence]=None,
                    name:Optional[str]=None, title:Optional[str]=None,
                    pyobject:bool=False, draw:bool=False, draw_option:Optional[str]=None):
        self.validate()
        column_ = self._get_column(column)
        weight_ = self._get_column(weight)
        if name is None:
            if weight is None:
                name = column
            else:
                name = f'{column} * {weight}'
        if title is None:
            title = name
        th1d_model = TH1.create_model(bins=bins, bin_range=bin_range, name=name, title=title)
        if weight is None:
            r_th1_ptr = self.rdf.Histo1D(th1d_model, column_)
        else:
            r_th1_ptr = self.rdf.Histo1D(th1d_model, column_, weight_)
        r_th1 = r_th1_ptr.GetPtr()
        if draw:
            if draw_option is None:
                draw_option = ""
            self.create_canvas()
            r_th1.Draw(draw_option)
            self.add_cache(r_th1)
            self.canvas_draw()
        if pyobject:
            py_th1 = TH1(r_th1)
            return py_th1
        return r_th1
    
    def append(self, robject:"ROOT.TObject"):
        ROOT = cached_import("ROOT")
        if not isinstance(robject, ROOT.TObject):
            raise RuntimeError("only TObject can be added to TFile")
        self.stdout.info(f"Added object \"{robject.GetName()}\" to internal components")
        self._components.append(robject)
    
    def add_cache(self, robject:"ROOT.TObject"):
        ROOT = cached_import("ROOT")
        self.stdout.info(f"Added object \"{robject.GetName()}\" to cache")
        self._cache.append(robject)
        
    def clear_cache(self):
        self._cache = []
    
    def save_components(self, filename:str, mode:str="RECREATE", components:Optional[List]=None):
        ROOT = cached_import("ROOT")
        if components is None:
            components = self.components
        f = ROOT.TFile(filename, mode)
        f.cd()
        for component in components:
            component.Write()
        f.Close()