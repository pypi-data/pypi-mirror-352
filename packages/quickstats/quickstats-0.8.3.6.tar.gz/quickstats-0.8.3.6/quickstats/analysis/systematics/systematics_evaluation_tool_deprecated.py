from typing import List, Union ,Optional, Dict
import os
import json
from functools import partial

from .gaussian_shape_systematics import GaussianShapeSystematics
from .normalization_systematics import NormalizationSystematics
from .base_systematics import SystematicType
from quickstats.utils.common_utils import execute_multi_tasks
from quickstats import AbstractObject, DescriptiveEnum, ConfigurableObject

from quickstats.analysis.config_format_templates import DEFAULT_SYSTEMATIC_EVAL_CONFIG
    
class SystErrorEvalMethod(DescriptiveEnum):
    ANALYTIC = (0, "Evaluate systematic error analytically"),
    BOOTSTRAP = (1, "Evaluate systematic error via bootstrap")
    
class ShapeSystEvalMethod(DescriptiveEnum):
    FIT = (0, "Evaluate shape systematic via a fit")
    MEAN_IQR = (1, "Evaluate shape systematic using the mean inter-quartile-range")

class SystPartitionMethod(DescriptiveEnum):
    INDIVIDUAL = (0, "No partition")
    BOOTSTRAP = (1, "Partition using bootstrap toys")
    JACKNIFE = (2, "Partition using the jacknife method")
    
FILE_NAMES = {
    "individual_detailed"  : "{syst_type}_systematics_detailed.json",
    "individual_processed" : "{syst_type}_systematics_processed.json",
    "individual_summary"   : "{syst_type}_systematics.json",
    "combined_summary"     : "systematics.json",
    "input_tree": "{campaign}_{process}_{syst_theme}.root"
}    
    
class SystematicsEvaluationTool(ConfigurableObject):
    
    CONFIG_FORMAT = DEFAULT_SYSTEMATIC_EVAL_CONFIG

    @property
    def cache(self):
        return self._cache

    @property
    def syst_theme_list(self):
        return self._syst_theme_list

    @property
    def sample_list(self):
        return self._sample_list
    
    @property
    def sample_type_list(self):
        return self._sample_type_list

    @property
    def category_list(self):
        return self._category_list
    
    @property
    def sample_path_df(self):
        return self._sample_path_df
    
    @property
    def sample_config(self):
        return self._sample_config
    
    @property
    def eval_config(self):
        return self._eval_config
    
    def __init__(self, config_source:Optional[Union[Dict, str]]=None,
                 disable_config_message:bool=False,
                 cache:bool=True,
                 verbosity:Optional[Union[int, str]]="INFO") -> None:
        super().__init__(config_source=config_source,
                         disable_config_message=disable_config_message,
                         verbosity=verbosity)
        self.setup_root_env()
        self.set_cache(cache)
        self.setup_norm_syst_tool()
        self.setup_shape_syst_tool()
        
        
    def set_eval_config(self, config_source:Optional[Union[Dict, str]]=None):
        self._eval_config = self.SampleConfigCls(config_source).config

    def setup_root_env(self):
        import ROOT
        ROOT.TH1.SetDefaultSumw2(1)
        if not self.stdout.verbosity < 'INFO':
            ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.INFO)
            ROOT.RooMsgService.instance().setSilentMode(1)
            ROOT.RooMsgService.instance().setStreamStatus(1, False)

    def set_cache(self, cache:bool=True):
        self._cache = cache
        
    def setup_norm_syst_tool(self):
        self.norm_syst_tool = NormalizationSystematics()
    
    def setup_shape_syst_tool(self):
        self.shape_syst_module = GaussianShapeSystematics()

    def get_validated_syst_themes(self, syst_themes:Optional[List[str]]=None):
        if syst_themes is None:
            return list(self.syst_theme_list)
        invalid_syst_themes = list(set(syst_themes) - set(self.syst_theme_list))
        if invalid_syst_themes:
            raise ValueError(f'the following systematic themes are not defined in the systematics config: '
                             f'{", ".join(invalid_syst_themes)}')
        return list(syst_themes)

    def get_validated_samples(self, samples:Optional[List[str]]=None):
        if samples is None:
            return list(self.sample_list)
        invalid_samples = list(set(samples) - set(self.sample_list))
        if invalid_samples:
            raise ValueError(f'the following samples are not defined in the systematics config: '
                             f'{", ".join(invalid_samples)}')
        return list(samples)

    def evaluate(self, samples:Optional[List[str]]=None,
                 syst_themes:Optional[List[str]]=None,
                 syst_types:Optional[List[str]]=None):
        pass
    
    def evaluate_yield_systematics(self, samples:Optional[List[str]]=None,
                                   syst_themes:Optional[List[str]]=None):
        input_paths = self.get_selected_paths(samples=samples, syst_themes=syst_themes)
        executor = self.norm_syst_module.get_systematics_from_root_file
        for process in input_paths:
            categories = self.get_categories(process)
            for syst_theme in input_paths[process]:
                syst_list = self.systematics_by_theme[syst_theme]
                filename = input_paths[process][syst_theme]
                executor(filename, categories, syst_list, process, append=True)
                
    def create_bootstrap_trees(self, cache:Optional[bool]=None):
        if cache is None:
            cache = self.cache
        tree_paths = self.get_input_tree_paths()
        cache = self.config['cache']
        parallel = self.config['parallel']
        executor = partial(self.shape_syst_module.create_bootstrap_trees_from_root_file, cache=cache)
        args_filenames = []
        args_categories = []
        args_syst_list = []
        args_processes = []
        for process in tree_paths:
            categories = self.get_categories(process)
            for syst_theme in tree_paths[process]:
                syst_list = self.systematics_by_theme[syst_theme]
                filename = tree_paths[process][syst_theme]
                args_filenames.append(filename)
                args_categories.append(categories)
                args_syst_list.append(syst_list)
                args_processes.append(process)
        task_args = (args_filenames, args_categories, args_syst_list, args_processes)
        execute_multi_tasks(executor, *task_args, parallel=parallel)
                
    def evaluate_shape_systematics(self):
        parallel = self.config['parallel']
        save_toys = self.config['save_toys']
        cache = self.config['cache']
        executor = partial(self.shape_syst_module.get_bootstrap_systematics,
                           parallel=parallel, cache=cache, save_toys=save_toys)
        for key in self.processes:
            process_name = self.process_map[key]
            categories = self.get_categories(process_name)
            systematics_list = []
            for syst_theme in self.syst_themes:
                if syst_theme not in self.syst_config["inputs"][key]:
                    continue
                systematics_list += self.systematics_by_theme[syst_theme]
            executor(process_name, categories, systematics_list)
            
    def post_process(self, syst_types=None):
        modules = {"yield": self.yield_syst_module, "shape": self.shape_syst_module}
        if syst_types is None:
            syst_types = self.syst_types
        for syst_type in syst_types:
            # discard certain unwanted systematics by pattern
            if self.discard_data is not None:
                for item in self.discard_data:
                    self.stdout.info("Discarding `{}` from {} systematics".format(item, syst_type))
                    modules[syst_type].discard(**self.discard_data[item])
            self.stdout.info("Post-processing {} systematics results".format(syst_type))
            modules[syst_type].post_process(merge_condition=self.merge_condition)
            
    def load_result(self, syst_types=None, mode="processed"):
        modules = {"yield": self.yield_syst_module, "shape": self.shape_syst_module}
        if syst_types is None:
            syst_types = self.syst_types
        for syst_type in syst_types:
            dirname = os.path.join(self.base_path, "results")
            if mode == "detailed":
                basename = self.FILE_NAMES['individual_detailed'].format(syst_type=syst_type)
            elif mode == "processed":
                basename = self.FILE_NAMES['individual_processed'].format(syst_type=syst_type)
            else:
                raise ValueError("unknown mode: {}".format(mode))
            filename = os.path.join(dirname, basename)
            if os.path.exists(filename):
                modules[syst_type].load(filename)
                self.stdout.info("Loaded results for {} systematics from `{}`".format(syst_type, filename))
                modules[syst_type].processed = (mode == "processed")
            else:
                self.stdout.error("No saved results found for {} systematics (in `{}`)".format(syst_type, filename))
                
    def save_result(self, syst_types=None):
        modules = {"yield": self.yield_syst_module, "shape": self.shape_syst_module}
        if syst_types is None:
            syst_types = self.syst_types
        for syst_type in syst_types:
            dirname = os.path.join(self.base_path, "results")
            if modules[syst_type].processed:
                basename = self.FILE_NAMES['individual_processed'].format(syst_type=syst_type)
            else:
                basename = self.FILE_NAMES['individual_detailed'].format(syst_type=syst_type)
            filename = os.path.join(dirname, basename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            modules[syst_type].save(filename)
            self.stdout.info("Saved results for {} systematics in `{}`".format(syst_type, filename))
            
    def get_combined_summary(self):
        modules = {"yield": self.yield_syst_module, "shape": self.shape_syst_module}
        combined_result = {}
        for syst_type in self.syst_types:
            if modules[syst_type].dataframe is None:
                continue
            simplified_data = modules[syst_type].get_simplified_data()
            combined_result.update(simplified_data)
        return combined_result
    
    def save_combined_summary(self):
        combined_result = self.get_combined_summary()
        dirname = os.path.join(self.base_path, "results")
        basename = self.FILE_NAMES['combined_summary']
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filename = os.path.join(dirname, basename)
        with open(filename, 'w') as f:
            json.dump(combined_result, f, indent=2)
        self.stdout.info("Saved combined summary in `{}`".format(filename))
            
    def get_dataframe(self, syst_type, simplified=True):
        if syst_type == "yield":
            df = self.yield_syst_module.get_valid_dataframe("yield")
        elif syst_type == "shape":
            df = self.shape_syst_module.dataframe
        elif syst_type == "position_shape":
            df = self.shape_syst_module.get_valid_dataframe("position_shape")
        elif syst_type == "spread_shape":
            df = self.shape_syst_module.get_valid_dataframe("spread_shape")
        else:
            raise ValueError(f"invalid systematics type: {syst_type}")
        if simplified:
            columns = list(df.columns)
            to_drop = [i for i in columns if isinstance(i, tuple) and "rel_effect" not in i]
            if syst_type == "position_shape":
                to_drop += [i for i in columns if isinstance(i, tuple) and "position_shape" not in i]
            elif syst_type == "spread_shape":
                to_drop += [i for i in columns if isinstance(i, tuple) and "spread_shape" not in i]                
            df = df.drop(to_drop, axis=1)
        return df