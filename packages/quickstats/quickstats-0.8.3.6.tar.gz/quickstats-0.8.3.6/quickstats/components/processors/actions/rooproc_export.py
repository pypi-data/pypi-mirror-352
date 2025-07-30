from typing import Optional, List, Dict
import os
import json

from .rooproc_helper_action import RooProcHelperAction
from .auxiliary import register_action

from quickstats.utils.common_utils import is_valid_file

@register_action
class RooProcExport(RooProcHelperAction):
    
    NAME = "EXPORT"
    
    def __init__(self, filename:str):
        super().__init__(filename=filename)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        kwargs = cls.parse_as_kwargs(main_text)
        return cls(**kwargs)
    
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        filename = params['filename']
        if processor.cache and is_valid_file(filename):
            processor.stdout.info(f'Cached output "{filename}".')
            return processor   
        data = {k:v.GetValue() for k,v in processor.external_variables.items()}
        dirname = os.path.dirname(filename)
        if dirname and (not os.path.exists(dirname)):
            os.makedirs(dirname)
        with open(filename, 'w') as outfile:
            processor.stdout.info(f'Writing auxiliary data to "{filename}".')
            json.dump(data, outfile, indent=2)
        return processor