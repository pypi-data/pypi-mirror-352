from typing import Optional, Dict
import re

from quickstats.utils.string_utils import extract_variable_names
from .rooproc_rdf_action import RooProcRDFAction
from .auxiliary import register_action

@register_action
class RooProcFilter(RooProcRDFAction):
    
    NAME = "FILTER"
    
    def __init__(self, expression:str, name:Optional[str]=None):
        super().__init__(expression=expression,
                         name=name)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        name_literals = re.findall(r"@{([^{}]+)}", main_text)
        if len(name_literals) == 0:
            name = main_text.strip()
            expression = name
        elif len(name_literals) == 1:
            name = name_literals[0]
            expression = main_text.replace("@{" + name + "}", "").strip()
        else:
            raise RuntimeError(f"multiple filter names detected in the expression `{main_text}`")
        return cls(name=name, expression=expression)
        
    def _execute(self, rdf:"ROOT.RDataFrame", **params):
        expression = params['expression']
        name = params.get("name", None)
        if name is not None:
            rdf_next = rdf.Filter(expression, name)
        else:
            rdf_next = rdf.Filter(expression)
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