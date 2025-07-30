from typing import Optional, Dict
import re

from .rooproc_hybrid_action import RooProcHybridAction
from .auxiliary import register_action

@register_action
class RooProcAlias(RooProcHybridAction):
    
    NAME = "ALIAS"
    
    def __init__(self, alias:str, column_name:str):
        super().__init__(alias=alias, column_name=column_name)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        result = re.search(r"^\s*(\w+)\s*=\s*([\w\.\${}]+)\s*$", main_text)
        if not result:
            if re.search(r"^\s*(\w+)\s*=\s*([\w\.\${}]+)", main_text):
                raise RuntimeError(f'can not alias an expression ("{main_text}"), '
                                   'please use DEFINE instead')
            raise RuntimeError(f"invalid expression {main_text}")
        alias = result.group(1)
        column_name = result.group(2)
        return cls(alias=alias, column_name=column_name)

    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        alias = params['alias']
        column_name = params['column_name']
        rdf_next = rdf.Alias(alias, column_name)
        return rdf_next, processor

    def get_referenced_columns(self, global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars, strict=False)
        column = params['column_name']
        return [column]

    def get_defined_columns(self, global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars, strict=False)
        column = params['alias']
        return [column]