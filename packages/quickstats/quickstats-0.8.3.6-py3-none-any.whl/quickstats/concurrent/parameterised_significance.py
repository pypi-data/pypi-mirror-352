import os
import sys
import json
from typing import Optional, Union, Dict, List, Any

from quickstats import semistaticmethod, cached_import
from quickstats.parsers import ParamParser
from quickstats.concurrent import ParameterisedRunner
from quickstats.utils.common_utils import batch_makedirs, list_of_dict_to_dict_of_list, save_json, combine_dict
from quickstats.maths.numerics import pretty_value
from quickstats.components import AnalysisBase, AsimovType, AsimovGenerator

class ParameterisedSignificance(ParameterisedRunner):
    
    def __init__(self, input_path:str,
                 file_expr:Optional[str]=None,
                 param_expr:Optional[str]=None,
                 poi_name:Optional[str]=None,
                 filter_expr:Optional[str]=None,
                 exclude_expr:Optional[str]=None,
                 data_name:str="combData",
                 snapshot_name:Optional[str]=None,
                 mu_exp:float=0.,
                 asimov_type:Optional[int]=None,
                 config:Optional[Dict]=None,
                 outdir:str="output", cachedir:str="cache",
                 outname:str="{param_names}.json", cache:bool=True,
                 save_log:bool=True, parallel:int=-1,
                 asimov_method:Optional[str]="baseline",
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(file_expr=file_expr,
                         param_expr=param_expr,
                         filter_expr=filter_expr,
                         exclude_expr=exclude_expr,
                         outdir=outdir, cachedir=cachedir,
                         parallel=parallel, save_log=save_log,
                         cache=cache, verbosity=verbosity)
        ROOT = cached_import("ROOT")
        
        self.attributes.update({
            'input_path': input_path,
            'poi_name': poi_name,
            'data_name': data_name,
            'snapshot_name': snapshot_name,
            'mu_exp': mu_exp,
            'asimov_type': asimov_type,
            'asimov_method': asimov_method,
            'config': config,
            'outname': outname
        })

    def _prerun_batch(self):
        self.stdout.tips("When running likelihood fit on an Asimov dataset, remember to restore the global "
                         "observables to their Asimov values by loading the appropriate snapshot. "
                         "Asimov dataset generated on the fly (via the --asimov_type option) will automatically "
                         "load the internally saved snapshot so no user intervention is needed.")
        super()._prerun_batch()
    
    @semistaticmethod
    def _prerun_instance(self, filename:str, parameters:Optional[Union[float, Dict[str, float]]]=None, **kwargs):
        param_str = "("+ParamParser.val_encode_parameters(parameters)+")"
        self.stdout.info(f"Evaluating significance {param_str} for the workspace {filename}")
        
    @semistaticmethod
    def _run_instance(self, filename:str,
                      poi_name:Optional[str]=None,
                      data_name:str="combData",
                      config:Optional[Dict]=None,
                      mu_exp:float=0.,
                      asimov_type:Optional[int]=None,
                      snapshot_name:Optional[str]=None,
                      outname:Optional[str]=None,
                      asimov_method:Optional[str]="baseline",
                      **kwargs):
        try:
            if config is None:
                config = {}
            config.update(kwargs)
            config['filename'] = filename
            config['poi_name'] = poi_name
            config['data_name'] = data_name
            config['snapshot_name'] = snapshot_name
            analysis = AnalysisBase(**config)
            if asimov_type is not None:
                asimov_type = AsimovType.parse(asimov_type)
                asimov_data = analysis.generate_standard_asimov(asimov_type, do_import=False, method=asimov_method)
                asimov_snapshot = AsimovGenerator.ASIMOV_SETTINGS[asimov_type]['asimov_snapshot']
                analysis.set_data(asimov_data)
                result = analysis.nll_fit(poi_val=mu_exp, mode='hybrid',
                                          snapshot_name=asimov_snapshot,
                                          do_minos=config.get('minos', None))
            else:
                result = analysis.nll_fit(poi_val=mu_exp, mode='hybrid',
                                          do_minos=config.get('minos', None))
            if outname:
                with open(outname, 'w') as outfile:
                    json.dump(result, outfile, indent=2)
            return result
        except Exception as e:
            sys.stdout.write(f"{e}\n")
            return None
    
    def prepare_task_inputs(self):
        input_path = self.attributes['input_path']
        cache_dir  = self.get_cache_dir()
        outname    = "{param_str}.json"
        param_points = self.get_param_points(input_path)
        param_data = self.get_serialised_param_data(param_points, outdir=cache_dir, outname=outname)

        configs = []
        base_config = self.attributes['config']
        if base_config is None:
            base_config = {}
        for param_point in param_points:
            base_fix_params = base_config.get("fix_param", None)
            internal_params = param_point['internal_parameters']
            fix_param_expr = self.join_param_setup(base_fix_params, internal_params)
            config = combine_dict(base_config, {"fix_param": fix_param_expr})
            configs.append(config)
        param_dpd_kwargs = {
            'parameters' : param_data['parameters'], # just for display
            'filename'   : param_data['filenames'],
            'outname'    : param_data['outnames'],
            'config'     : configs
        }

        param_ind_kwargs = {}
        for param in ['poi_name', 'data_name', 'snapshot_name',
                      'mu_exp', 'asimov_type', 'asimov_method']:
            param_ind_kwargs[param] = self.attributes[param]
        
        self.set_param_ind_kwargs(**param_ind_kwargs)
        self.set_param_dpd_kwargs(**param_dpd_kwargs)
        kwarg_set = self.create_kwarg_set()
        auxiliary_args = {
            'parameters': param_data['parameters']
        }
        if not kwarg_set:
            raise RuntimeError("no parameter point to scan for")        
        return kwarg_set, auxiliary_args
    
    def postprocess(self, raw_result, auxiliary_args:Dict):
        parameters = auxiliary_args['parameters']
        data = list_of_dict_to_dict_of_list(parameters)
        param_names = list(data.keys())
        data.update({
            'nll_muexp'    : [],
            'nll_muhat'    : [],
            'qmu'          : [],
            'muexp'        : [],
            'muhat'        : [],
            'significance' : [],
            'pvalue'       : [],
            'status_muexp' : [],
            'status_muhat' : [],
            'status'       : []
        })
        for result in raw_result:
            data['nll_muexp'].append(result['cond_fit']['nll'])
            data['nll_muhat'].append(result['uncond_fit']['nll'])
            data['qmu'].append(result['qmu'])
            data['muexp'].append(next(iter(result['cond_fit']['mu'].values())))
            data['muhat'].append(next(iter(result['uncond_fit']['muhat'].values())))
            data['significance'].append(result['significance'])
            data['pvalue'].append(result['pvalue'])
            data['status_muexp'].append(result['cond_fit']['status'])
            data['status_muhat'].append(result['uncond_fit']['status'])
            data['status'].append(result['status'])
        outdir  = self.attributes['outdir']
        outname = self.attributes['outname'].format(param_names="_".join(param_names))
        outpath = os.path.join(outdir, outname)
        save_json(data, outpath)