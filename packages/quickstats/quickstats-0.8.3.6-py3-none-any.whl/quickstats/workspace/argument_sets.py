from typing import Optional, Union, List, Dict

from quickstats import AbstractObject, cached_import
from quickstats.maths.numerics import is_float
from quickstats.workspace.settings import (
    OBS_SET,
    POI_SET,
    NUIS_SET,
    GLOB_SET,
    CONSTR_SET
)

class SystArgSets:
    
    def __init__(self):
        ROOT = cached_import('ROOT')
        self.constr_set = ROOT.RooArgSet()
        self.nuis_set   = ROOT.RooArgSet()
        self.glob_set   = ROOT.RooArgSet()
 
    def add(self, constr: "ROOT.RooAbsPdf", nuis: "ROOT.RooRealVar", glob: "ROOT.RooRealVar") -> None:
        if not constr:
            raise RuntimeError(f'Failed to add constraint pdf: null pointer found')
        if not nuis:
            raise RuntimeError(f'Failed to add nuisance parameter: null pointer found')
        if not glob:
            raise RuntimeError(f'Failed to add global observable: null pointer found')
        self.constr_set.add(constr, True)
        self.nuis_set.add(nuis, True)
        self.glob_set.add(glob, True)

    def merge(self, other: "SystArgSets") -> None:
        self.constr_set.add(other.constr_set, True)
        self.nuis_set.add(other.nuis_set, True)
        self.glob_set.add(other.glob_set, True)

class CoreArgSets:
    
    def __init__(self):
        ROOT = cached_import('ROOT')
        self.obs_set    = ROOT.RooArgSet()
        self.poi_set    = ROOT.RooArgSet()
        self.nuis_set   = ROOT.RooArgSet()
        self.glob_set   = ROOT.RooArgSet()
        self.constr_set = ROOT.RooArgSet()
        
    @property
    def obs_set_name(self) -> str:
        return OBS_SET

    @property
    def poi_set_name(self) -> str:
        return POI_SET

    @property
    def nuis_set_name(self) -> str:
        return NUIS_SET

    @property
    def glob_set_name(self) -> str:
        return GLOB_SET

    @property
    def constr_set_name(self) -> str:
        return CONSTR_SET

    @property
    def named_map(self) -> Dict[str, "ROOT.RooArgSet"]:
        result = {
            self.obs_set_name: self.obs_set,
            self.poi_set_name: self.poi_set,
            self.nuis_set_name: self.nuis_set,
            self.glob_set_name: self.glob_set
        }
        return result

    @classmethod
    def from_workspace(cls, ws: "ROOT.RooWorkspace") -> "Self":
        from quickstats.interface.cppyy import is_null_ptr
        argsets = cls()
        obs_set = ws.set(OBS_SET)
        if not obs_set:
            raise RuntimeError(f'Observable set "{OBS_SET}" not defined '
                               f'in workspace "{ws.GetName()}".')
        poi_set = ws.set(POI_SET)
        if (not poi_set) and is_null_ptr(poi_set):
            raise RuntimeError(f'POI set "{POI_SET}" not defined '
                               f'in workspace "{ws.GetName()}".')
        nuis_set = ws.set(NUIS_SET)
        if (not nuis_set) and is_null_ptr(nuis_set):
            raise RuntimeError(f'NP set "{NUIS_SET}" not defined '
                               f'in workspace "{ws.GetName()}".')
        glob_set = ws.set(GLOB_SET)
        if (not glob_set) and is_null_ptr(glob_set):
            raise RuntimeError(f'Global observable set "{GLOB_SET}" '
                               f'not defined in workspace "{ws.GetName()}".')
        argsets.obs_set = obs_set
        argsets.poi_set = poi_set
        argsets.nuis_set = nuis_set
        argsets.glob_set = glob_set
        return argsets

    def sanity_check(self):
        if self.obs_set.size() == 0:
            raise RuntimeError('Observable set not initialized.')
        #if self.poi_set.size() == 0:
        #    raise RuntimeError('POI set not initialized.')

    def add_syst_argsets(self, syst_argsets: SystArgSets) -> None:
        self.nuis_set.add(syst_argsets.nuis_set, True)
        self.glob_set.add(syst_argsets.glob_set, True)
        self.constr_set.add(syst_argsets.constr_set, True)

    def merge(self, other: "CoreArgSets") -> None:
        self.obs_set.add(other.obs_set, True)
        self.poi_set.add(other.poi_set, True)
        self.constr_set.add(other.constr_set, True)
        self.nuis_set.add(other.nuis_set, True)
        self.glob_set.add(other.glob_set, True)    

    def set_modelconfig(self, mc: "ROOT.RooStats.ModelConfig") -> None:
        named_map = self.named_map
        mc.SetObservables(named_map[self.obs_set_name])
        mc.SetParametersOfInterest(named_map[self.poi_set_name])
        mc.SetNuisanceParameters(named_map[self.nuis_set_name])
        mc.SetGlobalObservables(named_map[self.glob_set_name])