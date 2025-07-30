from .rooproc_stat import RooProcStat
from .auxiliary import register_action

@register_action
class RooProcMin(RooProcStat):
    
    NAME = "GETMIN"
    
    def _get_func(self, rdf:"ROOT.RDataFrame"):
        return rdf.Min