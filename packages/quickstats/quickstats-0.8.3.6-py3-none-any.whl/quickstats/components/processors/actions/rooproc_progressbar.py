from typing import Optional
import re

from quickstats import cached_import
from quickstats.utils.common_utils import in_notebook
from .rooproc_hybrid_action import RooProcHybridAction
from .auxiliary import register_action

@register_action
class RooProcProgressBar(RooProcHybridAction):
    
    NAME = "PROGRESSBAR"
        
    def _execute(self, rdf:"ROOT.RDataFrame", processor, **params):
        ROOT = cached_import("ROOT")
        if not isinstance(rdf, ROOT.RDataFrame):
            rdf_next = ROOT.RDF.AsRNode(rdf)
        else:
            rdf_next = rdf
        if in_notebook():
            processor.stdout.warning("ProgressBar does not work properly inside jupyter. Disabling for now.")
        else:
            ROOT.RDF.Experimental.AddProgressBar(rdf_next)
        return rdf_next, processor