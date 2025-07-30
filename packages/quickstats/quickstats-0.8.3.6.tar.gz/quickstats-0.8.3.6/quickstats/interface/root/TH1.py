from typing import Optional, Tuple, List, Dict, Union
from quickstats.core.typing import ArrayLike
import uuid
import array
import numpy as np

from quickstats import cached_import
from quickstats.concepts import Histogram1D
from quickstats.maths.histograms import (get_hist_mean, get_hist_mean_error,
                                         get_hist_std, get_cumul_hist, histogram,
                                         bin_edge_to_bin_center,
                                         bin_center_to_bin_edge)
from quickstats.interface.root import TObject, TArrayData
from quickstats.interface.root import load_macro
from quickstats.interface.cppyy.vectorize import as_vector, as_np_array, as_c_array, np_type_str_maps

class TH1(TObject):
    
    def __init__(self, h:Optional["ROOT.TH1"]=None, dtype:str='double', 
                 underflow_bin:int=0,
                 overflow_bin:int=0):
        self.dtype = dtype
        self.underflow_bin = underflow_bin
        self.overflow_bin  = overflow_bin
        self.init(h)
        
    def get_fundamental_type(self):
        ROOT = cached_import("ROOT")
        return ROOT.TH1
    
    def sanity_check(self):
        if any(attribute is None for attribute in [self.bin_content, self.bin_error, self.bin_center,
                                                   self.bin_width, self.bin_low_edge]):
            raise RuntimeError("histogram not initialized")
        
    def init(self, h:Optional["ROOT.TH1"]=None):
        if h is not None:
            self.bin_content  = self.GetBinContentArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
            self.bin_error    = self.GetBinErrorArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
            self.bin_center   = self.GetBinCenterArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
            self.bin_width    = self.GetBinWidthArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
            self.bin_low_edge = self.GetBinLowEdgeArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        else:
            self.bin_content = None
            self.bin_error = None
            self.bin_center = None
            self.bin_width = None
            self.bin_low_edge = None
    
    @classmethod
    def from_numpy_data(cls, x:np.ndarray, weights:Optional[np.ndarray]=None,
                        bins:ArrayLike=10,
                        bin_range:ArrayLike=None,
                        normalize:bool=False,
                        **kwargs):
        bin_content, bin_edges, bin_error = histogram(x, weights=weights,
                                                      bins=bins, bin_range=bin_range,
                                                      normalize=normalize, clip_weight=True,
                                                      evaluate_error=True,
                                                      error_mode='sumw2')
        instance = cls.from_numpy_histogram(bin_content, bin_edges,
                                            bin_error=bin_error,
                                            **kwargs)
        return instance
    
    @classmethod
    def from_numpy_histogram(cls, bin_content:np.ndarray,
                             bin_edges:np.ndarray,
                             bin_error:Optional[np.ndarray]=None,
                             **kwargs):
        assert (bin_content.ndim == 1) and (bin_edges.ndim == 1)
        instance = TH1(**kwargs)
        instance.bin_content = np.array(bin_content)
        if bin_error is None:
            instance.bin_error = np.zeros(instance.bin_content.shape)
        else:
            bin_error = np.array(bin_error)
            assert bin_error.shape == instance.bin_content.shape
            instance.bin_error = bin_error
        instance.bin_low_edge = np.array(bin_edges)
        instance.bin_center = bin_edge_to_bin_center(instance.bin_low_edge)
        instance.bin_width = np.diff(instance.bin_low_edge)
        return instance
        
    @staticmethod
    def _to_ROOT(name:str, bin_content, bin_width=None, bin_center=None, bin_low_edge=None,
                 bin_error=None, title:str=None):
        ROOT = cached_import("ROOT")
        if ((bin_low_edge is None) and (bin_center is None)) or \
           ((bin_low_edge is not None) and (bin_center is not None)):
            raise ValueError("must provide either bin low edge or bin center values")
        if bin_center is not None:
            bin_low_edge = bin_center_to_bin_edge(bin_center)
        bin_low_edge = np.array(bin_low_edge)
        nbins = len(bin_low_edge) - 1
        title = title or name
        dtype = bin_content.dtype
        if np_type_str_maps[dtype] == "float":
            h_func = ROOT.TH1F
        elif np_type_str_maps[dtype] == "float":
            h_func = ROOT.TH1D
        else:
            bin_low_edge = bin_low_edge.astype('double')
            h_func = ROOT.TH1D
            
        h = h_func(name, title, nbins, as_c_array(bin_low_edge))
        if bin_error is None:
            bin_error = np.zeros((nbins,))
        for i in range(nbins):
            h.SetBinContent(i + 1, bin_content[i])
            h.SetBinError(i + 1, bin_error[i])
        return h
    
    def to_ROOT(self, name:str, title:str=None):
        self.sanity_check()
        return self._to_ROOT(name, self.bin_content, bin_low_edge=self.bin_low_edge,
                             bin_error=self.bin_error, title=title)

    def to_histogram(self):
        return Histogram1D(
            bin_content=self.bin_content,
            bin_edges=self.bin_low_edge,
            bin_errors=self.bin_error
        )
    
    @staticmethod
    def find_bin_by_edge(h:"ROOT.TH1", low_edge:float, tol:float=1e-6):
        ROOT = cached_import("ROOT")
        return ROOT.TH1Utils.FindBinIndexByBinEdge(h, low_edge, tol)
    
    @staticmethod
    def find_binnings_relative_to_variable(h:"ROOT.TH1", variable:"ROOT.RooRealVar", tol:float=1e-6):
        vmin, vmax = variable.getMin(), variable.getMax()
        bin_low  = TH1.find_bin_by_edge(h, vmin, tol=tol)
        bin_high = TH1.find_bin_by_edge(h, vmax, tol=tol)
        nbins   = bin_high - bin_low
        return bin_low, bin_high, nbins
    
    
    @staticmethod
    def rebin_to_variable(h:"ROOT.TH1", variable:"ROOT.RooRealVar", tol:float=1e-6):
        bin_low, bin_high, nbins = TH1.find_binnings_relative_to_variable(h, variable, tol=tol)
        var_nbins = variable.getBins()
        if nbins != var_nbins:
            histname = h.GetName()
            varname = variable.GetName()
            if nbins == 0:
                raise RuntimeError(f"Input histogram `{histname}` has 0 bins in the "
                                   f"range defined by the variable `{varname}`."
                                   f"Please check compatibility between your "
                                   f"variable and the histogram range")
            if (nbins < var_nbins):
                raise RuntimeError(f"input histogram `{histname}` has fewer bins "
                                   f"({nbins}) than the variable `{varname}` "
                                   f"({var_nbins})")
            if (nbins > var_nbins) and (nbins % var_nbins != 0):
                raise RuntimeError(f"input histogram `{histname}` has inconsistent "
                                   f"number of bins ({nbins}) with the "
                                   f"variable `{varname}` ({var_nbins})")
            else:
                ratio = nbins // var_nbins
                h.Rebin(ratio)
                return ratio
        return 1
    
    @staticmethod
    def copy_histogram_in_effective_range(source:"ROOT.TH1", target:"ROOT.TH1",
                                          tol:float=1e-6, weight_scale:float=1):
        source_bin_edges = TH1.GetBinLowEdgeArray(source)
        target_bin_edges = TH1.GetBinLowEdgeArray(target)
        idx_first = np.where(np.abs(source_bin_edges - target_bin_edges[0]) < tol)[0]
        idx_last = np.where(np.abs(source_bin_edges - target_bin_edges[-1]) < tol)[0]
        if (((not len(idx_first)) or (not len(idx_last))) or 
            (not np.allclose(source_bin_edges[idx_first[0]:idx_last[0]+1], target_bin_edges, atol=tol))):
            raise RuntimeError("binnings of the target histogram is not a subset of the "
                               "binnings of the source histogram")
        idx_first, idx_last = int(idx_first[0]), int(idx_last[0])
        nbins = target.GetNbinsX()
        for i in range(1, nbins + 1):
            bin_index = idx_first + i
            bin_content = source.GetBinContent(bin_index) * weight_scale
            bin_error = source.GetBinError(bin_index) * weight_scale
            target.SetBinContent(i, bin_content)
            target.SetBinError(i, bin_error)
    
    @staticmethod
    def apply_blind_range(h:"ROOT.TH1", blind_range:List[float]):
        assert len(blind_range) == 2
        nbins = h.GetNbinsX()
        for i in range(1, nbins + 1):
            bin_center = h.GetBinCenter(i)
            if (bin_center > blind_range[0]) and (bin_center < blind_range[1]):
                h.SetBinContent(i, 0)
    
    @staticmethod
    def remove_negative_bins(h:"ROOT.TH1"):
        py_h = TH1(h)
        neg_bin_indices = np.where(py_h.bin_content < 0.)
        neg_bin_values  = py_h.bin_content[neg_bin_indices]
        neg_bins = neg_bin_indices[0] + 1
        for i in neg_bins:
            # cast from np.int64 to int
            i = int(i)
            h.SetBinContent(i, 0)
            h.SetBinError(i, 0)
        return neg_bin_indices[0], neg_bin_values
    
    @staticmethod
    def GetBinContentArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TH1Utils.GetBinContentArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)        
        
    @staticmethod
    def GetBinErrorArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TH1Utils.GetBinErrorArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)
                     
    @staticmethod
    def GetBinErrorUpArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TH1Utils.GetBinErrorUpArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetBinErrorLowArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TH1Utils.GetBinErrorLowArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)                     

    @staticmethod
    def GetBinCenterArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TH1Utils.GetBinCenterArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)
    
    @staticmethod
    def GetBinWidthArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TH1Utils.GetBinWidthArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetBinLowEdgeArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TH1Utils.GetBinLowEdgeArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)
    
    @staticmethod
    def GetPoissonError(data:np.ndarray, nsigma: int = 1, offset: bool = True):
        ROOT = cached_import("ROOT")
        data = np.array(data)
        c_data = as_vector(data)
        c_result  = ROOT.THistUtils.GetPoissonError(c_data, nsigma, offset)
        result = as_np_array(c_result)
        data_size = data.shape[0]
        errlo, errhi = result[:data_size], result[data_size:]
        return errlo, errhi
        
    @staticmethod
    def add_ghost_weights(h:"ROOT.TH1",
                          blind_range:Optional[List[float]]=None,
                          ghost_weight:float=1e-9):
        nbins = h.GetNbinsX()
        for i in range(1, nbins + 1):
            if h.GetBinContent(i) != 0:
                continue
            bin_center = h.GetBinCenter(i)
            if blind_range and (bin_center > blind_range[0]) and (bin_center < blind_range[1]):
                continue
            h.SetBinContent(i, ghost_weight)
            
    def rebin(self, bins:Union[int, np.ndarray]=None):
        if isinstance(bins, int):
            bins = np.linspace(self.bin_low_edge[0], self.bin_low_edge[-1], bins + 1)
        h = self.to_ROOT('temp', 'temp')
        h_new = h.Rebin(bins.shape[0] - 1, 'temp_2', bins)
        self.init(h_new)
        # free memory
        h.Delete()
        h_new.Delete()
        
    def GetMean(self):
        return get_hist_mean(x=self.bin_center, y=self.bin_content)
    
    def GetMeanError(self):
        return get_hist_mean_error(x=self.bin_center,
                                   y=self.bin_content,
                                   yerr=self.bin_error)
    
    def GetStdDev(self):
        return get_hist_std(x=self.bin_center, y=self.bin_content)
    
    def GetCumulativeHist(self):
        bin_content, bin_error = get_cumul_hist(self.bin_content, self.bin_error)
        return self.from_numpy_histogram(bin_content=bin_content,
                                         bin_edges=self.bin_low_edge,
                                         bin_error=bin_error)

    @staticmethod
    def create_model(bins: ArrayLike=10,
                     bin_range: ArrayLike=None,
                     name: str='histo1d',
                     title: Optional[str]=None):
        ROOT = cached_import("ROOT")
        title = title or name
        # specify bin edges directly
        if np.ndim(bins) == 1:
            bins = np.array(bins)
            if np_type_str_maps[bins.dtype] not in ['float', 'double']:
                bins = bins.astype('double')
            model = ROOT.RDF.TH1DModel(name, title, len(bins) - 1,  as_c_array(bins))
        elif bin_range is None:
            model = ROOT.RDF.TH1DModel(name, title, bins, 0., 0.)
        else:
            xlow, xhigh = bin_range
            model = ROOT.RDF.TH1DModel(name, title, bins, xlow, xhigh)
        return model