import os
import sys
import copy
import json
import math
from typing import Optional, Union, Dict, List, Any
from itertools import repeat

from quickstats import semistaticmethod, cached_import
from quickstats.parsers import ParamParser
from quickstats.concurrent import ParameterisedRunner
from quickstats.utils.common_utils import batch_makedirs, save_json
from quickstats.components import Likelihood
from quickstats.components.basics import WSArgument

class ParameterisedLikelihood(ParameterisedRunner):
    
    def __init__(self, input_path:str, param_expr:str, file_expr:Optional[str]=None,
                 filter_expr:Optional[str]=None, exclude_expr:Optional[str]=None,
                 data_name:str="combData", uncond_snapshot:Optional[str]=None,
                 config:Optional[Dict]=None, outdir:str="output", cachedir:str="cache",
                 outname:str="{poi_names}.json", cache:bool=True, cache_ws:bool=False,
                 save_log:bool=True, parallel:int=-1, allow_nan:bool=True,
                 verbosity:Optional[Union[int, str]]="INFO"):
        
        super().__init__(file_expr=file_expr, param_expr=param_expr,
                         filter_expr=filter_expr, exclude_expr=exclude_expr,
                         parallel=parallel, save_log=save_log,
                         outdir=outdir, cachedir=cachedir,
                         cache=cache, allow_none=True, verbosity=verbosity)
        cached_import("ROOT")
        
        self.attributes.update({
            'input_path': input_path,
            'data_name': data_name,
            'uncond_snapshot': uncond_snapshot,
            'config': config,
            'outname': outname
        })
        
        self.allow_nan = allow_nan
        self.cache_ws = cache_ws
        
        self.attributes['poi_names'] = ParamParser._get_param_str_attributes(param_expr)

    def _prerun_batch(self):
        self.stdout.tips("When running likelihood scan on an Asimov dataset, remember to restore the global "
                         "observables to their Asimov values by loading the appropriate snapshot.")
        super()._prerun_batch()
    
    @semistaticmethod
    def _prerun_instance(self, filename:str, mode:int, poi_val:Optional[Union[float, Dict[str, float]]]=None, **kwargs):
        if mode == 2:
            param_str = "("+ParamParser.val_encode_parameters(poi_val)+")"
            self.stdout.info(f"Evaluating conditional NLL {param_str} for the workspace {filename}")
        elif mode == 1:
            self.stdout.info(f"Evaluating unconditional NLL for the workspace {filename}")
    
    def _is_valid_cache(self, cached_result):
        if (not self.allow_nan) and math.isnan(cached_result['nll']):
            self.stdout.info('Found cached result with nan nll. Retrying')
            return False
        return True
    
    @semistaticmethod
    def _process_result(self, result:Dict):
        if 'uncond_fit' in result:
            fit_result = result['uncond_fit']
        elif 'cond_fit' in result:
            fit_result = result['cond_fit']
        else:
            raise RuntimeError("unexpected output (expect only conditional/unconditional fit in each task)")        
        nll    = fit_result['nll']
        status = fit_result['status']
        mu     = fit_result.get("mu", {})
        muhat  = fit_result.get("muhat", {})
        
        processed_result = {
            'nll': nll,
            'mu' : mu,
            'status': status
        }
        processed_result['mu'].update(muhat)
        return processed_result
        
    @semistaticmethod
    def _run_instance(self, filename:str, mode:int,
                      poi_name:Optional[Union[str, List[str]]]=None,
                      poi_val:Optional[Union[float, Dict[str, float]]]=None,
                      data_name:str="combData",
                      snapshot_name:Optional[str]=None,
                      config:Optional[Dict]=None,
                      outname:Optional[str]=None,
                      **kwargs):
        try:
            if mode not in [1, 2, 4]:
                error_msg = "only unconditional/conditional fit is allowed in parameterised likelihood runner"
                self.stdout.error(error_msg)
                raise RuntimeError(error_msg)
            if config is None:
                config = {}
            config.update(kwargs)
            do_minos = config.pop("do_minos", False)
            likelihood = Likelihood(filename=filename, poi_name=poi_name, data_name=data_name, 
                                    **config)
            fit_result = likelihood.nll_fit(poi_val, mode=mode, do_minos=do_minos,
                                            snapshot_name=snapshot_name)
            # save results
            if outname is not None:
                with open(outname, 'w') as outfile:
                    json.dump(fit_result, outfile)
                    outfile.truncate()
                self.stdout.info(f'Saved NLL result to {outname}')

                if self.cache_ws:
                    # save snapshot
                    outname_ws = outname.replace(".json", ".root")
                    likelihood.save(outname_ws)

            result = self._process_result(fit_result)
            return result
        except Exception as e:
            sys.stdout.write(f"{e}\n")
            return None
    
    def prepare_task_inputs(self):
        
        poi_names = self.attributes['poi_names']
        if len(poi_names) == 0:
            raise RuntimeError("no POI(s) to scan for")
            
        input_path = self.attributes['input_path']
        cache_dir  = self.get_cache_dir()
        outname    = "{param_str}.json"
        param_points = self.get_param_points(input_path)
        n_param_points = len(param_points)
        param_data = self.get_serialised_param_data(param_points, outdir=cache_dir, outname=outname)

        filenames = param_data['filenames']
        if not filenames:
            raise RuntimeError(f"no input file found matching the expression: {input_path}")

        external_param_points = self.get_external_param_points(input_path)
        unique_filenames = []
        outnames = []
        poi_names_text = "_".join(poi_names)
        for param_point in external_param_points:
            unique_filenames.append(param_point['filename'])
            param_str = ParamParser.str_encode_parameters(param_point['parameters'])
            if param_str:
                basename = f"{param_str}_{poi_names_text}_uncond"
            else:
                basename = f"{poi_names_text}_uncond"
            outnames.append(os.path.join(cache_dir, basename))
            
        n_unique_files = len(unique_filenames)
            
        if self.attributes['uncond_snapshot'] is None:
            # None is for unconditional NLL
            poi_values = [None] * n_unique_files
            # 1 is for unconditional NLL, 2 is for conditional NLL
            modes = [1] * n_unique_files + [2] * n_param_points
            snapshot_names = [Likelihood.kCurrentSnapshotName] * (n_unique_files + n_param_points)
        else:
            poi_values = [None] * n_unique_files
            modes = [4] * n_unique_files + [2] * n_param_points
            uncond_snapshot_name = self.attributes['uncond_snapshot']
            snapshot_names = ([uncond_snapshot_name] * n_unique_files + 
                              [Likelihood.kCurrentSnapshotName] * n_param_points)
        
        for param_point in param_points:
            poi_values.append(param_point['internal_parameters'])
            
        param_dpd_kwargs = {
            'filename'      : unique_filenames + filenames,
            'poi_val'       : poi_values,
            'mode'          : modes,
            'snapshot_name' : snapshot_names,
            'outname'       : outnames + param_data['outnames']
        }
        
        param_ind_kwargs = {
            'poi_name'  : self.attributes['poi_names'],
            'data_name' : self.attributes['data_name'],
            'config'    : self.attributes['config'],
            'verbosity' : self.attributes['verbosity']
        }
        
        self.set_param_ind_kwargs(**param_ind_kwargs)
        self.set_param_dpd_kwargs(**param_dpd_kwargs)
        kwarg_set = self.create_kwarg_set()
        auxiliary_args = {
            'points': poi_values
        }
        if not kwarg_set:
            raise RuntimeError("no parameter point to scan for")        
        return kwarg_set, auxiliary_args
    
    def postprocess(self, raw_result, auxiliary_args:Optional[Dict]=None):
        points = auxiliary_args['points']
        for result, poi_values in zip(raw_result, points):
            if result is None:
                if poi_values is None:
                    raise RuntimeError('NLL evaluation failed for the unconditional fit. '
                                       'Please check the log file for more details.')
                else:
                    param_str = ParamParser.val_encode_parameters(poi_values)
                    raise RuntimeError(f'NLL evaluation failed for the conditional fit ({param_str}).'
                                       'Please check the log file for more details.')
            if not isinstance(result, dict):
                raise RuntimeError("found cache result with deprecated format, a rerun "
                                   "is needed")
        uncond_result = raw_result[0]
        uncond_nll = uncond_result['nll']
        data = {'nll':[], 'qmu':[], 'status': []}
        poi_names = self.attributes['poi_names']
        for poi_name in poi_names:
            data[poi_name] = []
        for result, poi_values in zip(raw_result, points):
            nll   = result['nll']
            status = result['status']
            data['nll'].append(nll)
            data['qmu'].append(2*(nll-uncond_nll))
            data['status'].append(status)
            for poi_name in poi_names:
                mu_map = result['mu']
                if poi_name not in mu_map:
                    if poi_values is None:
                        raise RuntimeError(f'unable to extract value for the POI "{poi_name}" '
                                           f'for the unconditional fit. Please check the log '
                                           f'file for more details')
                    else:
                        param_str = ParamParser.val_encode_parameters(poi_values)
                        raise RuntimeError(f'unable to extract value for the POI "{poi_name}" '
                                           f'for the conditional fit ({param_str}). Please check the log '
                                           f'file for more details')
                mu = mu_map[poi_name]
                data[poi_name].append(mu)
        # backward compatibility
        if len(poi_names) == 1:
            poi_name = poi_names[0]
            data['mu'] = [v for v in data[poi_name]]
        outdir  = self.attributes['outdir']
        outname = self.attributes['outname'].format(poi_names="_".join(poi_names))
        outpath = os.path.join(outdir, outname.format(poi_name=poi_name))
        save_json(data, outpath)