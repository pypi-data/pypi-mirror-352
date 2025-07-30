from .rooproc_stat import RooProcStat
from .auxiliary import register_action

@register_action
class RooProcMean(RooProcStat):

    NAME = "GETMEAN"
    
    def _get_func(self, rdf:"ROOT.RDataFrame"):
        return rdf.Mean