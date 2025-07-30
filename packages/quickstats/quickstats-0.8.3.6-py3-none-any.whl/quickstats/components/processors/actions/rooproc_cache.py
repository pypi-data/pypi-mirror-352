from typing import Optional, Dict, List
import re

from .rooproc_output_action import RooProcOutputAction
from .auxiliary import register_action

@register_action
class RooProcCache(RooProcOutputAction):
    
    NAME = "CACHE"

    def __init__(self,
                 columns:Optional[List[str]]=None,
                 exclude:Optional[List[str]]=None,
                 **kwargs):
        super().__init__(filename=None,
                         columns=columns,
                         exclude=exclude,
                         **kwargs)

    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        columns = params.get('columns', None)
        exclude = params.get("exclude", None)
        cache_columns = self.resolve_columns(rdf, processor,
                                             columns=columns,
                                             exclude=exclude,
                                             mode="ALL")
        rdf_next = rdf.Cache(cache_columns)
        return rdf_next, processor
