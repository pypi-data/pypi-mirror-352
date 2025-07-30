from typing import Optional, List, Dict
import fnmatch

import numpy as np

from .rooproc_hybrid_action import RooProcHybridAction
from .formatter import ListFormatter
from quickstats.interface.root import RDataFrameBackend, RDataFrame

class RooProcOutputAction(RooProcHybridAction):

    PARAM_FORMATS = {
        'columns': ListFormatter,
        'exclude': ListFormatter
    }
    
    def __init__(self, filename:str,
                 columns:Optional[List[str]]=None,
                 exclude:Optional[List[str]]=None,
                 **kwargs):
        super().__init__(filename=filename,
                         columns=columns,
                         exclude=exclude,
                         **kwargs)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        kwargs = cls.parse_as_kwargs(main_text)
        return cls._try_create(**kwargs)
    
    def resolve_columns(self, rdf, processor,
                        columns:Optional[List[str]]=None,
                        exclude:Optional[List[str]]=None,
                        mode:str="REMOVE_NON_STANDARD_TYPE"):
        selected_columns, removed_columns = RDataFrame._resolve_columns(rdf=rdf,
                                                                        columns=columns,
                                                                        exclude=exclude,
                                                                        mode=mode)
        if len(removed_columns) > 0:
            col_str = ", ".join(removed_columns)
            processor.stdout.warning("The following column(s) will be excluded from the output as they have "
                                     f"data types incompatible with the output format: {col_str}")
        return selected_columns

    def get_referenced_columns(self, global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars, strict=False)
        columns = params.get("columns", None)
        if columns is None:
            columns = ["*"]
        exclude = params.get("exclude", None)
        if exclude is not None:
            self.stdout.warning("Column exclusion will not be applied when inferring referenced columns")
        return columns