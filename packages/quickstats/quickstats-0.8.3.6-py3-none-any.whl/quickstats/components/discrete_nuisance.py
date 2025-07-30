##################################################################################################
# Based on https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
from typing import List, Optional, Union, Dict

import numpy as np

from quickstats import semistaticmethod, AbstractObject, cached_import
from quickstats.interface.root import RooArgSet
from quickstats.utils.common_utils import combine_dict

class DiscreteNuisance(AbstractObject):
    
    _DEFAULT_CONFIG_ = {
        "disc_set_keyword": "discreteParams"
    }
    
    @property
    def multipdf_cats(self):
        return self._multipdf_cats
    
    @property
    def multipdf_params(self):
        return self._multipdf_params

    @property
    def all_params(self):
        return self._all_params
    
    @property
    def multipdfs(self):
        return self._multipdfs

    @property
    def freeze_flag(self):
        return self._freeze_flag
    
    def __init__(self, ws:Optional["ROOT.RooWorkspace"]=None,
                 pdf:Optional["ROOT.RooWorkspace"]=None,
                 config:Optional[Dict]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)        
        self.config = combine_dict(self._DEFAULT_CONFIG_, config)
        self.initialize(ws, pdf)
    
    @semistaticmethod
    def extract_discrete_variables(self, ws:"ROOT.RooWorkspace", pdf:"ROOT.RooAbsPdf",
                                   keyword:Optional[str]=None):
        ROOT = cached_import("ROOT")
        all_cats = ws.allCats().Clone()
        if pdf.InheritsFrom("RooSimultaneous"):
            index_cat = pdf.indexCat()
            if index_cat in all_cats:
                all_cats.remove(index_cat)
        if not all_cats:
            return ROOT.RooArgList(), ROOT.RooArgList(), ROOT.RooArgSet()
        if (keyword is not None) and ws.genobj(keyword):
            disc_obj = ws.genobj(keyword)
            # sanity check
            if not isinstance(disc_obj, ROOT.RooArgSet):
                raise RuntimeError(f'discrete parameter container "{keyword}" is not an instance of RooArgSet')
            disc_cats = RooArgSet.select_by_class(disc_obj, 'RooCategory')
            if len(disc_cats) != len(disc_obj):
                raise RuntimeError(f'discrete parameter set "{keyword}" contain instance(s) other than RooCategory')
        else:
            disc_cats = all_cats
        all_pdfs = ws.allPdfs()
        disc_pdfs = RooArgSet.select_by_class(all_pdfs, 'RooMultiPdf')
        if not disc_pdfs:
            return ROOT.RooArgList(), ROOT.RooArgList(), ROOT.RooArgSet()
        dpd_disc_cats = RooArgSet.select_dependent_parameters(disc_cats, pdf)
        dpd_disc_pdfs = RooArgSet.select_dependent_parameters(disc_pdfs, pdf)
        if len(dpd_disc_cats) != len(dpd_disc_pdfs):
            raise RuntimeError('mismatch between number of discrete categories and number of multi pdfs')
        valid_disc_cats = ROOT.RooArgList()
        valid_disc_pdfs = ROOT.RooArgList()
        valid_disc_params = ROOT.RooArgSet()

        for cat in dpd_disc_cats:
            clients = ROOT.RooArgSet()
            # avoid warning when multiple objects with same name is in clients
            for client in cat.clients():
                if client not in clients:
                    clients.add(client)
            candidate_pdfs = dpd_disc_pdfs.selectCommon(clients)
            if len(candidate_pdfs) == 1:
                valid_disc_cats.add(cat)
                valid_disc_pdfs.add(candidate_pdfs)
            elif len(candidate_pdfs) == 0:
                raise RuntimeError(f'failed to find multi pdf associated with the category "{cat.GetName()}"')
            else:
                raise RuntimeError(f'failed to more than one multi pdfs associated with the category "{cat.GetName()}": '
                                   f'{", ".join([pdf.GetName() for pdf in candidate_pdfs])}')
            disc_pdf = candidate_pdfs.first()
            disc_params = disc_pdf.getParameters(0)
            disc_params = RooArgSet.select_by_class(disc_params, 'RooRealVar')
            ROOT.RooStats.RemoveConstantParameters(disc_params)
            valid_disc_params.add(disc_params)
        return valid_disc_cats, valid_disc_pdfs, valid_disc_params
    
    def initialize(self, ws:"ROOT.RooWorkspace", pdf:"ROOT.RooAbsPdf"):
        ROOT = cached_import("ROOT")
        if (ws is None) and (pdf is None):
            self._multipdf_cats = ROOT.RooArgList()
            self._multipdfs = ROOT.RooArgList()
            self._multipdf_params = ROOT.RooArgSet()
            self._all_params = ROOT.RooArgSet()
            self._freeze_flag = False
            return
        disc_set_keyword = self.config['disc_set_keyword']
        disc_cats, disc_pdfs, disc_params = self.extract_discrete_variables(ws, pdf, disc_set_keyword)
        if disc_cats:
            n_disc_cats = len(disc_cats)
            self.stdout.info(f'Found {n_disc_cats} discrete nuisances.')
        else:
            self.stdout.info('No discrete nuisances found.')
        
        self._multipdf_cats = disc_cats
        self._multipdfs = disc_pdfs
        self._multipdf_params = disc_params
        self._all_params = ws.allVars()
        self._freeze_flag = True
        
        self.print_active_pdf_summary()
        
    def has_discrete_nuisance(self):
        return len(self.multipdfs) > 0
    
    def print_active_pdf_summary(self):
        if not self.has_discrete_nuisance():
            return
        self.stdout.info('Summary of multipdfs and their corresponding active pdfs:')
        for multipdf, multipdf_cat in zip(self.multipdfs, self.multipdf_cats):
            multipdf_name = multipdf.GetName()
            current_pdf = multipdf.getCurrentPdf()
            current_pdf_name = current_pdf.GetName()
            current_index = multipdf_cat.getCurrentIndex()
            self.stdout.info(f'    {multipdf_name} -> {current_pdf_name} (index = {current_index})', bare=True)
            
    def set_freeze_flag(self, flag:bool=True):
        self._freeze_flag = flag
    
    def freeze_discrete_params(self, freeze:bool=True):
        ROOT = cached_import("ROOT")
        if (not self.has_discrete_nuisance()) or (not self.freeze_flag):
            return None
        multipdfs       = self.multipdfs
        multipdf_params = ROOT.RooArgSet(self.multipdf_params)
        # For each multiPdf, get the active pdf and remove its parameters
        # from this list of params and then freeze the remaining ones
        for multipdf in multipdfs:
            current_pdf = multipdf.getCurrentPdf()
            pdf_params = current_pdf.getParameters(0)
        for multipdf, multipdf_cat in zip(self.multipdfs, self.multipdf_cats):
            if not multipdf_cat.isConstant():
                current_pdf = multipdf.getCurrentPdf()
                pdf_params = current_pdf.getParameters(0)
                ROOT.RooStats.RemoveConstantParameters(pdf_params)
                multipdf_params.remove(pdf_params)
        num_params = len(multipdf_params)
        if freeze:
            self.stdout.debug(f'Freezing {num_params} disassociated multipdf parameters.')
        else:
            self.stdout.debug(f'Unfreezing {num_params} disassociated multipdf parameters.')
        if self.stdout.verbosity <= "DEBUG":
            multipdf_params.Print("V")
        RooArgSet.set_constant_state(multipdf_params, freeze)

    def get_default_pdf_indices(self):
        return np.zeros(len(self.multipdf_cats))

    def get_current_pdf_indices(self):
        return np.array([cat.getCurrentIndex() for cat in self.multipdf_cats])

    def get_pdf_sizes(self):
        return np.array([len(cat) for cat in self.multipdf_cats])

    def get_n_orthogonal_combination(self):
        pdf_sizes = self.get_pdf_sizes()
        return np.sum(pdf_sizes) - len(pdf_sizes) + 1

    def get_n_combination(self, contributing_indices:Optional[List[np.ndarray]]=None):
        if contributing_indices is None:
            return np.prod(self.get_pdf_sizes())
        return np.prod([np.sum(indices, dtype=int) for indices in contributing_indices])
        
    def get_orthogonal_combinations(self):
        pdf_sizes = self.get_pdf_sizes()
        n_pdf = len(pdf_sizes)
        combinations = np.zeros((np.sum(pdf_sizes) - n_pdf + 1, n_pdf), dtype=np.int32)
        start_idx = 1
        for i, size in enumerate(pdf_sizes):
            combinations[start_idx:start_idx + size - 1, i] = np.arange(1, size, dtype=np.int32)
            start_idx += (size - 1)
        return combinations

    def get_total_combinations(self, contributing_indices:Optional[List[np.ndarray]]=None):
        pdf_sizes = self.get_pdf_sizes()
        if contributing_indices is None:
            grid_points = [np.arange(size, dtype=np.int32) for size in pdf_sizes]
        else:
            grid_points = [np.arange(size, dtype=np.int32)[np.array(contributing_indices[i], dtype=bool)] for i, size in enumerate(pdf_sizes)]
        combinations = np.array(np.meshgrid(*grid_points)).T.reshape(-1, len(pdf_sizes))
        return combinations
        
    def reorder_combinations(self, combinations:np.ndarray, reference_indices:np.ndarray):
        pdf_sizes = self.get_pdf_sizes()
        return (combinations + reference_indices) % pdf_sizes
        
    def create_contributing_indices(self):
        return [np.ones(size) for size in self.get_pdf_sizes()]

    def filter_combinations(self, combinations, contributing_indices:Optional[List[np.ndarray]]=None):
        if contributing_indices is None:
            return combinations
        if np.all(contributing_indices == 1):
            return combinations
        pdf_sizes = self.get_pdf_sizes()
        n_pdf = len(pdf_sizes)
        max_size = np.max(pdf_sizes)
        regular_array = np.zeros((len(pdf_sizes), max_size))
        for i in range(n_pdf):
            regular_array[i, 0 : pdf_sizes[i]] = contributing_indices[i]
        valid_idx = np.where(np.choose(combinations, regular_array.T).sum(axis=1) == n_pdf)
        return combinations[valid_idx]

    def float_all_cats(self):
        RooArgSet.set_constant_state(self.multipdf_cats, False)

    def fix_non_target_cats(self, target_index:int):
        if target_index < 0:
            RooArgSet.set_constant_state(self.multipdf_cats, False)
        else:
            RooArgSet.set_constant_state(self.multipdf_cats, True)
            self.multipdf_cats.at(target_index).setConstant(False)

    def set_category_indices(self, indices:np.ndarray):
        return RooArgSet.set_category_indices(self.multipdf_cats, indices)