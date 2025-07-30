from typing import Dict, List, Optional, Union, Tuple, Any
import os
import copy
import json

from quickstats import ConfigurableObject, ConfigComponent, ConfigUnit
from quickstats.utils.common_utils import remove_duplicates

from .analysis_path_manager import AnalysisPathManager
from .config_templates import AnalysisConfig

class AnalysisBase(ConfigurableObject):

    PATH_MANAGER_CLS = AnalysisPathManager
    
    config : ConfigUnit(AnalysisConfig)
    
    @property
    def names(self) -> Dict[str, str]:
        try:
            names = self.config["names"]
        except Exception:
            names = {}
        return names
    
    def __init__(self, analysis_config:Optional[Union[Dict, str]]=None,
                 plot_config:Optional[Union[Dict, str]]=None,
                 ntuple_dir:Optional[str]=None,
                 array_dir:Optional[str]=None,
                 outdir:Optional[str]=None,
                 path_manager:Optional[AnalysisPathManager]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        
        super().__init__(verbosity=verbosity)
        
        if path_manager is None:
            self.path_manager = self.PATH_MANAGER_CLS()
        else:
            self.path_manager = path_manager
        
        self.load_analysis_config(analysis_config)
        self.load_plot_config(plot_config)
            
        # setup file paths used in the analysis pipeline
        self.update_paths(ntuple_dir=ntuple_dir, array_dir=array_dir, outdir=outdir)
                                        
    def update_paths(self, outdir:Optional[str]=None,
                     ntuple_dir:Optional[str]=None,
                     array_dir:Optional[str]=None) -> None:
        for path, config_key, dirname in [(outdir, "outputs", "output"),
                                          (ntuple_dir, "ntuples", "ntuple"),
                                          (array_dir, "arrays", "array")]:
            if path is not None:
                self.config["paths"][config_key] = path
            path = self.config["paths"][config_key]
            self.path_manager.set_directory(dirname, path, absolute=True)
    
    def set_study_name(self, study_name:str) -> None:
        self.path_manager.set_study_name(study_name)
        
    def get_study_name(self) -> str:
        return self.path_manager.study_name
        
    def load_analysis_config(self, config_source:Optional[Union[Dict, str]]=None) -> None:
        if isinstance(config_source, str):
            if not os.path.exists(config_source):
                raise FileNotFoundError(f'Config file "{config_source}" does not exist')
            config_path = os.path.abspath(config_source)
            self.path_manager.set_file("analysis_config", config_path)
        if config_source is not None:
            self.config.load(config_source)
        try:
            self.all_channels = list(self.config['channels'])
        except Exception:
            self.all_channels = []
        try:
            self.all_kinematic_regions = list(self.config['kinematic_regions'])
        except Exception:
            self.all_kinematic_regions = []
        try:
            self.all_samples = list(self.config['samples']['all'])
        except Exception:
            self.all_samples = []
        try:
            self.extra_samples = list(self.config['samples']['extra'])
        except Exception:
            self.extra_samples = []            
        try:
            self.all_variables = list(self.config['variables']['all'])
        except Exception:
            self.all_variables = []
        try:
            self.treename = self.config['names']['tree_name']
        except Exception:
            self.treename = None
        
    def load_plot_config(self, config_source:Optional[Union[Dict, str]]=None) -> None:
        if isinstance(config_source, str):
            if not os.path.exists(config_source):
                raise FileNotFoundError(f'Config file "{config_source}" does not exist')
            config_path = os.path.abspath(config_source)
            self.path_manager.set_file("plot_config", config_path)
        # use the default plot config from the framework
        if config_source is None:
            self.plot_config = {}
            return None
        elif isinstance(config_source, str):
            with open(config_source, "r") as file:
                self.plot_config = json.load(file)
        elif isinstance(config_source, dict):
            self.plot_config = copy.deepcopy(config_source)
        else:
            raise RuntimeError("Invalid plot config format")  
        
    def resolve_channels(self, channels:List[str]) -> List[str]:
        for channel in channels:
            if channel not in self.all_channels:
                raise ValueError(f"Unknown channel: {channel}")
        return channels
    
    def resolve_samples(self, samples:Optional[List[str]]=None) -> List[str]:
        if samples is None:
            return self.all_samples
        resolved_samples = []
        for sample_key in samples:
            if sample_key in self.config['samples']:
                resolved_samples.extend(self.config['samples'][sample_key])
            elif (sample_key in self.all_samples) or (sample_key in self.extra_samples):
                resolved_samples.append(sample_key)
            else:
                raise RuntimeError(f'Unknown sample "{sample_key}". Please make sure it is defined in the list of all samples.')
        resolved_samples = remove_duplicates(resolved_samples)
        return resolved_samples

    def resolve_variables(self, variables:Optional[List[str]]=None) -> List[str]:
        if variables is None:
            return self.all_variables
        resolved_variables = []
        for variable_key in variables:
            if variable_key in self.config['variables']:
                resolved_variables.extend(self.config['variables'][variable_key])
            elif variable_key in self.all_variables:
                resolved_variables.append(variable_key)
            else:
                raise RuntimeError(f'Unknown variable "{variable_key}"')
        resolved_variables = remove_duplicates(resolved_variables)
        return resolved_variables
    
    def resolve_class_labels(self, class_labels:Dict[Any, str]) -> Dict[str, Any]:
        resolved_class_labels = {}
        for label, samples in class_labels.items():
            resolved_samples = self.resolve_samples(samples)
            for sample in resolved_samples:
                if sample not in resolved_class_labels:
                    resolved_class_labels[sample] = label
                else:
                    raise RuntimeError(f'Multiple class labels found for the sample "{sample}"')
        return resolved_class_labels
    
    def get_analysis_data_format(self) -> str:
        return self.config["data_storage"]["analysis_data_arrays"]["storage_format"]
    
    def get_event_index_variable(self):
        if "event_number" not in self.names:
            raise RuntimeError('No event index variable defined.')
        return self.names["event_number"]
    
    def get_blind_sample_name(self, sample:str):
        return f"{sample}_blind" if self.is_data_sample(sample) else sample
    
    def is_data_sample(self, sample:str):
        """Check whether a given sample is the observed data. Analysis specific, should be overridden.
        """
        return "data" in sample