from typing import Optional, List, Dict, Union, Callable
import os
import glob
import json
import math

import numpy as np

from quickstats import semistaticmethod, ConfigurableObject, ConfigUnit
from quickstats.utils.common_utils import (combine_dict, reindex_dataframe,
                                           filter_dataframe_by_index_values)
from quickstats.utils.string_utils import split_str
from .analysis_path_manager import AnalysisPathManager
from .config_templates import SampleConfig

class NTupleProcessTool(ConfigurableObject):
    """ Tool for processing root ntuples
    """

    config : ConfigUnit(SampleConfig)
    
    DEFAULT_SAMPLE_OUTNAME             = "{sample_name}_{sample_type}.root"
    DEFAULT_SYST_SAMPLE_OUTNAME        = "{sample_name}_{syst_name}_{syst_var}_{sample_type}.root"
    DEFAULT_MERGED_SAMPLE_OUTNAME      = "{sample_name}.root"
    DEFAULT_MERGED_SYST_SAMPLE_OUTNAME = "{sample_name}_{syst_name}_{syst_var}.root"
    DEFAULT_CUTFLOW_OUTNAME            = "cutflow_{sample_name}_{sample_type}.csv"
    DEFAULT_WEIGHT_OUTNAME             = "yield_{sample_name}_{sample_type}.json"
    DEFAULT_MERGED_CUTFLOW_OUTNAME     = "cutflow_{sample_name}.csv"
    
    @property
    def sample_config(self):
        return self.config
    
    @property
    def syst_theme_list(self):
        return self._syst_theme_list

    @property
    def sample_list(self):
        return self._sample_list
    
    @property
    def merge_sample_map(self):
        return self._merge_sample_map
    
    @property
    def sample_type_list(self):
        return self._sample_type_list
    
    @property
    def syst_name_list(self):
        return self._syst_name_list
    
    @property
    def sample_df(self):
        return self._sample_df
    
    @property
    def attribute_df(self):
        return self._attribute_df
    
    def __init__(self, sample_config:Union[Dict, str],
                 outdir:str='output',
                 process_config:Optional[Union["RooProcessConfig", str]]=None,
                 process_flags:Optional[List[str]]=None,
                 cache:bool=True,
                 use_template:bool=False,
                 multithread:bool=True,
                 data_service:Optional[str]=None,
                 data_service_options:Optional[Dict]=None,                 
                 backend:Optional[str]=None,
                 backend_options:Optional[Dict]=None,
                 verbosity:Optional[Union[int, str]]="INFO",
                 **kwargs):
        
        super().__init__(verbosity=verbosity)
        
        self.outdir = outdir
        self.path_manager = AnalysisPathManager(base_path=outdir)
        self.path_manager.set_directory("ntuple", "ntuples")
        self.path_manager.set_directory("cutflow", "cutflow")
        
        self.load_sample_config(sample_config)
        
        self.processor = None        
        if process_config is not None:
            self.load_process_config(process_config,
                                     cache=cache,
                                     use_template=use_template,
                                     multithread=multithread,
                                     data_service=data_service,
                                     data_service_options=data_service_options,
                                     backend=backend,
                                     backend_options=backend_options,
                                     **kwargs)
            
        if process_flags is not None:
            self.process_flags = list(process_flags)
        else:
            self.process_flags = []
        
        self.cutflow_report = None
        self.process_metadata = {}
        
    def load_sample_config(self, config_source:Union[Dict, str]):
        if isinstance(config_source, str):
            if not os.path.exists(config_source):
                raise FileNotFoundError(f'config file "{config_source}" does not exist')
            config_path = os.path.abspath(config_source)
            self.path_manager.set_file("sample_config", config_path)
        self.config.load(config_source)
            
        if 'Nominal' in self.sample_config['systematic_samples']:
            raise ValueError('Nominal samples should be placed in the "samples" key '
                             '(instead of "systematic_samples")')
        sample_list = list(self.sample_config['samples'])
        self._syst_theme_list = list(self.sample_config['systematic_samples'])
        for syst_theme in self.syst_theme_list:
            sample_list.extend(list(self.sample_config['systematic_samples'][syst_theme]))
        self._syst_theme_list.append('Nominal')
        import pandas as pd
        self._sample_list = pd.unique(np.array(sample_list))
        merge_sample_map = combine_dict(self.sample_config.get('merge_samples', {}))
        if not merge_sample_map:
            merge_sample_map = {sample: [sample] for sample in self.sample_list}
        else:
            # fill missing samples
            for sample in self.sample_list:
                if ((sample not in merge_sample_map) and 
                    all(sample not in samples for samples in merge_sample_map.values())):
                    merge_sample_map[sample] = [sample]
        self._merge_sample_map = merge_sample_map
        self._sample_df = self.get_sample_df()
        self._sample_type_list = list(self.sample_df.index.get_level_values('sample_type').unique())
        self._attribute_df = self.get_attribute_df(self.sample_df)
        syst_name_list = []
        for syst_names in self.sample_config['systematics'].values():
            syst_name_list.extend(syst_names)
        self._syst_name_list = pd.unique(np.array(syst_name_list))
    
    def get_sample_df(self):
        sample_data = []
        samples = combine_dict(self.sample_config['systematic_samples'],
                               {'Nominal': self.sample_config['samples']})
        for syst_theme in samples:
            for sample in samples[syst_theme]:
                for sample_type, filepaths in samples[syst_theme][sample].items():
                    if isinstance(filepaths, str):
                        filepaths = [filepaths]
                    for index, filepath in enumerate(filepaths):
                        data = {
                            'syst_theme': syst_theme,
                            'sample': sample,
                            'sample_type': sample_type,
                            'file_index': index,
                            'filepath': filepath
                        }
                        sample_data.append(data)
        index_list = ['syst_theme', 'sample', 'sample_type', 'file_index']
        import pandas as pd
        sample_df = pd.DataFrame(sample_data).set_index(index_list)
        return sample_df
    
    def get_attribute_df(self, sample_df):
        sample_df = sample_df.reset_index()[['syst_theme', 'sample', 'sample_type']]
        tuple_data = list(sample_df.itertuples(index=False, name=None))
        tuple_data = list(dict.fromkeys(tuple_data))
        attribute_data = {'syst_theme': [], 'sample':[], 'syst_name': [], 'syst_var':[],
                          'sample_type':[]}
        for syst_theme, sample, sample_type in tuple_data:
            if syst_theme == 'Nominal':
                attribute_data['syst_theme'].append(syst_theme)
                attribute_data['sample'].append(sample)
                attribute_data['syst_name'].append("")
                attribute_data['syst_var'].append("")
                attribute_data['sample_type'].append(sample_type)
                continue
            for syst_name in self.sample_config['systematics'][syst_theme]:
                for syst_var in ['1up', '1down']:
                    attribute_data['syst_theme'].append(syst_theme)
                    attribute_data['sample'].append(sample)
                    attribute_data['syst_name'].append(syst_name)
                    attribute_data['syst_var'].append(syst_var)
                    attribute_data['sample_type'].append(sample_type)
        import pandas as pd
        index_list = ['syst_theme', 'sample', 'syst_name', 'sample_type', 'syst_var']
        attribute_df = pd.DataFrame(attribute_data).set_index(index_list)
        return attribute_df
    
    def load_process_config(self, config_source:Union["RooProcessConfig", str], **kwargs):
        from quickstats.components import RooProcessor
        self.processor = RooProcessor(config_source,
                                      verbosity=self.stdout.verbosity,
                                      **kwargs)
        if isinstance(config_source, str):
            self.path_manager.set_file("process_config", os.path.abspath(config_source))
        
    def get_validated_syst_themes(self, syst_themes:Optional[List[str]]=None):
        if syst_themes is None:
            return [theme for theme in list(self.syst_theme_list) if theme != 'Nominal']
        invalid_syst_themes = list(set(syst_themes) - set(self.syst_theme_list))
        if invalid_syst_themes:
            raise ValueError(f'the following systematic themes are not defined in the sample config: '
                             f'{", ".join(invalid_syst_themes)}')
        return list(syst_themes)
        
    def get_validated_samples(self, samples:Optional[List[str]]=None, merged:bool=False):
        if merged:
            sample_list = list(self.merge_sample_map)
        else:
            sample_list = self.sample_list
        if samples is None:
            samples = sample_list
        invalid_samples = list(set(samples) - set(sample_list))
        if invalid_samples:
            raise ValueError(f'the following samples are not defined in the sample config: '
                             f'{", ".join(invalid_samples)}')
        return list(samples)
    
    def get_validated_sample_types(self, sample_types:Optional[List[str]]=None):
        if sample_types is None:
            return list(self.sample_type_list)
        invalid_sample_types = list(set(sample_types) - set(self.sample_type_list))
        if invalid_sample_types:
            raise ValueError(f'the following sample types are not defined in the sample config: '
                             f'{", ".join(invalid_sample_types)}')
        return list(sample_types)
    
    def get_validated_syst_names(self, syst_names:Optional[List[str]]=None):
        if syst_names is None:
            return self.syst_name_list
        invalid_syst_names = list(set(syst_names) - set(self.syst_name_list))
        if invalid_syst_names:
            raise ValueError(f'the following systematic names are not defined in the sample config: '
                             f'{", ".join(invalid_syst_names)}')
        return list(syst_names)
    
    def get_syst_names_from_theme(self, syst_theme:str):
        return list(self.sample_config['systematics'].get(syst_theme, []))
    
    def get_selected_paths(self, samples:Optional[List[str]]=None,
                           sample_types:Optional[List[str]]=None,
                           syst_themes:Optional[List[str]]=None,
                           fullpath:bool=True,
                           fmt:str="dict"):
        samples = self.get_validated_samples(samples)
        sample_types = self.get_validated_sample_types(sample_types)
        syst_themes = self.get_validated_syst_themes(syst_themes)
        df = self.sample_df
        selected_df = filter_dataframe_by_index_values(df, (syst_themes, samples, sample_types),
                                                       ('syst_theme', 'sample', 'sample_type'))


        if fullpath:
            sample_dir = self.sample_config['sample_dir']
            for sample_type in self.sample_type_list:
                sample_subdir = self.sample_config['sample_subdir'].get(sample_type, '')
                # # need to also consider friends
                path_lambda = lambda x: ";".join([os.path.join(sample_dir, sample_subdir, path) for path in split_str(x, sep=";")])
                mask = selected_df.index.get_level_values('sample_type') == sample_type
                selected_df.loc[mask, ['filepath']] = selected_df.loc[mask, 'filepath'].apply(path_lambda)
        # reindex to the order given in the arguments
        selected_df = reindex_dataframe(selected_df, (syst_themes,
                                                      samples,
                                                      sample_types))
        if fmt.lower() in ["dataframe", "df"]:
            return selected_df
        elif fmt.lower() == "dict":
            result = {}
            iter_data = selected_df.reset_index().itertuples(index=False, name=None)
            for syst_theme, sample, sample_type, _, filepath in iter_data:
                if syst_theme not in result:
                    result[syst_theme] = {}
                if sample not in result[syst_theme]:
                    result[syst_theme][sample] = {}
                if sample_type not in result[syst_theme][sample]:
                    result[syst_theme][sample][sample_type] = []
                result[syst_theme][sample][sample_type].append(filepath)
            return result
        else:
            raise ValueError(f'unsupported format: {fmt}')
    
    @semistaticmethod
    def get_sample_outpath(self, sample_config:Dict, outdir:str):
        sample_name = sample_config["sample"]
        sample_type = sample_config["sample_type"]
        basename = self.DEFAULT_SAMPLE_OUTNAME.format(sample_name=sample_name,
                                                      sample_type=sample_type)
        return os.path.join(outdir, basename)
    
    @semistaticmethod
    def get_syst_sample_outpath(self, sample_config:Dict, outdir:str):
        sample_name = sample_config["sample"]
        sample_type = sample_config["sample_type"]
        syst_theme = sample_config["syst_theme"]
        syst_name = sample_config["syst_name"]
        syst_var = sample_config["syst_var"]
        basename = self.DEFAULT_SYST_SAMPLE_OUTNAME.format(sample_name=sample_name,
                                                           sample_type=sample_type,
                                                           syst_var=syst_var,
                                                           syst_name=syst_name)
        return os.path.join(outdir, syst_theme, basename)
    
    @semistaticmethod
    def get_merged_sample_outpath(self, sample_config:Dict, outdir:str):
        sample_name = sample_config["sample"]
        basename = self.DEFAULT_MERGED_SAMPLE_OUTNAME.format(sample_name=sample_name)        
        return os.path.join(outdir, basename)
    
    @semistaticmethod
    def get_merged_syst_sample_outpath(self, sample_config:Dict, outdir:str):
        sample_name = sample_config["sample"]
        syst_theme = sample_config["syst_theme"]
        syst_name = sample_config["syst_name"]
        syst_var = sample_config["syst_var"]
        basename = self.DEFAULT_MERGED_SYST_SAMPLE_OUTNAME.format(sample_name=sample_name,
                                                                  syst_var=syst_var,
                                                                  syst_name=syst_name)        
        return os.path.join(outdir, syst_theme, basename)
    
    @semistaticmethod
    def get_cutflow_outpath(self, sample_config:Dict, outdir:str):
        sample_name = sample_config["sample"]
        sample_type = sample_config["sample_type"]
        basename_cutflow = self.DEFAULT_CUTFLOW_OUTNAME.format(sample_name=sample_name,
                                                               sample_type=sample_type)
        basename_weight  = self.DEFAULT_WEIGHT_OUTNAME.format(sample_name=sample_name,
                                                              sample_type=sample_type)
        return [os.path.join(outdir, basename_cutflow), os.path.join(outdir, basename_weight)]  
    
    @semistaticmethod
    def get_merged_cutflow_outpath(self, sample_config:Dict, outdir:str):
        sample_name = sample_config["sample"]
        basename = self.DEFAULT_MERGED_CUTFLOW_OUTNAME.format(sample_name=sample_name)
        return os.path.join(outdir, basename)    
                    
    def prerun_process(self, sample_config:Dict):
        pass
    
    def process_syst_samples(self, syst_names:Optional[List[str]]=None,
                             syst_themes:Optional[List[str]]=None,
                             samples:Optional[List[str]]=None,
                             sample_types:Optional[List[str]]=None):
        if self.processor is None:
            raise RuntimeError("processor not initialized (probably missing a process config)")
        paths = self.get_selected_paths(syst_themes=syst_themes,
                                        samples=samples,
                                        sample_types=sample_types)
        outdir = self.path_manager.base_path
        syst_names = self.get_validated_syst_names(syst_names)
        for syst_theme in paths:
            for sample in paths[syst_theme]:
                self.processor.set_flags(self.process_flags)
                for sample_type in paths[syst_theme][sample]:
                    sample_paths = paths[syst_theme][sample][sample_type]
                    sample_config = {
                        "name": sample,
                        "path": sample_paths,
                        "type": sample_type
                    }
                    syst_names_by_theme = self.get_syst_names_from_theme(syst_theme)
                    syst_names_by_theme = np.intersect1d(syst_names_by_theme, syst_names)
                    for syst_name in syst_names_by_theme:
                        self.processor.global_variables['sample'] = sample
                        self.processor.global_variables['sample_type'] = sample_type
                        self.processor.global_variables['syst_theme'] = syst_theme
                        self.processor.global_variables['syst_name'] = syst_name
                        self.processor.global_variables['outdir'] = outdir
                        self.prerun_process(sample_config)
                        self.processor.run(sample_paths)
                        self.processor.clear_global_variables()

    def process_samples(self, samples:Optional[Union[List[str], str]]=None,
                        sample_types:Optional[Union[List[str], str]]=None):
        if isinstance(samples, str):
            samples = [samples]
        if isinstance(sample_types, str):
            sample_types = [sample_types]
        if self.processor is None:
            raise RuntimeError("processor not initialized (probably missing a process config)")
        paths = self.get_selected_paths(syst_themes=['Nominal'],
                                        samples=samples,
                                        sample_types=sample_types)
        if not paths:
            self.stdout.warning('No inputs matching the given conditions. Skipped processing.')
            return None
        paths = paths['Nominal']
        outdir = self.path_manager.base_path
        for sample in paths:
            self.processor.set_flags(self.process_flags)
            for sample_type in paths[sample]:
                sample_paths = paths[sample][sample_type]
                sample_config = {
                    "name": sample,
                    "path": sample_paths,
                    "type": sample_type
                }
                self.processor.global_variables['sample'] = sample
                self.processor.global_variables['sample_type'] = sample_type
                self.processor.global_variables['outdir'] = outdir
                self.prerun_process(sample_config)
                self.processor.run(sample_paths)
                self.set_process_metadata(sample, sample_type,
                                          self.processor.result_metadata.copy())
                self.processor.clear_global_variables()

    def set_process_metadata(self, sample:str,
                             sample_type:str,
                             metadata:Dict):
        if sample not in self.process_metadata:
            self.process_metadata[sample] = {}
        self.process_metadata[sample][sample_type] = metadata
                
    def merge_outputs(self, source_path_func:Callable,
                      target_path_func:Callable,
                      merge_func:Callable,
                      outdir:str,
                      samples:Optional[List[str]]=None,
                      syst_themes:Optional[List[str]]=None,
                      syst_names:Optional[List[str]]=None,
                      subdirs:Optional[List[str]]=None):
        if subdirs is None:
            subdirs = [""]
        syst_themes = self.get_validated_syst_themes(syst_themes)
        syst_names = self.get_validated_syst_names(syst_names)
        if "Nominal" in syst_themes:
            syst_names = np.concatenate([syst_names, [""]])
        attribute_df = filter_dataframe_by_index_values(self.attribute_df,
                                                        (syst_themes, syst_names),
                                                        ('syst_theme', 'syst_name'))
        samples = self.get_validated_samples(samples, merged=True)
        group_level = ['syst_theme', 'syst_name', 'syst_var']
        for subdir in subdirs:
            sample_subdir = os.path.join(outdir, subdir)
            for sample in samples:
                subsamples = self.merge_sample_map[sample]
                filtered_attribute_df = filter_dataframe_by_index_values(attribute_df, subsamples, 'sample')
                for indices, selected_df in filtered_attribute_df.groupby(level=group_level):
                    sample_subattributes = selected_df.reset_index().to_dict('records')
                    source_files = []
                    for subattributes in sample_subattributes:
                        file = source_path_func(subattributes, sample_subdir)
                        source_files.append(file)
                    main_attributes = dict(zip(group_level, indices))
                    main_attributes['sample'] = sample
                    target_file = target_path_func(main_attributes, sample_subdir)
                    if main_attributes['syst_theme'] == 'Nominal':
                        self.stdout.info(f'Merging outputs for the sample "{sample}"')
                    else:
                        syst_name = main_attributes['syst_name']
                        syst_var = main_attributes['syst_var']
                        self.stdout.info(f'Merging outputs for the sample "{sample}" '
                                         f'(systematic = "{syst_name}", variation = "{syst_var}")')
                    merge_func(source_files, target_file)
    
    def merge_samples(self, samples:Optional[List[str]]=None, subdirs:Optional[List[str]]=None):
        outdir = self.path_manager.get_directory("ntuple")
        self.merge_outputs(self.get_sample_outpath,
                           self.get_merged_sample_outpath,
                           self._merge_samples_with_hadd,
                           outdir=outdir,
                           samples=samples,
                           syst_themes=['Nominal'],
                           subdirs=subdirs)
        
    def merge_syst_samples(self, samples:Optional[List[str]]=None,
                           syst_names:Optional[List[str]]=None,
                           syst_themes:Optional[List[str]]=None,
                           subdirs:Optional[List[str]]=None):
        outdir = self.path_manager.get_directory("ntuple")
        self.merge_outputs(self.get_syst_sample_outpath,
                           self.get_merged_syst_sample_outpath,
                           self._merge_samples_with_hadd,
                           outdir=outdir,
                           samples=samples,
                           syst_themes=syst_themes,
                           syst_names=syst_names,
                           subdirs=subdirs)
    
    def _merge_samples_with_hadd(self, filenames:List[str], outname:str):
        for filename in filenames:
            if not os.path.exists(filename):
                raise FileNotFoundError(f'missing ntuple file "{filename}"')
        hadd_cmd = "hadd -f {} {}".format(outname, " ".join(filenames))
        os.system(hadd_cmd)
            
    def merge_cutflows(self, samples:Optional[List[str]]=None, subdirs:Optional[List[str]]=None):
        outdir = self.path_manager.get_directory("cutflow")
        self.merge_outputs(self.get_cutflow_outpath,
                           self.get_merged_cutflow_outpath,
                           self._merge_cutflow_data,
                           outdir=outdir,
                           samples=samples,
                           subdirs=subdirs,
                           syst_themes=['Nominal'])
    
    def _process_exported_data(self, df, filename:str=None):
        import pandas as pd
        if (filename is None) or (not os.path.exists(filename)):
            return df, None
        with open(filename, 'r') as file:
            data = json.load(file)
        cutflow_names = df['name'].values
        yield_values = [data.pop(name, None) for name in cutflow_names]
        if (None in yield_values) and not (len(set(yield_values)) == 1):
            self.stdout.warning(f"Missing some cutflow entries from the yield file {filename}")
        if not data:
            return df, yield_values
        extra_cutflow = {}
        extra_yields = {}
        for key, value in data.items():
            if key.startswith("CUTFLOW"):
                key = key.strip("CUTFLOW").strip()
                extra_cutflow[key] = int(value)
            elif key.startswith("WEIGHT"):
                key = key.strip("WEIGHT").strip()
                extra_yields[key] = float(value)
        n_events = df['all'].values[0]
        rows = []
        for key, value in extra_cutflow.items():
            row = {"name": key, "all": None, "pass": value,
                   "efficiency": None,
                   "cumulative_efficiency": 100 * (value / n_events)}
            rows.append(row)
            yield_values.append(extra_yields.get(key, None))
        df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
        return df, yield_values
    
    def _get_efficiency_values(self, df, weight_column:str):
        weight_values = df[weight_column].values
        prev_pass_values = df['all'].values
        this_pass_values = df['pass'].values
        efficiency = [100]
        cumul_efficiency = [100]
        for i in range(1, len(weight_values)):
            cumul_efficiency.append(100 * (weight_values[i] / weight_values[0]))
            prev_pass_value = prev_pass_values[i]
            if (prev_pass_value is None) or math.isnan(prev_pass_value):
                efficiency.append(None)
                continue
            last_idx = np.where(this_pass_values == prev_pass_value)
            if len(last_idx[0]) == 0:
                raise RuntimeError("failed to calculate efficiency")
            efficiency.append(100 * (weight_values[i] / weight_values[last_idx][0]))
        return efficiency, cumul_efficiency
    
    def _merge_cutflow_data(self, filenames:List[str], outname:str):
        import pandas as pd
        merged_df = None
        for filename in filenames:
            if isinstance(filename, (list, tuple)):
                # first file contains cutflow information
                # second file contains weight information                
                assert len(filename) == 2
                cutflow_filename = filename[0]
                weight_filename = filename[1]
            else:
                cutflow_filename = filename
                weight_filename = None
            if not os.path.exists(cutflow_filename):
                raise FileNotFoundError(f'missing cutflow file "{cutflow_filename}"')
            cutflow_df = pd.read_csv(cutflow_filename)
            cutflow_df, yield_values = self._process_exported_data(cutflow_df, weight_filename)
            if merged_df is None:
                merged_df = cutflow_df.copy()
                if yield_values is not None:
                    merged_df['yield'] = yield_values
            else:
                merged_df['all']  += cutflow_df['all']
                merged_df['pass'] += cutflow_df['pass']
                if 'yield' in merged_df:
                    if yield_values is None:
                        raise RuntimeError(f'missing weight file that is in association with the '
                                           f'cutflow file "{cutflow_filename}"')
                    merged_df['yield'] += yield_values
        efficiency, cumul_efficiency = self._get_efficiency_values(merged_df, 'pass')
        merged_df['efficiency'] = efficiency
        merged_df['cumulative_efficiency'] = cumul_efficiency
        if 'yield' in merged_df:
            yield_efficiency, yield_cumul_efficiency = self._get_efficiency_values(merged_df, 'yield')
            merged_df['yield_efficiency'] = yield_efficiency
            merged_df['yield_cumulative_efficiency'] = yield_cumul_efficiency
        merged_df.to_csv(outname, index=False)
        self.stdout.info(f'Saved cutflow data as "{outname}"')
        
    def load_cutflow_report(self, samples:Optional[List[str]]=None):
        import pandas as pd
        samples = self.get_validated_samples(samples, merged=True)
        
        cutflow_dir   = self.path_manager.get_directory("cutflow")
        
        cutflow_report = {}
        for sample in self.merge_sample_map:
            if sample not in samples:
                continue
            sample_config = {
                "sample": sample
            }
            cutflow_file = self.get_merged_cutflow_outpath(sample_config, cutflow_dir)
            if not os.path.exists(cutflow_file):
                self.stdout.warning(f'Missing cutflow file for the sample "{sample}".')
                continue
            df = pd.read_csv(cutflow_file)
            cutflow_report[sample] = df
            
        self.cutflow_report = cutflow_report

    def plot_cutflow_report(self, samples:Optional[List[str]]=None,
                            label_map:Optional[Dict]=None,
                            rotation:int=15,
                            pad:float=3.0,
                            figsize=(17,8)):

        import matplotlib.pyplot as plt
        
        plt.rcParams['figure.dpi'] = 200
        
        # Load the cutflow report if it doesn't exist yet
        if self.cutflow_report is None:
            self.load_cutflow_report(samples)

        colors = ["#36B1BF","#F2385A","#FDC536"]  # turqouise, pink, yellow

        if samples is None:
            samples = list(self.cutflow_report.keys())
            
        if label_map is None:
            label_map = {}
            
        # Loop over each sample and make a plot of the cutflow
        for sample in samples: 
            
            if sample not in self.cutflow_report:
                self.stdout.warning(f'Missing cutflow report for the sample "{sample}". Skipped.')
                continue

            df = self.cutflow_report[sample].fillna(0)

            cut_labels = [label_map.get(name, name) for name in df["name"]]

            fig, axs = plt.subplots(3, 1, figsize=figsize)
            fig.tight_layout(pad=pad)

            for i in range(len(axs)): # set x-axes style
                axs[i].tick_params(axis='x', rotation=rotation, labelsize=10) 

            # Yields bar chart 
            axs[0].bar(cut_labels, df["yield"], color=colors[0])
            axs[0].set_ylabel("Yields", fontsize=14)
            
            # Efficiency bar chart 
            axs[1].bar(cut_labels, df["yield_efficiency"], color=colors[1])
            axs[1].set_ylabel("Efficiency [%]", fontsize=14)
            
            # Culmulative efficiency bar chart 
            axs[2].bar(cut_labels, df["yield_cumulative_efficiency"], color=colors[2])
            axs[2].set_ylabel("Cumulative Efficiency [%]", fontsize=14)

            fig.suptitle(f"Sample: {sample}", fontsize=20, y=0.98)
            
            plt.show()

    def copy_remote_samples(self, samples:Optional[Union[List[str], str]]=None,
                            sample_types:Optional[Union[List[str], str]]=None,
                            cache:bool=True,
                            cachedir:str='/tmp',
                            parallel:bool=False):
        if isinstance(samples, str):
            samples = [samples]
        if isinstance(sample_types, str):
            sample_types = [sample_types]
        paths = self.get_selected_paths(syst_themes=['Nominal'],
                                        samples=samples,
                                        sample_types=sample_types)
        if not paths:
            self.stdout.warning('No inputs matching the given conditions. Skipped.')
        paths = paths['Nominal']
        filenames = []
        for sample in paths:
            for sample_type in paths[sample]:
                filenames.extend(paths[sample][sample_type])
        from quickstats.interface.root import TFile
        TFile.copy_remote_files(filenames, cache=cache,
                                cachedir=cachedir, parallel=parallel)