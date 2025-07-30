##################################################################################################
# Based on https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
from typing import Optional, Union

import cppyy

from quickstats import semistaticmethod, AbstractObject
from quickstats.interface.cppyy import cpp_define

class CachingNLLWrapper(AbstractObject):
    """
        Dedicated wrapper for the CachingSimNLL class from CMS
    """

    @property
    def nll(self):
        return self._nll

    def __init__(self, nll:Optional["ROOT.RooAbsReal"]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.set_nll(nll)

    @semistaticmethod
    def is_defined_class(self):
        return hasattr(cppyy.gbl, 'cacheutils::CachingSimNLL')

    @semistaticmethod
    def define_cast_function(self):
        if not self.is_defined_class():
            return None
        expr = 'cacheutils::CachingSimNLL * castAsCachingSimNLL(RooAbsReal* nll){ return dynamic_cast<cacheutils::CachingSimNLL *>(nll);}'
        status = cpp_define(expr, 'CachingNLLWrapperMethod')
        return status
        
    def set_nll(self, nll:Optional["ROOT.RooAbsReal"]=None):
        if (nll is None) or (not self.is_defined_class()):
            self._nll = None
            return None
        if not hasattr(cppyy.gbl, 'castAsCachingSimNLL'):
            self.define_cast_function()
        caching_nll = cppyy.gbl.castAsCachingSimNLL(nll)
        if caching_nll:
            self._nll = caching_nll
        else:
            self._nll = None

    def set_zero_point(self):
        """Offset the current NLL value to zero
        """
        if self.nll is None:
            return None
        self.stdout.debug(f'Setting zero point for the caching NLL: {self.nll.GetName()}')
        self.nll.setZeroPoint()

    def update_zero_point(self):
        """Update offset value of the current NLL
        """
        if self.nll is None:
            return None
        self.stdout.debug(f'Updating zero point for the caching NLL: {self.nll.GetName()}')
        self.nll.updateZeroPoint()

    def clear_zero_point(self):
        """Remove offset value of the current NLL
        """
        if self.nll is None:
            return None
        self.stdout.debug(f'Clearing zero point for the caching NLL: {self.nll.GetName()}')
        self.nll.clearZeroPoint()

    def set_hide_categories(self, value:bool=True):
        if self.nll is None:
            return None
        self.nll.setHideRooCategories(value)

    def set_mask_non_discrete_channels(self, value:bool=True):
        if self.nll is None:
            return None
        self.nll.setMaskNonDiscreteChannels(value)

    def set_hide_constants(self, value:bool=True):
        if self.nll is None:
            return None
        self.nll.setHideConstants(value)

    def set_mask_constraints(self, value:bool=True):
        if self.nll is None:
            return None
        self.nll.setMaskConstraints(value)