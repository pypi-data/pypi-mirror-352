from .rooproc_define import RooProcDefine
from .auxiliary import register_action

@register_action
class RooProcSafeDefine(RooProcDefine):
    
    NAME = "SAFEDEFINE"
        
    def _execute(self, rdf:"ROOT.RDataFrame", **params):
        name = params['name']
        expression = params['expression']
        all_column_names = [str(i) for i in rdf.GetColumnNames()]
        # already defined, skipping
        if name in all_column_names:
            return rdf
        rdf_next = rdf.Define(name, expression)
        return rdf_next