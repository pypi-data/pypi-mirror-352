from typing import Optional, List
import fnmatch

from .rooproc_output_action import RooProcOutputAction
from .auxiliary import register_action
from .formatter import ListFormatter

from quickstats.utils.common_utils import is_valid_file, filter_by_wildcards

@register_action
class RooProcSave(RooProcOutputAction):
    
    NAME = "SAVE"
    
    def __init__(self, treename:str, filename:str, 
                 columns:Optional[List[str]]=None,
                 exclude:Optional[List[str]]=None):
        super().__init__(treename=treename,
                         filename=filename,
                         columns=columns,
                         exclude=exclude)
    
    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        treename = params['treename']
        filename = params['filename']
        if processor.cache and is_valid_file(filename):
            processor.stdout.info(f'INFO: Cached output from "{filename}".')
            return rdf, processor
        columns = params.get('columns', None)
        exclude = params.get('exclude', None)
        save_columns = self.resolve_columns(rdf, processor,
                                            columns=columns,
                                            exclude=exclude,
                                            mode="ALL")
        processor.stdout.info(f'Writing output to "{filename}".')
        self.makedirs(filename)
        if processor.use_template:
            from quickstats.utils.root_utils import templated_rdf_snapshot 
            rdf_next = templated_rdf_snapshot(rdf, save_columns)(treename, filename, save_columns)
        else:
            rdf_next = rdf.Snapshot(treename, filename, save_columns)
        return rdf_next, processor