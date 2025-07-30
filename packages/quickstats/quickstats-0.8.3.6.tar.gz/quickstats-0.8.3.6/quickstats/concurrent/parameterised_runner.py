from typing import Optional, List, Dict, Union, Tuple
import os
import json

from quickstats import semistaticmethod, cached_import
from . import AbstractRunner
from quickstats.parsers import ParamParser
from quickstats.utils.common_utils import combine_dict, batch_makedirs
from quickstats.utils.root_utils import close_all_root_files

class ParameterisedRunner(AbstractRunner):
    
    @property
    def parser(self):
        return self._parser
    
    @property
    def param_points(self):
        return self._param_points
    
    def __init__(self, file_expr:Optional[str]=None,
                 param_expr:Optional[str]=None,
                 filter_expr:Optional[str]=None,
                 exclude_expr:Optional[str]=None,
                 outdir:str="output", cachedir:str="cache",
                 save_log:bool=True, cache:bool=True,
                 allow_none:bool=True, parallel:int=-1,
                 verbosity:Optional[Union[int, str]]="INFO"):
        
        super().__init__(parallel=parallel, save_log=save_log,
                         cache=cache, verbosity=verbosity)
        cached_import("ROOT")
        self.attributes = {
            'outdir'   : outdir,
            'cachedir' : cachedir,
            'verbosity': verbosity
        }
        
        self.filter_expr = filter_expr
        self.exclude_expr = exclude_expr
        self._parser = ParamParser(file_expr, param_expr, allow_none=allow_none)
        self._param_points = None
        self.param_ind_kwargs = {}
        self.param_dpd_kwargs = {}

    def _prerun_batch(self):
        outdir = self.attributes['outdir']
        cache_dir = self.get_cache_dir()
        batch_makedirs([outdir, cache_dir])

    @semistaticmethod
    def _cached_return(self, outname:str):
        with open(outname, 'r') as f:
            result = json.load(f)
            processed_result = self._process_result(result)
        return processed_result

    @semistaticmethod
    def _process_result(self, result:Dict):
        return result
        
    def setup_parser(self, file_expr:Optional[str]=None,
                     param_expr:Optional[str]=None):
        self._parser.setup(file_expr, param_expr)

    def get_cache_dir(self):
        return os.path.join(self.attributes['outdir'], self.attributes['cachedir'])
        
    def get_param_points(self, input_path:str):
        param_points = self.parser.get_param_points(input_path, filter_expr=self.filter_expr,
                                                    exclude_expr=self.exclude_expr)
        return param_points

    def get_internal_param_points(self):
        param_points = self.parser.get_internal_param_points(filter_expr=self.filter_expr,
                                                             exclude_expr=self.exclude_expr)
        return param_points

    def get_external_param_points(self, input_path:str):
        param_points = self.parser.get_external_param_points(input_path, filter_expr=self.filter_expr,
                                                             exclude_expr=self.exclude_expr)
        return param_points
        
    def get_serialised_param_data(self, param_points:str, outdir:str="./", outname:str="{param_str}.json"):
        filenames = []
        outnames = []
        parameter_list = []
        outname_raw = os.path.join(outdir, outname)
        for param_point in param_points:
            filename = param_point['filename']
            parameters = {**param_point['internal_parameters'], **param_point['external_parameters']}
            param_str = ParamParser.str_encode_parameters(parameters)
            if not param_str:
                param_str = os.path.splitext(os.path.basename(filename))[0]
            outname = outname_raw.format(param_str=param_str)
            filenames.append(filename)
            parameter_list.append(parameters)
            outnames.append(outname)
        if len(outnames) != len(set(outnames)):
            raise RuntimeError("output names are not distinct, please check your input. (this can be "
                               "due to 1. multiple tasks have the same set of parameters or 2. "
                               "multiple zero-parameter tasks with input files of the same basename)")
        serialised_param_data = {
            'filenames': filenames,
            'outnames': outnames,
            'parameters': parameter_list
        }
        return serialised_param_data
    
    def set_param_ind_kwargs(self, **kwargs):
        self.param_ind_kwargs = kwargs
        
    def set_param_dpd_kwargs(self, **kwargs):
        self.param_dpd_kwargs = kwargs
        
    def create_kwarg_set(self):
        n_params = [len(v) for v in self.param_dpd_kwargs.values()]
        if len(set(n_params)) != 1:
            raise RuntimeError("inconsistent shape for parameter dependent argument set")
        kwarg_set = [combine_dict(self.param_ind_kwargs, dict(zip(self.param_dpd_kwargs, t))) \
                     for t in zip(*self.param_dpd_kwargs.values())]
        return kwarg_set
    
    def prepare_task_inputs(self)->Tuple[List, Dict]:
        raise NotImplementedError
    
    def run(self, cache_only:bool=False):
        kwarg_set, auxiliary_args = self.prepare_task_inputs()
        return self.run_batch(kwarg_set, auxiliary_args=auxiliary_args, cache_only=cache_only)

    def _end_of_instance_cleanup(self):
        close_all_root_files()

    @staticmethod
    def join_param_setup(base_setup:Optional[str]=None, new_setup:Optional[str]=None):
        components = []
        for setup in [base_setup, new_setup]:
            if not setup:
                continue
            if isinstance(setup, dict):
                setup = ParamParser.val_encode_parameters(setup)
            assert isinstance(setup, str)
            components.append(setup)
        if not components:
            return None
        return ",".join(components)
