import array
import numpy as np

from quickstats import semistaticmethod, cached_import
from quickstats.interface.root import TObject, TArrayData
from quickstats.interface.cppyy.vectorize import c_array_to_np_array

class TH3(TObject):

    """
    Note: bin content are stored in row-major order with shape (nbins_z, nbins_y, nbins_x)
    """
    DTYPE_MAP = {
        "TH3I": "int",
        "TH3F": "float",
        "TH3D": "double"
    }
    
    def __init__(self, h:"ROOT.TH3", underflow_bin:bool=False, overflow_bin:bool=False):
        ROOT = cached_import("ROOT")
        dtype_map = {
            ROOT.TH3I: "int",
            ROOT.TH3F: "float",
            ROOT.TH3D: "double"
        }
        self.dtype = dtype_map.get(type(h), "double")
        self.underflow_bin = underflow_bin
        self.overflow_bin  = overflow_bin
        self.init(h)
        
    def get_fundamental_type(self):
        ROOT = cached_import("ROOT")
        return ROOT.TH3
        
    def init(self, h):
        self.bin_content    = self.GetBinContentArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.x_bin_center   = self.GetXBinCenterArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.y_bin_center   = self.GetYBinCenterArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.z_bin_center   = self.GetZBinCenterArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.x_bin_width    = self.GetXBinWidthArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.y_bin_width    = self.GetYBinWidthArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.z_bin_width    = self.GetZBinWidthArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.x_bin_low_edge = self.GetXBinLowEdgeArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.y_bin_low_edge = self.GetYBinLowEdgeArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.z_bin_low_edge = self.GetZBinLowEdgeArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        
    @staticmethod
    def GetBinContentArray(h, dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        arr = h.GetArray()
        # account for underflow and overflow bins
        nbins_x = h.GetNbinsX() + 2
        nbins_y = h.GetNbinsY() + 2
        nbins_z = h.GetNbinsZ() + 2
        size = nbins_x * nbins_y * nbins_z
        np_arr = c_array_to_np_array(arr, size=size)
        np_arr = np_arr.reshape((nbins_z, nbins_y, nbins_x), order='C')
        x_start = 1 if not underflow_bin else 0
        y_start = x_start
        z_start = x_start
        x_end = -1 if not overflow_bin else nbins_x
        y_end = -1 if not overflow_bin else nbins_y
        z_end = -1 if not overflow_bin else nbins_z
        np_arr = np_arr[z_start:z_end, y_start:y_end, x_start:x_end]
        return np_arr
    
    @staticmethod
    def GetXLabelArray(h:"ROOT.TH3"):
        return np.array(h.GetXaxis().GetLabels(), dtype=str)
    
    @staticmethod
    def GetYLabelArray(h:"ROOT.TH3"):
        return np.array(h.GetYaxis().GetLabels(), dtype=str)
    
    @staticmethod
    def GetZLabelArray(h:"ROOT.TH3"):
        return np.array(h.GetYaxis().GetLabels(), dtype=str)
    
    @staticmethod
    def GetAxisBinCenterArray(ax:"ROOT.TAxis", dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TAxisUtils.GetBinCenterArray[dtype](ax, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)
    
    @staticmethod
    def GetAxisBinWidthArray(ax:"ROOT.TAxis", dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TAxisUtils.GetBinWidthArray[dtype](ax, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetAxisBinLowEdgeArray(ax:"ROOT.TAxis", dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        ROOT = cached_import("ROOT")
        c_vector = ROOT.TAxisUtils.GetBinLowEdgeArray[dtype](ax, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetXBinCenterArray(h:"ROOT.TH3", dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH3.GetAxisBinCenterArray(h.GetXaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetYBinCenterArray(h:"ROOT.TH3", dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH3.GetAxisBinCenterArray(h.GetYaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetZBinCenterArray(h:"ROOT.TH3", dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH3.GetAxisBinCenterArray(h.GetZaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetXBinWidthArray(h:"ROOT.TH3", dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH3.GetAxisBinWidthArray(h.GetXaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetYBinWidthArray(h:"ROOT.TH3", dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH3.GetAxisBinWidthArray(h.GetYaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetZBinWidthArray(h:"ROOT.TH3", dtype:str='double', underflow_bin:bool=False, overflow_bin:bool=False):
        return TH3.GetAxisBinWidthArray(h.GetZaxis(), dtype, underflow_bin, overflow_bin)

    @staticmethod
    def GetXBinLowEdgeArray(h:"ROOT.TH3", dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        return TH3.GetAxisBinLowEdgeArray(h.GetXaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetYBinLowEdgeArray(h:"ROOT.TH3", dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        return TH3.GetAxisBinLowEdgeArray(h.GetYaxis(), dtype, underflow_bin, overflow_bin)
    
    @staticmethod
    def GetZBinLowEdgeArray(h:"ROOT.TH3", dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        return TH3.GetAxisBinLowEdgeArray(h.GetZaxis(), dtype, underflow_bin, overflow_bin)