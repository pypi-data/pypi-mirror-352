from typing import Optional, Dict
import re

from .rooproc_alias import RooProcAlias
from .auxiliary import register_action

@register_action
class RooProcSafeAlias(RooProcAlias):
    
    NAME = "SAFEALIAS"
    
    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        alias = params['alias']
        column_name = params['column_name']
        all_column_names = [str(i) for i in rdf.GetColumnNames()]
        if column_name not in all_column_names:
            processor.stdout.warning(f"WARNING: Column name `{column_name}` does not exist. No alias made.")
            return rdf, processor
        rdf_next = rdf.Alias(alias, column_name)
        return rdf_next, processor