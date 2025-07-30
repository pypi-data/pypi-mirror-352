from typing import Optional, Union, Dict, List, Tuple
import os

from quickstats import PathManager
from quickstats.utils.common_utils import combine_dict

class AnalysisPathManager(PathManager):
    
    DEFAULT_DIRECTORIES = {
        "ntuple"                : "ntuples",
        "array"                 : "arrays",
        "output"                : "outputs",
        "study"                 : ("output", "base_study"),
        "ml_model"              : ("study", "models"),
        "categorized_array"     : ("study", "categorized_arrays"),
        "categorized_minitree"  : ("study", "categorized_minitrees"),
        "categorized_histogram" : ("study", "categorized_histograms"),
        "yield"                 : ("study", "yields"),
        "signal_model"          : ("study", "signal_modelling"),
        "summary"               : ("study", "summary"),
        "plot"                  : ("study", "plots"),
        "workspace"             : ("study", "workspaces"),
        "xml"                   : ("study", "xmls"),
        "xml_config"            : ("xml", "config"),
        "xml_data"              : ("xml", "data"),
        "xml_model"             : ("xml", "models"),
        "xml_category"          : ("xml", "categories"),
        "xml_systematics"       : ("xml", "systematics"),
        "stat_result"           : ("output", "stat_results"),
        "limit"                 : ("stat_result", "limits"),
        "likelihood"            : ("stat_result", "likelihoods")
    }
    
    DEFAULT_FILES = {
        "ntuple_sample"                            : ("ntuple", "{sample}.root"),
        "train_sample"                             : ("array", "{sample}.{fmt}"),
        "array_sample"                             : ("array", "{sample}.{fmt}"),
        "categorized_array_sample"                 : ("categorized_array", "{sample}_{category}.{fmt}"),
        "categorized_minitree_sample"              : ("categorized_minitree", "{sample}_{category}.root"),
        "categorized_histogram_sample"             : ("categorized_histogram", "{sample}_{category}.root"),
        "score_distribution_plot"                  : ("plot", "score_distribution_{channel}.pdf"),
        "variable_distribution_plot"               : ("plot", "distribution_{variable}_{category}.pdf"),
        "merged_yield_data"                        : ("yield", "yields.json"),
        "merged_yield_err_data"                    : ("yield", "yields_err.json"),
        "yield_data"                               : ("yield", "yields_{category}.json"),
        "yield_err_data"                           : ("yield", "yields_err_{category}.json"),  
        "signal_modelling_plot"                    : ("plot", "modelling_{category}.pdf"),
        "signal_modelling_data"                    : ("signal_model", "model_parameters.json"),
        "signal_modelling_summary"                 : ("signal_model", "model_summary_{category}.json"),
        "input_xml"                                : ("xml_config", "input.xml"),
        "category_summary"                         : ("summary", "category_summary_{channel}.json"),
        "boundary_data"                            : ("summary", "boundary_tree_{channel}.json"),
        "benchmark_significance"                   : ("summary", "benchmark_significance.json")
    }

    @property
    def study_name(self):
        return self.directories['study'].basename
        
    def __init__(self, study_name : str = "base_study",
                 base_path:str = None,
                 directories:Optional[Dict[str, str]]=None,
                 files:Optional[Dict[str, Union[str, Tuple[Optional[str], str]]]]=None):
        super().__init__(base_path=base_path, directories=directories, files=files)
        self.set_study_name(study_name)

    def set_study_name(self, name: str = "base_study"):
        self.directories['study'].basename = name