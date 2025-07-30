import os
import sys
import copy
import json
import traceback
from typing import Optional, Union, Dict, List, Any
from itertools import repeat

import pandas as pd

from quickstats import semistaticmethod, cached_import
from quickstats.concurrent import AbstractRunner
from quickstats.utils.common_utils import combine_dict, batch_makedirs, str_list_filter
from quickstats.utils.string_utils import split_str
from quickstats.components import ExtendedModel, NuisanceParameterRanking

class NuisanceParameterRankingRunner(AbstractRunner):
    def __init__(self, filename:str, filter_expr:Optional[str]=None,
                 exclude_expr:Optional[str]=None, constrained_only:bool=True,
                 poi_name:Optional[str]=None, data_name:str="combData",
                 config:Optional[Dict]=None, cache:bool=True,
                 outdir:str="pulls", outname:str="{nuis_name}.json",
                 save_log:bool=True, parallel:int=-1,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(parallel=parallel, save_log=save_log,
                         cache=cache, verbosity=verbosity)
        cached_import("ROOT")
        
        self.attributes = {
            'filename': filename,
            'poi_name': poi_name,
            'data_name': data_name,
            'config': config,
            'outdir': outdir,
            'outname': outname,
            'verbosity': verbosity
        }
        
        self.attributes['nuis_list'] = self.get_nuis_list(constrained_only=constrained_only,
                                                          filter_expr=filter_expr,
                                                          exclude_expr=exclude_expr)

    def get_nuis_list(self, constrained_only:bool=True,
                      filter_expr:Optional[str]=None,
                      exclude_expr:Optional[str]=None):
        model = ExtendedModel(self.attributes['filename'],
                              data_name=None, verbosity='ERROR')
        # include constrained NPs only
        if constrained_only:
            nuis_list = [np.GetName() for np in model.get_variables("constrained_nuisance_parameter")]
        # include all NPs
        else:
            nuis_list = [np.GetName() for np in model.get_variables("nuisance_parameter")]
        if filter_expr:
            include_patterns = split_str(filter_expr, sep=',', remove_empty=True)
            nuis_list = str_list_filter(nuis_list, include_patterns, inclusive=True)
        if exclude_expr:
            exclude_patterns = split_str(exclude_expr, sep=',', remove_empty=True)
            nuis_list = str_list_filter(nuis_list, exclude_patterns, inclusive=False)
        return nuis_list
    
    def prepare_task_inputs(self):
        
        base_kwargs = combine_dict(self.attributes)
        outdir    = base_kwargs.pop('outdir')
        nuis_list = base_kwargs.pop('nuis_list')
        
        argument_list = []
        for nuis_name in nuis_list:
            kwargs = combine_dict(base_kwargs)
            kwargs['nuis_name'] = nuis_name
            outname = kwargs['outname'].format(nuis_name=nuis_name)
            kwargs['outname'] = os.path.join(outdir, outname)
            argument_list.append(kwargs)
        return argument_list, None

    def _prerun_batch(self):
        self.stdout.tips("When running nuisance parameter pulls/impacts on an Asimov dataset, remember to restore the "
                         "global observables to their Asimov values by loading the appropriate snapshot.")
        outdir = self.attributes['outdir']
        batch_makedirs([outdir])
        
    @semistaticmethod
    def _prerun_instance(self, nuis_name:str, **kwargs):
        self.stdout.info(f"Evaluating pulls and impacts for the NP: {nuis_name}")
    
    @semistaticmethod
    def _cached_return(self, outname:str):
        return None
    
    @semistaticmethod
    def _run_instance(self, filename:str, nuis_name:str,
                      poi_name:Optional[Union[str, List[str]]]=None,
                      data_name:str="combData",
                      config:Optional[Dict]=None,
                      outname:Optional[str]=None,
                      verbosity:Optional[Union[int, str]]="INFO",
                      **kwargs):
        try:
            if poi_name is None:
                poi_name = []
                eval_impact = False
            else:
                eval_impact = True
            tool = NuisanceParameterRanking(filename, data_name=data_name,
                                            poi_name=poi_name, config=config,
                                            verbosity=verbosity)
            result = tool.evaluate_pulls_and_impact(nuis_name=nuis_name,
                                                    prefit_impact=eval_impact,
                                                    postfit_impact=eval_impact)
            if (outname is not None):
                with open(outname, 'w') as file:
                    json.dump(result, file, indent=2)
                tool.stdout.info(f'Saved pulls and impact results to {outname}')
            return None
        except Exception as e:
            sys.stdout.write(traceback.format_exc())
            return None