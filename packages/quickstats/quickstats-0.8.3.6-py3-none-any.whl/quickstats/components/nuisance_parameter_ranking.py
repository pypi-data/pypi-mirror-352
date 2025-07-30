##################################################################################################
# Based on https://gitlab.cern.ch/atlas-physics/stat/tools/StatisticsTools by Stefan Gadatsch
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
import os
import json
from typing import List, Optional, Union, Dict

import numpy as np

import quickstats
from quickstats import semistaticmethod, timer, cached_import
from . import AnalysisBase
from quickstats.utils import root_utils, common_utils, string_utils
from quickstats.utils.common_utils import combine_dict

class NuisanceParameterRanking(AnalysisBase):
    
    kBestFitSnapshotName = 'np_ranking_uncond_snapshot'
    
    def __init__(self, filename:str, poi_name:Optional[Union[str, List[str]]]=None,
                 data_name:Optional[str]=None, preset_param:bool=True,
                 verbosity:Optional[Union[int, str]]="INFO", **kwargs):
        super().__init__(filename=filename,
                         poi_name=poi_name,
                         data_name=data_name,
                         verbosity=verbosity,
                         preset_param=preset_param,
                         **kwargs)
        
    def preset_parameters(self):
        super().preset_parameters(fix_pois=False)
        self.model.set_parameters('<poi>=___0.15', mode='fix')
        
    def sanity_check(self):
        ROOT = cached_import("ROOT")
        if isinstance(self.poi, ROOT.RooArgSet) and len(self.poi) > 1:
            raise RuntimeError('Only single poi is allowed when evaluating pulls/ranking')
    
    def evaluate_pulls(self, nuis_name:str):
        ROOT = cached_import("ROOT")
        self.sanity_check()
        
        self.save_snapshot(self.kTempSnapshotName)
        
        has_poi = isinstance(self.poi, ROOT.RooRealVar)
        if has_poi:
            poi_name = self.poi.GetName()
            poi_nom  = self.poi.getVal()
            self.poi.setConstant(0)
        else:
            poi_name = None,
            poi_nom  = None
        
        nuis = self.model.get_var(nuis_name)
        nuis_name = nuis.GetName()
        nuis.setConstant(0)
        nuis_init = nuis.getVal()
        scan_set = ROOT.RooArgSet(nuis)
        
        self.stdout.info(f'Computing error for the NP "{nuis_name}" at {nuis_init}')
        self.stdout.info("Begin minimization")

        # evaluate postfit variation
        with timer() as t:
            status = self.minimizer.minimize(scan=1, scan_set=scan_set)
        time_uncond_fit = t.interval
        self.stdout.info(f'Minimization finished. Total time taken: {time_uncond_fit:.3f}s.')
           
        nuis_hat     = nuis.getVal()
        nuis_errhi   = nuis.getErrorHi()
        nuis_errlo   = nuis.getErrorLo()
        if has_poi:
            poi_hat  = self.poi.getVal()
        else:
            poi_hat  = None
        
        # evaluate prefit variation
        with timer() as t:
            all_constraints = self.model.get_all_constraints()
            prefit_variation, _, nuis_nom = self.model.inspect_constrained_nuisance_parameter(nuis, all_constraints)
        time_prefit_variation = t.interval
        self.stdout.info(f'Prefit variation extracted. Total time taken: {time_prefit_variation:.3f}s.')
            
        self.save_snapshot(self.kBestFitSnapshotName)
        
        summary_str = ""
        summary_str += f"         NP name : {nuis_name}\n"
        summary_str += f"   Nominal value : {nuis_nom:.5f}\n"
        summary_str += f"   Bestfit value : {nuis_hat:.5f}\n"
        summary_str += f" Lower variation : {nuis_errlo:.5f}\n"
        summary_str += f" Upper variation : {nuis_errhi:.5f}\n"
        summary_str += f"Prefit variation : {prefit_variation:.5f}\n"
        if has_poi:
            summary_str += f"        POI name : {poi_name}\n"
            summary_str += f"   Nominal value : {poi_nom:.5f}\n"
            summary_str += f"   Bestfit value : {poi_hat:.5f}\n"
        summary_str += f"      Fit status : {status}"
        self.stdout.info('Pull summary')
        self.stdout.info(summary_str, bare=True)
        
        result = {
            'nuis': {
                'name'            : nuis_name,
                'theta_0'         : nuis_nom,
                'theta_hat'       : nuis_hat,
                'theta_errlo'     : nuis_errlo,
                'theta_errhi'     : nuis_errhi,
                'theta_errprefit' : prefit_variation
            },
            'poi': {
                'name'   : poi_name,
                'mu_0'   : poi_nom,
                'mu_hat' : poi_hat
            },
            'fit_status' : {
                'uncond_fit': status
            },
            'time': {
                'uncond_fit': time_uncond_fit,
                'prefit_variation': time_prefit_variation
            }
        }
        
        self.load_snapshot(self.kTempSnapshotName)
        
        return result
    
    def _evaluate_poi_bestfit_with_cond_nuis(self, nuis:"ROOT.RooRealVar", nuis_val:float,
                                             snapshot_names:Optional[List[str]]=None):
        if not isinstance(snapshot_names, list):
            snapshot_names = list(snapshot_names)
        status = -1
        with timer() as t:
            for snapshot_name in snapshot_names:
                if snapshot_name is not None:
                    self.load_snapshot(snapshot_name)
                self.poi.setConstant(0)
                nuis.setVal(nuis_val)
                nuis.setConstant(1)
                status = self.minimizer.minimize()
                if (status >= 0):
                    break
        results = {
            'mu_hat'      : self.poi.getVal(),
            'fit_status'  : status,
            'time'        : t.interval
        }
        return results
    
    def evaluate_impact(self, pulls_data:Dict, prefit_impact:bool=True, postfit_impact:bool=True):
        ROOT = cached_import("ROOT")
        has_poi = isinstance(self.poi, ROOT.RooRealVar)
        if (not has_poi) or (pulls_data['poi']['name'] is None):
            self.stdout.warning('POI not set. No impact will be evaluated.')
            prefit_impact = False
            postfit_impact = False
        elif (self.poi.GetName() != pulls_data['poi']['name']):
            raise ValueError('POI mismatch')
        poi_name          = pulls_data['poi']['name']
        poi_hat           = pulls_data['poi']['mu_hat']
        nuis_name         = pulls_data['nuis']['name']
        nuis_hat          = pulls_data['nuis']['theta_hat']
        nuis_sigma_up     = pulls_data['nuis']['theta_errhi']
        nuis_sigma_down   = pulls_data['nuis']['theta_errlo']
        nuis_sigma_prefit = pulls_data['nuis']['theta_errprefit']
        nuis = self.model.get_var(nuis_name)
        
        self.save_snapshot(self.kTempSnapshotName)
        
        results = {}
        snapshot_names = [self.kTempSnapshotName, self.kBestFitSnapshotName]
        
        if postfit_impact:
            # fix theta at the MLE value +/- postfit uncertainty and minimize again to estimate the change in the POI
            self.stdout.info(f'Evaluating impact of moving NP up by one sigma postfit ({nuis_hat:.5f} + {abs(nuis_sigma_up):.5f})')
            result = self._evaluate_poi_bestfit_with_cond_nuis(nuis, nuis_hat + abs(nuis_sigma_up), snapshot_names)
            results['sigma_up_postfit'] = result
            self.stdout.info(f'Time to find postfit up impact: {result["time"]:.3f}s')
            self.stdout.info(f'Evaluating impact of moving NP down by one sigma postfit ({nuis_hat:.5f} - {abs(nuis_sigma_down):.5f})')
            result = self._evaluate_poi_bestfit_with_cond_nuis(nuis, nuis_hat - abs(nuis_sigma_down), snapshot_names)
            results['sigma_down_postfit'] = result
            self.stdout.info(f'Time to find postfit down impact: {result["time"]:.3f}s')
        
        if prefit_impact:
            # check if variable is a constrained NP
            constrained_nuis = self.model.get_constrained_nuisance_parameters(fmt='argset')
            if constrained_nuis.find(nuis_name):
                # fix theta at the MLE value +/- prefit uncertainty and minimize again to estimate the change in the POI
                self.stdout.info(f'Evaluating impact of moving NP up by one sigma prefit ({nuis_hat:.5f} + {abs(nuis_sigma_prefit):.5f})')
                result = self._evaluate_poi_bestfit_with_cond_nuis(nuis, nuis_hat + abs(nuis_sigma_prefit), snapshot_names)
                results['sigma_up_prefit'] = result
                self.stdout.info(f'Time to find prefit up impact: {result["time"]:.3f}s')
                self.stdout.info(f'Evaluating impact of moving NP down by one sigma prefit ({nuis_hat:.5f} - {abs(nuis_sigma_prefit):.5f})')
                result = self._evaluate_poi_bestfit_with_cond_nuis(nuis, nuis_hat - abs(nuis_sigma_prefit), snapshot_names)
                results['sigma_down_prefit'] = result
                self.stdout.info(f'Time to find prefit down impact: {result["time"]:.3f}s')
            else:
                self.stdout.warning(f'The nuisance parameter "{nuis_name}" is not constrained. No prefit impact '
                                    f'can be determined. The postfit impact is cloned instead (if available).')
                if 'sigma_up_postfit' in results:
                    results['sigma_up_prefit'] = combine_dict(results['sigma_up_postfit'])
                if 'sigma_down_postfit' in results:
                    results['sigma_down_prefit'] = combine_dict(results['sigma_down_postfit'])
        for key in results:
            results[key]['delta'] = results[key]['mu_hat'] - poi_hat
            
        values = {}
        for key in ['sigma_up_postfit', 'sigma_down_postfit', 'sigma_up_prefit', 'sigma_down_prefit']:
            if key in results:
                values[key] = results[key]['mu_hat']
            else:
                values[key] = '--'
                
        if results:
            self.stdout.info(f'Unconditional minimum of POI "{poi_name}": {poi_hat}')
            self.stdout.info(f'POI when varying NP up by one sigma postfit (prefit): {values["sigma_up_postfit"]:.5f} '
                             f'({values["sigma_up_prefit"]:.5f})')
            self.stdout.info(f'POI when varying NP down by one sigma postfit (prefit): {values["sigma_down_postfit"]:.5f} '
                             f'({values["sigma_down_prefit"]:.5f})')
        
        self.load_snapshot(self.kTempSnapshotName)
        
        return results
    
    def _get_merged_result(self, pulls_data:Dict, impact_data:Dict):
        merged_result = combine_dict(pulls_data)
        for key, label in [('sigma_up_postfit', 'up'), ('sigma_down_postfit', 'down'),
                           ('sigma_up_prefit', 'up_nom'), ('sigma_down_prefit', 'down_nom')]:
            if key in impact_data:
                merged_result['poi'][label] = impact_data[key]['mu_hat']
                merged_result['fit_status'][key] = impact_data[key]['fit_status']
                merged_result['time'][key] = impact_data[key]['time']
        return merged_result
    
    def evaluate_pulls_and_impact(self, nuis_name:str, prefit_impact:bool=True, postfit_impact:bool=True):
        pulls_data = self.evaluate_pulls(nuis_name)
        impact_data = self.evaluate_impact(pulls_data, prefit_impact=prefit_impact,
                                           postfit_impact=postfit_impact)
        merged_data = self._get_merged_result(pulls_data, impact_data)
        return merged_data
            
    def save_as_root(self, data:Dict, outname:str, treename:str='result'):
        ROOT = cached_import("ROOT")
        root_data = {}
        for k, v in data.items():
            buffer = {f'{k}_{kk}': vv for kk, vv in v.items()}
            root_data.update(buffer)
        dirname = os.path.dirname(outname)
        if dirname and (not os.path.exists(dirname)):
            os.makedirs(dirname)
        r_file = ROOT.TFile(outname, "RECREATE")
        r_tree = ROOT.TTree(treename, treename)
        root_utils.fill_branch(r_tree, root_data)
        r_file.Write()
        r_file.Close()
        self.stdout(f'INFO: Saved NP pulls and impact output to {outname}')
        
    @staticmethod
    def parse_root_result(filename):
        import uproot
        with uproot.open(filename) as file:
            result = root_utils.uproot_to_dict(file)
        return result