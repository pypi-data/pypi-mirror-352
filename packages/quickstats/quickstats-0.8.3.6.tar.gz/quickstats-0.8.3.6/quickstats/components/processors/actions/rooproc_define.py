from typing import Optional, Dict
import re

from quickstats.utils.string_utils import extract_variable_names
from .rooproc_rdf_action import RooProcRDFAction
from .auxiliary import register_action

@register_action
class RooProcDefine(RooProcRDFAction):
    
    NAME = "DEFINE"
    
    def __init__(self, name:str, expression:str):
        super().__init__(name=name, expression=expression)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        main_text = re.sub(' +', ' ', main_text)
        result = re.search(r"^\s*(\w+)\s*=(.*)", main_text)
        if not result:
            raise RuntimeError(f"invalid expression {main_text}")
        name = result.group(1)
        expression = result.group(2)
        return cls(name=name, expression=expression)        
        
    def _execute(self, rdf:"ROOT.RDataFrame", **params):
        name = params['name']
        expression = params['expression']
        rdf_next = rdf.Define(name, expression)
        return rdf_next

    def get_referenced_columns(self, global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars, strict=False)
        expr = params['expression']
        # need to remove global variables from the variable search
        literals = self._get_literals(expr)
        for literal in literals:
            expr = expr.replace("${" + literal + "}", "1")
        literals = ["${" + literal + "}" for literal in literals]
        referenced_columns = extract_variable_names(expr)
        referenced_columns.extend(literals)
        return referenced_columns

    def get_defined_columns(self, global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars, strict=False)
        defined_columns = [params['name']]
        return defined_columns