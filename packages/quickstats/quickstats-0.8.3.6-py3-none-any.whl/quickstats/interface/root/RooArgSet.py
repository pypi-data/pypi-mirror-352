from typing import Dict, Union, List, Optional

import numpy as np

import cppyy

from quickstats import semistaticmethod, cached_import
from quickstats.concepts import RealVariableSet
from quickstats.interface.cppyy.vectorize import as_vector
from .RooRealVar import RooRealVar

class RooArgSet:
    
    @staticmethod
    def from_list(args:List["ROOT.RooAbsArg"]):
        ROOT = cached_import("ROOT")
        return ROOT.RooArgSet(*args)

    @staticmethod
    def from_RealVariableSet(data: RealVariableSet):
        if not isinstance(data, RealVariableSet):
            raise TypeError('`data` must be an instance of RealVariableSet')
        args = [RooRealVar(variable).new() for variable in data]
        return RooArgSet.from_list(args)
    
    @staticmethod
    def sort(argset:"ROOT.RooArgSet"):
        argset.sort()
        return argset
    
    def get_boundary_parameters(argset:"ROOT.RooArgSet"):
        return cppyy.gbl.RFUtils.GetBoundaryParameters(argset)
    
    def select_by_class(argset:"ROOT.RooArgSet", classname:str):
        return cppyy.gbl.RFUtils.SelectByClass(argset, classname)
    
    def exclude_by_class(argset:"ROOT.RooArgSet", classname:str):
        return cppyy.gbl.RFUtils.ExcludeByClass(argset, classname)
    
    def select_dependent_parameters(argset:"ROOT.RooArgSet", source:"ROOT.RooAbsArg"):
        return cppyy.gbl.RFUtils.SelectDependentParameters(argset, source)
    
    def get_set_difference(argset1:"ROOT.RooArgSet", argset2:"ROOT.RooArgSet"):
        return cppyy.gbl.RFUtils.GetRooArgSetDifference(argset1, argset2)
    
    def set_constant_state(argset:"ROOT.RooArgSet", value:bool=True):
        argset.setAttribAll('Constant', value)
        
    def select_by_constant_state(argset:"ROOT.RooArgSet", value:bool=True):
        return argset.selectByAttrib('Constant', value)
         
    def get_parameters_close_to_min(argset:"ROOT.RooArgSet", threshold:float=0.1):
        return cppyy.gbl.RFUtils.GetParametersCloseToMin(argset, threshold)
    
    def get_parameters_close_to_max(argset:"ROOT.RooArgSet", threshold:float=0.1):
        return cppyy.gbl.RFUtils.GetParametersCloseToMax(argset, threshold)
    
    def get_parameters_close_to_boundary(argset:"ROOT.RooArgSet", threshold:float=0.1):
        return cppyy.gbl.RFUtils.GetParametersCloseToBoundary(argset, threshold)
    
    def expand_parameters_range(argset:"ROOT.RooArgSet", threshold:float=0.1,
                                expand_min:bool=True, expand_max:bool=True,
                                orig_argset_at_min:Optional["ROOT.RooArgSet"]=None,
                                new_argset_at_min:Optional["ROOT.RooArgSet"]=None,
                                orig_argset_at_max:Optional["ROOT.RooArgSet"]=None,
                                new_argset_at_max:Optional["ROOT.RooArgSet"]=None,):
        orig_argset_at_min = 0 if orig_argset_at_min is None else orig_argset_at_min
        new_argset_at_min = 0 if new_argset_at_min is None else new_argset_at_min
        orig_argset_at_max = 0 if orig_argset_at_max is None else orig_argset_at_max
        new_argset_at_max = 0 if new_argset_at_max is None else new_argset_at_max
        return cppyy.gbl.RFUtils.ExpandParametersRange(argset, threshold,
                                                       expand_min, expand_max,
                                                       orig_argset_at_min,
                                                       new_argset_at_min,
                                                       orig_argset_at_max,
                                                       new_argset_at_max)
    def set_category_indices(argset:"ROOT.RooArgSet", indices:np.ndarray):
        return cppyy.gbl.RFUtils.SetCategoryIndices(argset, as_vector(indices))

    def save_data_as_txt(argset:"ROOT.RooArgSet", filename:str, precision:int=7):
        return cppyy.gbl.RFUtils.SaveRooArgSetDataAsTxt(argset, filename, precision)