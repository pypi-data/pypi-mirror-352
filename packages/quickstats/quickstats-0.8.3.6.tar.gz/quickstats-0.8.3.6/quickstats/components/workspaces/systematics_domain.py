from typing import Optional, Union, List, Dict

import ROOT

from quickstats.interface.cppyy.vectorize import list2vec

from .systematic import Systematic
from .settings import RESPONSE_PREFIX, GLOBALOBS_PREFIX, CONSTRTERM_PREFIX

# basic data structure for systematic domain
# all the systematics under the same systematic domain will be merged into one response function          
class SystematicsDomain:
    
    def __init__(
        self,
        domain:str,
        use_piecewise_interp:bool=True
    ):
        self.domain = domain
        self.use_piecewise_interp = use_piecewise_interp
        self.is_shape = None
        self.nominal_var = None
        self.nuis_list = ROOT.RooArgList()
        self.prod_nuis_list = ROOT.RooArgList()
        self.nominal_list = []
        self.uncert_hi_list = ROOT.RooArgList()
        self.uncert_lo_list = ROOT.RooArgList()
        self.interp_code_list = []
        self.constr_term_list = []
        
    def get_response_name(self) -> str:
        return f"{RESPONSE_PREFIX}{self.domain}"

    def get_nominal_var_name(self) -> str:
        return f"{RESPONSE_PREFIX}{self.domain}_nominal"

    def get_syst_pi_name(self, response_name:str, syst_name: str) -> str:
        return f"{response_name}_{syst_name}_PI"

    def get_main_pi_name(self, response_name:str) -> str:
        return f"{response_name}_main_PI"
        
    def decompose(self):
        components = {
            'linear': {
                'nuis': ROOT.RooArgList(),
                'uncert_lo': ROOT.RooArgList(),
                'uncert_hi': ROOT.RooArgList(),
                'code': []
            },
            'exponential': {
                'nuis': ROOT.RooArgList(),
                'uncert_lo': ROOT.RooArgList(),
                'uncert_hi': ROOT.RooArgList(),
                'code': []                
            }
        }
        nuis_list = self.nuis_list if not self.prod_nuis_list.size() else self.prod_nuis_list
        for i in range(nuis_list.size()):
            code = self.interp_code_list[i]
            if code == 0:
                component = components['linear']
            else:
                component = components['exponential']
            component['nuis'].add(nuis_list[i])
            component['uncert_lo'].add(self.uncert_lo_list[i])
            component['uncert_hi'].add(self.uncert_hi_list[i])
            component['code'].append(code)
        return components                
        
    def get_response_function(self):
        resp_name = self.get_response_name()
        if self.use_piecewise_interp:
            if not self.nominal_var:
                raise RuntimeError(
                    'Failed to create PiecewiseInterpolation function. '
                    'Nominal variable is not defined.'
                )
            resp_func = ROOT.RooProduct(resp_name, resp_name, ROOT.RooArgList())
            components = self.decompose()
            # linear components needs separate PI functions at the moment
            linear_components = components['linear']
            for i in range(linear_components['nuis'].size()):
                nuis = linear_components['nuis'][i]
                uncert_lo = linear_components['uncert_lo'][i]
                uncert_hi = linear_components['uncert_hi'][i]
                code = linear_components['code'][i]
                syst_pi_name = self.get_syst_pi_name(resp_name, nuis.GetName())
                syst_pi = ROOT.PiecewiseInterpolation(
                    syst_pi_name,
                    syst_pi_name,
                    self.nominal_var,
                    ROOT.RooArgList(uncert_lo),
                    ROOT.RooArgList(uncert_hi),
                    ROOT.RooArgList(nuis)
                )
                syst_pi.setPositiveDefinite(False)
                syst_pi.setAllInterpCodes(code)
                resp_func.addTerm(syst_pi.Clone())
            
            # construct main PiecewiseInterpolation function
            exp_components = components['exponential']
            if exp_components['nuis'].size() > 0:
                main_pi_name = self.get_main_pi_name(resp_name)
                main_pi = ROOT.PiecewiseInterpolation(
                    main_pi_name,
                    main_pi_name,
                    self.nominal_var,
                    exp_components['uncert_lo'],
                    exp_components['uncert_hi'],
                    exp_components['nuis']
                )
                main_pi.setPositiveDefinite(False)
                for i in range(exp_components['nuis'].size()):
                    main_pi.setInterpCode(exp_components['nuis'].at(i), exp_components['code'][i])
                resp_func.addTerm(main_pi.Clone())
        else:
            if not getattr(ROOT, "ResponseFunction"):
                raise RuntimeError("ResponseFunction class undefined: may be you need to load the corresponding macro...")
            nominal_list = list2vec(self.nominal_list)
            interp_code_list = list2vec(self.interp_code_list)
            resp_func = ROOT.ResponseFunction(resp_name, resp_name, self.nuis_list, nominal_list,
                                              self.uncert_lo_list, self.uncert_hi_list,
                                              interp_code_list)
        return resp_func
    
    def get_np_glob_constr_names(self, idx:int):
        if idx >= self.nuis_list.size():
            raise RuntimeError("index out of range")
        np = self.nuis_list.at(idx)
        np_name = np.GetName()
        glob_name = f"{GLOBALOBS_PREFIX}{np_name}"
        constr_name = f"{CONSTRTERM_PREFIX}{np_name}"
        return np_name, glob_name, constr_name

    def set_nominal_var(self, var: ROOT.RooRealVar):
        self.nominal_var = var
    
    def add_item(self, nuis:ROOT.RooRealVar, nominal:float, uncert_hi:ROOT.RooRealVar,
                 uncert_lo:ROOT.RooRealVar, interp_code:int, constr_term:str,
                 prod_nuis: Optional[ROOT.RooAbsArg] = None):
        self.nuis_list.add(nuis)
        self.nominal_list.append(nominal)
        self.uncert_hi_list.add(uncert_hi)
        self.uncert_lo_list.add(uncert_lo)
        self.interp_code_list.append(interp_code)
        self.constr_term_list.append(constr_term)
        if prod_nuis is not None:
            self.prod_nuis_list.add(prod_nuis)