from typing import Dict, Union, List, Optional
import copy

import numpy as np
import cppyy

from quickstats import semistaticmethod, cached_import
from quickstats.concepts import Binning, RealVariable
from quickstats.maths.numerics import get_proper_ranges
from quickstats.interface.root import TArrayData

class RooRealVar:
    
    @property
    def range(self):
        return self._range
    
    @range.setter
    def range(self, value:Optional[List[float]]=None):
        self._range = self._parse_value_range(value, self.value)
   
    @property
    def named_ranges(self):
        return self._named_ranges
    
    @named_ranges.setter
    def named_ranges(self, value:Optional[Dict[str, List[float]]]=None):
        self._named_ranges = self._parse_named_ranges(value)
        
    def __init__(self, obj:Optional[Union[Dict, "ROOT.RooRealVar"]]=None):
        self.name   = None
        self.title  = None
        self.value  = None
        self.nbins = None
        self.unit   = None
        self.range  = None
        self.named_ranges = None
        if obj is not None:
            self.parse(obj)
        
    def parse(self, obj:Union[str, Dict, "ROOT.RooRealVar"]):
        if isinstance(obj, str):
            self.parse({"name": obj})
        elif isinstance(obj, dict):
            self.name = obj["name"]
            self.title = obj.get("title", None)
            self.value = obj.get("value", None)
            self.range = obj.get("range", None)
            self.named_ranges = obj.get("named_ranges", None)
            self.nbins = obj.get("nbins", None)
            self.unit = obj.get("unit", None)
        elif isinstance(obj, RooRealVar):
            self.__dict__ = copy.deepcopy(obj.__dict__)
        elif isinstance(obj, RealVariable):
            self.name = obj.name
            self.title = obj.description
            self.value = obj.value
            self.range = (obj.range.min, obj.range.max)
            self.nbins = obj.nbins
            named_ranges = {}
            for range_name, range_data in obj.named_ranges:
                named_ranges[range_name] = (range_data.min, range_data.max)
            self.named_ranges = named_ranges
            self.unit = obj.unit
        else:
            isvalid = hasattr(obj, 'ClassName') and (obj.ClassName() == 'RooRealVar')
            if not isvalid:
                raise ValueError("object must be an instance of ROOT.RooRealVar")
            self.name   = str(obj.GetName())
            self.title  = str(obj.getTitle())
            self.value  = obj.getVal()
            self.nbins = obj.getBins()
            self.unit   = obj.getUnit()
            _range = obj.getRange()
            self.range = [_range[0], _range[1]]
            named_ranges = {}
            for name in obj.getBinningNames():
                if str(name) in ["", "cache"]:
                    continue
                _range = obj.getRange(name)
                named_ranges[name] = [_range[0], _range[1]]
            self.named_ranges = named_ranges
        
    @staticmethod
    def _parse_named_ranges(named_ranges:Optional[Dict[str, List[float]]]=None):
        if named_ranges:
            ranges = get_proper_ranges(list(named_ranges.values()), no_overlap=False)
            result = {k:v for k, v in zip(named_ranges.keys(), ranges)}
            return result
        return None
    
    @staticmethod
    def _parse_value_range(value_range:Optional[List[float]]=None,
                           nominal_value:Optional[float]=None):
        if value_range is not None:
            result = get_proper_ranges(value_range, nominal_value)
            if result.shape != (1, 2):
                raise ValueError("value range must be list of size 2")
            return result[0]
        return None
                                
    @classmethod
    def create(cls, name:str, title:Optional[str]=None,
               value:Optional[float]=None,
               range:Optional[List[float]]=None,
               named_ranges:Optional[Dict[str, List[float]]]=None,
               nbins:Optional[int]=None, unit:Optional[str]=None):
        instance = cls()
        kwargs = {
                    "name" : name,
                   "title" : title,
                   "value" : value,
                   "range" : range,
            "named_ranges" : named_ranges,
                  "nbins"  : nbins,
                    "unit" : unit
        }
        instance.parse(kwargs)
        return instance
        
    def new(self) -> "ROOT.RooRealVar":
            
        if self.name is None:
            raise RuntimeError("object not initialized")
            
        ROOT = cached_import("ROOT")
        
        if self.title is not None:
            title = self.title
        else:
            title = self.name
        
        if (self.value is not None) and (self.range is not None):
            variable = ROOT.RooRealVar(self.name, title, self.value,
                                       self.range[0], self.range[1])
        elif (self.value is None) and (self.range is not None):
            variable = ROOT.RooRealVar(self.name, title,
                                       self.range[0], self.range[1])
        elif (self.value is not None) and (self.range is None):
            variable = ROOT.RooRealVar(self.name, title, self.value)
        else:
            variable = ROOT.RooRealVar(self.name, title, 0.)
            
        if self.named_ranges is not None:
            for name, _range in self.named_ranges.items():
                variable.setRange(name, _range[0], _range[1])            
        
        if self.nbins is not None:
            variable.setBins(self.nbins)
            
        if self.unit is not None:
            variable.setUnit(self.unit)
        ROOT.SetOwnership(variable, False)
        return variable

    def to_root(self) -> "ROOT.RooRealVar":
        return self.new()
        
    @semistaticmethod
    def get_bin_widths(self, obj:"ROOT.RooRealVar") -> np.ndarray:
        ROOT = cached_import("ROOT")
        c_vector = ROOT.RFUtils.GetRooRealVarBinWidths(obj)
        return TArrayData.vec_to_array(c_vector)
    
    @semistaticmethod
    def get_binning(self, obj:"ROOT.RooRealVar") -> Binning:
        binning = obj.getBinning()
        boundaries = binning.array()
        num_boundaries = binning.numBoundaries()
        from quickstats.interface.cppyy.vectorize import c_array_to_np_array
        from quickstats.maths.histograms import bin_edge_to_bin_center, bin_edge_to_bin_width
        bin_low_edge = c_array_to_np_array(boundaries, num_boundaries)
        binning = Binning(bins=bin_low_edge)
        return binning

    @semistaticmethod
    def get_default_value(self, obj:"ROOT.RooRealVar") -> float:
        temp = obj.getVal()
        obj.setBin(obj.getBins() - 1)
        result = obj.getVal()
        obj.setVal(temp)
        return result
    
    @staticmethod
    def at_boundary(obj:"ROOT.RooRealVar"):
        return cppyy.gbl.RFUtils.ParameterAtBoundary(obj)
    
    @staticmethod
    def close_to_min(obj:"ROOT.RooRealVar", threshold:float=0.1):
        return cppyy.gbl.RFUtils.ParameterCloseToMin(obj, threshold)

    @staticmethod
    def close_to_max(obj:"ROOT.RooRealVar", threshold:float=0.1):
        return cppyy.gbl.RFUtils.ParameterCloseToMax(obj, threshold)
    
    @staticmethod
    def close_to_boundary(obj:"ROOT.RooRealVar", threshold:float=0.1):
        return cppyy.gbl.RFUtils.ParameterCloseToBoundary(obj, threshold)