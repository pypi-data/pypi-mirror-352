import os
import sys
import json
from typing import Optional, Union, Dict, List, Any
from itertools import repeat

from quickstats import semistaticmethod, cached_import
from quickstats.parsers import ParamParser
from quickstats.concurrent import ParameterisedRunner
from quickstats.utils.common_utils import batch_makedirs, json_load, combine_dict, save_json
from quickstats.components import AsymptoticCLs

class ParameterisedAsymptoticCLs(ParameterisedRunner):
    def __init__(self, input_path:str, config:Optional[Dict]=None,
                 file_expr:Optional[str]=None, param_expr:Optional[str]=None,
                 filter_expr:Optional[str]=None, exclude_expr:Optional[str]=None,
                 outdir:str="output", cachedir:str="cache", outname:str="limits.json",
                 save_summary:bool=False, cache:bool=True,
                 save_log:bool=True, parallel:int=-1,
                 verbosity:Optional[Union[int, str]]="INFO"):
        
        super().__init__(file_expr=file_expr, param_expr=param_expr,
                         filter_expr=filter_expr, exclude_expr=exclude_expr,
                         parallel=parallel, save_log=save_log,
                         outdir=outdir, cachedir=cachedir,
                         cache=cache, allow_none=False, verbosity=verbosity)
        cached_import("ROOT")
        
        self.attributes.update({
            'input_path': input_path,
            'config': config,
            'outname': outname,
            'save_summary': save_summary
        })
    
    @semistaticmethod
    def _prerun_instance(self, filename:str, parameters:Optional[Dict[str, Any]]=None, **kwargs):
        if parameters:
            param_str = "("+ParamParser.val_encode_parameters(parameters)+")"
        else:
            param_str = ""
        self.stdout.info(f"Evaluating limit {param_str} for the workspace {filename}")

    @semistaticmethod
    def _run_instance(self, filename:str, config:Dict[str, Any],
                      parameters:Dict[str, Any],
                      outname:Optional[str]=None,
                      save_summary:bool=True,
                      **kwargs):
        try:
            config['filename'] = filename
            config.update(kwargs)
            asymptotic_cls = AsymptoticCLs(**config)
            asymptotic_cls.evaluate_limits()
            if outname is not None:
                asymptotic_cls.save(outname, parameters=parameters, summary=save_summary)
            return asymptotic_cls.limits
        except Exception as e:
            sys.stdout.write(f"{e}\n")
            return {}
        
    def prepare_task_inputs(self):
        input_path = self.attributes['input_path']
        cache_dir  = self.get_cache_dir()
        outname    = "{param_str}.json"
        param_points = self.get_param_points(input_path)
        param_data = self.get_serialised_param_data(param_points, outdir=cache_dir, outname=outname)
        
        configs = []
        base_config = self.attributes['config']
        for param_point in param_points:
            base_fix_params = base_config.get("fix_param", None)
            internal_params = param_point['internal_parameters']
            fix_param_expr = self.join_param_setup(base_fix_params, internal_params)
            config = combine_dict(base_config, {"fix_param": fix_param_expr})
            configs.append(config)
        param_dpd_kwargs = {
            'filename': param_data['filenames'],
            'config': configs,
            'outname': param_data['outnames'],
            'parameters': param_data['parameters']
        }
        param_ind_kwargs = {
            'save_summary' : self.attributes['save_summary'],
            'verbosity'    : self.attributes['verbosity']
        }
        self.set_param_ind_kwargs(**param_ind_kwargs)
        self.set_param_dpd_kwargs(**param_dpd_kwargs)
        kwarg_set = self.create_kwarg_set()
        auxiliary_args = {
            'filenames': param_data['filenames'],
            'parameters': param_data['parameters']
        }
        if not kwarg_set:
            raise RuntimeError("no parameter point to scan for")
        return kwarg_set, auxiliary_args
    
    def postprocess(self, raw_result, auxiliary_args:Optional[Dict]=None):
        filenames = auxiliary_args["filenames"]
        parameters = auxiliary_args["parameters"]
        
        final_result = []
        for filename, params, limit in zip(filenames, parameters, raw_result):
            if len(limit) == 0:
                if params:
                    param_str = "("+ParamParser.val_encode_parameters(params)+")"
                else:
                    param_str = ""                
                raise RuntimeError(f'Job failed for the input "{filename}" {param_str}. '
                                   'Please check the log file for more details.')
            final_result.append({**params, **limit})
        import pandas as pd
        final_result = pd.DataFrame(final_result).to_dict('list')

        poi_name   = self.attributes['config'].get('poi_name', None)
        outdir     = self.attributes['outdir']
        outname    = self.attributes['outname'].format(poi_name=poi_name)
        
        if outname is not None:
            outpath = os.path.join(outdir, outname)
            save_json(final_result, outpath)