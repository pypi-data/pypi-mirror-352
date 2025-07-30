from typing import Optional, List, Dict, Union
import os
import glob
import json
import fnmatch

from quickstats import AbstractObject, cached_import
from quickstats.interface.root import TChain
from quickstats.utils.common_utils import str_list_filter

class RooInspector(AbstractObject):
    def __init__(self, source:Union[str, List[str]],
                 treename: Optional[str]=None,
                 filter_expr:Optional[str]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.initialize(source=source,
                        treename=treename,
                        filter_expr=filter_expr)
    
    def initialize(self, source: Union[str, List[str]],
                   treename: Optional[str]=None,
                   filter_expr:Optional[str]=None):
        ROOT = cached_import("ROOT")
        self.chain = TChain(source, default_treename=treename)
        self.rdf = ROOT.RDataFrame(self.chain.get())
        if filter_expr is not None:
            self.rdf = self.rdf.Filter(filter_expr)
        
    def get_column_names(self)->List[str]:
        column_names = sorted([str(i) for i in self.rdf.GetColumnNames()])
        return column_names
    
    def get_column_types(self, column_names:List[str])->Dict[str,str]:
        all_column_names = self.get_column_names()
        invalid_column_names = set(column_names) - set(all_column_names)
        if len(invalid_column_names) > 0:
            raise RuntimeError("unknown column names: {}".format(",".join(invalid_column_names)))
        column_types = {}
        for column_name in column_names:
            try:
                column_types[column_name] = str(self.rdf.GetColumnType(column_name))
            except Eception:
                column_types[column_name] = "undefined"
        return column_types
    
    def get_entries(self):
        return self.rdf.Count().GetValue()
    
    def print_summary(self, suppress_print:bool=False,
                      include_patterns:Optional[List]=None, exclude_patterns:Optional[List]=None,
                      save_as:Optional[str]=None):
        column_names = self.get_column_names()
        if include_patterns is not None:
            column_names = str_list_filter(column_names, include_patterns, inclusive=True)
        if exclude_patterns is not None:
            column_names = str_list_filter(column_names, exclude_patterns, inclusive=False)
        column_types = self.get_column_types(column_names)
        nentries = self.get_entries()
        n_columns = len(column_types)
        summary_str = f"Number of Events: {nentries:,}\n"
        summary_str += f"Columns of Interest ({n_columns}):\n"
        for cname, ctype in column_types.items():
            ctype_str = "(" + ctype + ")"
            summary_str += f"{ctype_str:<30}{cname}\n"
        if not suppress_print:
            self.stdout.info(summary_str, bare=True)
        if save_as is not None:
            with open(save_as, "w") as f:
                f.write(summary_str)
        
        

    