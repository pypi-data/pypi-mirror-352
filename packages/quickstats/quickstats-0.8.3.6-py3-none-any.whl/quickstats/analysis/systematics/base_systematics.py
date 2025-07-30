from typing import Optional, Union, List, Dict
import json
import itertools

import numpy as np
import pandas as pd

from quickstats import DescriptiveEnum, semistaticmethod
from quickstats import ConfigurableObject, ConfigComponent, ConfigUnit
from quickstats.utils.common_utils import filter_dataframe_by_index_values, remove_duplicates
from quickstats.analysis.config_templates import SystematicEvalConfig

class SystematicType(DescriptiveEnum):

    Norm  = (0, "Normalization Systematics", "yield")
    Shape = (1, "Shape Systematics", "shape")

    
    __aliases__ = {
        "normalization": Norm,
        "yield": Norm
    }

    def __new__(cls, value:int, description:str="", name_prefix:str=""):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.name_prefix = name_prefix
        return obj

class BaseSystematics(ConfigurableObject):

    config : ConfigUnit(SystematicEvalConfig)

    INDICES = ['sample', 'syst_theme', 'systematics', 'category']
    
    PRIMARY_KEYS = ['up_rel_effect_val', 'down_rel_effect_val',
                    'up_rel_effect_err', 'down_rel_effect_err']
    
    SYST_TYPES = None
    
    ATOL = 1e-8
    RTOL = 1e-4
    
    DEFAULT_VARIATIONS = ['up', 'down']
    
    INPUT_PATH_FMT = "{array_dir}/{syst_theme}/{sample}.h5"
    
    def __init__(self, config_source:Optional[Union[Dict, str]]=None,
                 array_dir:str="arrays",
                 verbosity:Optional[Union[int, str]]="INFO",
                 **kwargs):
        """
        """
        super().__init__(verbosity=verbosity)
        self.config.load(config_source)
        self.array_dir = array_dir
        self.reset()
        
    def reset(self):
        self.dataframe = None
        self.processed = False
        
    def append(self, dataframe):
        if self.dataframe is None:
            self.dataframe = dataframe
        else:
            self.dataframe = dataframe.combine_first(self.dataframe)
    
    def _resolve_choices(self, full_list:List,
                         choices:Optional[List]=None,
                         name:str="choices"):
        if choices is None:
            return list(full_list)
        invalid_choices = list(set(choices) - set(full_list))
        if invalid_choices:
            raise ValueError(f'the following {name} are not defined in the config: '
                             f'{", ".join(invalid_choices)}')
        return list(choices)
    
    def resolve_samples(self, samples:Optional[List]=None):
        sample_list = list(self.config['samples'])
        if self.dataframe is not None:
            df_samples = list(self.dataframe.index.get_level_values('sample').unique())
            sample_list.extend(df_samples)
            sample_list = remove_duplicates(sample_list)
        return self._resolve_choices(sample_list,
                                     samples, 'samples')
    
    def resolve_syst_themes(self, syst_themes:Optional[List]=None):
        syst_theme_list = list(self.config['systematics'])
        # to take care of merging themes
        if self.dataframe is not None:
            df_syst_themes = list(self.dataframe.index.get_level_values('syst_theme').unique())
            syst_theme_list.extend(df_syst_themes)
            syst_theme_list = remove_duplicates(syst_theme_list)
        return self._resolve_choices(syst_theme_list,
                                     syst_themes, 'systematic themes')
    
    def resolve_syst_names(self, syst_names:Optional[List]=None):
        syst_name_list = []
        for names in self.config['systematics'].values():
            syst_name_list.extend(names)
        # to take care of merging names
        if self.dataframe is not None:
            df_syst_names = list(self.dataframe.index.get_level_values('systematics').unique())
            syst_name_list.extend(df_syst_names)
        syst_name_list = remove_duplicates(syst_name_list)
        return self._resolve_choices(syst_name_list,
                                     syst_names, 'systematics')
    
    def resolve_categories(self, categories:Optional[List]=None):
        category_list = self.get_categories()
        if self.dataframe is not None:
            df_categories = list(self.dataframe.index.get_level_values('category').unique())
            category_list.extend(df_categories)
            category_list = remove_duplicates(category_list)
        return self._resolve_choices(category_list,
                                     categories, 'categories')
    
    def get_syst_names_from_theme(self, syst_theme:str):
        return list(self.config['systematics'].get(syst_theme, []))
    
    def get_categories(self):
        return list(self.config['category_selection'])
    
    def get_category_selection(self, category:str):
        return self.config['category_selection'][category]
    
    def get_input_df(self, **kwargs):
        filename = self.INPUT_PATH_FMT.format(array_dir=self.array_dir, **kwargs)
        variation = kwargs['variation']
        if variation is None:
            key = f"{kwargs['syst_name']}"
        else:
            key = f"{kwargs['syst_name']}_1{kwargs['variation']}"
        df = pd.read_hdf(filename, key=key)
        return df
    
    @semistaticmethod
    def get_syst_types(self):
        if self.SYST_TYPES is None:
            return ['']
        return list(self.SYST_TYPES)
    
    def get_seeds(self, index_values):
        return np.sum(np.array([*index_values]), axis=1)
    
    def get_nom_toy_weights(self, df, n_toys:int):
        from quickstats.maths.statistics_jitted import random_poisson_elementwise_seed
        seeds = self.get_seeds(df.index.values)
        poisson_weights = random_poisson_elementwise_seed(seeds, n_toys)
        return poisson_weights
    
    def get_sys_toy_weights(self, df_nom, df_sys, n_toys:int, nom_weights:np.ndarray):
        from quickstats.maths.statistics_jitted import random_poisson_elementwise_seed
        com_idx = df_nom.index.intersection(df_sys.index)
        # all events common, use same weights
        if (len(com_idx) == len(df_sys)) and (len(df_nom) == len(df_sys)):
            return nom_weights
        com_nom_loc = df_nom.index.get_indexer_for(com_idx)
        com_sys_loc = df_sys.index.get_indexer_for(com_idx)
        poisson_weights = np.zeros((n_toys, len(df_sys)))
        poisson_weights[:, com_sys_loc] = nom_weights[:, com_nom_loc]
        uncom_sys_idx = df_sys.index.difference(df_nom.index)
        if len(uncom_sys_idx):
            uncom_sys_loc = df_sys.index.get_indexer_for(uncom_sys_idx)
            uncom_sys_seeds = self.get_seeds(uncom_sys_idx)
            poisson_weights[:, uncom_sys_loc] = random_poisson_elementwise_seed(uncom_sys_seeds, n_toys)
        return poisson_weights
    
    def format_column(self, col:str, syst_type:str):
        if not syst_type:
            return col
        return f"{syst_type}_{col}"
    
    def get_n_toys(self):
        return None
    
    def read_systematics_data(self, samples:Optional[List]=None,
                              syst_themes:Optional[List]=None,
                              syst_names:Optional[List]=None,
                              append:bool=True):
        samples = self.resolve_samples(samples)
        syst_themes = self.resolve_syst_themes(syst_themes)
        syst_names = self.resolve_syst_names(syst_names)
        category_selection = self.config['category_selection']
        categories = list(self.config['category_selection'])
        variations = list(self.DEFAULT_VARIATIONS)
        syst_data_list = []
        cat_df_nom = {}
        toy_weights_nom = {}
        n_toys = self.get_n_toys()

        for sample in samples:
            df_nom = self.get_input_df(syst_theme='Nominal',
                                       sample=sample,
                                       syst_name='Nominal',
                                       variation=None)
            for category in categories:
                selection = category_selection[category]
                cat_df_nom[category] = df_nom.query(selection).set_index(self.config['index']).sort_index()

            if n_toys is not None:
                self.stdout.info('Evaluating bootstrap weights for the nominal sample')
                for category in categories:
                    toy_weights_nom[category] = self.get_nom_toy_weights(cat_df_nom[category], n_toys)
                    
            for syst_theme in syst_themes:
                syst_names_by_theme = self.get_syst_names_from_theme(syst_theme)
                syst_names_by_theme = np.intersect1d(syst_names_by_theme, syst_names)
                self.stdout.info(f"Sample: {sample}\tSystematic Theme: {syst_theme}", bare=True)
                for syst_name in syst_names_by_theme:
                    self.stdout.info(f'Reading systematic data for the systematic "{syst_name}"')
                    syst_data = {}
                    for variation in variations:
                        df_sys = self.get_input_df(syst_theme=syst_theme,
                                                   sample=sample,
                                                   syst_name=syst_name,
                                                   variation=variation)
                        for category in categories:
                            if n_toys is not None:
                                kwargs = {'toy_weights_nom': toy_weights_nom[category]}
                            else:
                                kwargs = {}
                            selection = category_selection[category]
                            cat_df_sys = df_sys.query(selection).set_index(self.config['index']).sort_index()

                            cat_syst_data = self.process_systematics_data(cat_df_nom[category],
                                                                          cat_df_sys,
                                                                          variation=variation,
                                                                          **kwargs)
                            if category not in syst_data:
                                syst_data[category] = {
                                    'sample': sample,
                                    'syst_theme': syst_theme,
                                    'systematics': syst_name,
                                    'category': category
                                }
                            syst_data[category].update(cat_syst_data)
                            syst_data[category]['status'] = 1
                    syst_data_list.extend(syst_data.values())
        
        dataframe = pd.DataFrame(syst_data_list).set_index(self.INDICES)
        dataframe = self.process_systematics_dataframe(dataframe, variations=variations)
        if append:
            self.append(dataframe)
        return dataframe
    
    def process_systematics_dataframe(self, df, variations:Optional[List]=None):
        return df
    
    def resolve_primary_keys(self, syst_types:Optional[List]=None):
        raw_primary_keys = list(self.PRIMARY_KEYS)
        if syst_types is None:
            return raw_primary_keys
        primary_keys = []
        for syst_type in syst_types:
            for primary_key in raw_primary_keys:
                primary_keys.append(f"{syst_type}_{primary_key}")
        return primary_keys
    
    def sanity_check(self, check_dataframe:bool=True,
                     check_rel_effect:bool=False,
                     strict:bool=True):
        if check_dataframe or check_rel_effect:
            if self.dataframe is None:
                if strict:
                    raise RuntimeError("systematics dataframe not initialized")
                else:
                    self.stdout.warning("Systematics dataframe not initialized. Skipping.")
                    return False
        if check_rel_effect:
            primary_keys = self.resolve_primary_keys(self.SYST_TYPES)
            if any(primary_key not in self.dataframe.columns for primary_key in primary_keys):
                if strict:
                    raise RuntimeError("systematic relative effects not evaluated")
                else:
                    self.stdout.warning("Systematic relative effects not evaluated. Skipping.")
                    return False
        return True
    
    def process_systematics_data(self, df_nom, df_sys, variation:str):
        raise NotImplementedError
        
    def get_dataframe(self, samples:List[str]=None,
                      syst_themes:List[str]=None,
                      syst_names:List[str]=None,
                      categories:List[str]=None,
                      simplified:bool=True,
                      remove_pruned:bool=True):
        if simplified:
            pass_check = self.sanity_check(check_dataframe=True,
                                           check_rel_effect=True,
                                           strict=False)
        else:
            pass_check = self.sanity_check(check_dataframe=True,
                                           check_rel_effect=False,
                                           strict=False)
        if not pass_check:
            return None
        samples = self.resolve_samples(samples)
        syst_themes = self.resolve_syst_themes(syst_themes)
        syst_names = self.resolve_syst_names(syst_names)
        categories = self.resolve_categories(categories)
        index_values = (samples, syst_themes, syst_names, categories)
        index_levels = ('sample', 'syst_theme', 'systematics', 'category')
        selected_df = filter_dataframe_by_index_values(self.dataframe,
                                                       index_values,
                                                       index_levels)
        if remove_pruned and ('pruned' in selected_df.columns):
            selected_df = selected_df[selected_df['pruned'] != 1]
        if simplified:
            primary_keys = self.resolve_primary_keys(self.SYST_TYPES)
            return selected_df[primary_keys]
        
        return selected_df

    def evaluate_relative_effect(self, variations:Optional[List]=None):
        self.sanity_check(check_dataframe=True, check_rel_effect=False)
        self.dataframe = self._evaluate_relative_effect(self.dataframe, variations=variations)
    
    @semistaticmethod
    def _evaluate_relative_effect(self, df, variations:Optional[List]=None):
        raise df
   
    @semistaticmethod
    def _prune_systematics(self, df, prune_significative:bool=True, prune_threshold:float=0.1):
        new_df = df.copy()
        syst_types = self.get_syst_types()
        for syst_type in syst_types:
            prune_col = self.format_column("pruned", syst_type)
            # initialize prune status if not exist
            if prune_col not in df.columns:
                new_df[prune_col] = 0
            mask_all_pruned = pd.Series(True, index=df.index)
            variations = list(self.DEFAULT_VARIATIONS)
            for variation in variations:
                significative_col = self.format_column(f"{variation}_significative", syst_type)
                above_threshold_col = self.format_column(f"{variation}_above_threshold", syst_type)
                new_df[significative_col] = 1
                new_df[above_threshold_col] = 1
                mask_pruned = pd.Series(False, index=df.index)
                val_label = self.format_column(f"{variation}_rel_effect_val", syst_type)
                err_label = self.format_column(f"{variation}_rel_effect_err", syst_type)
                if prune_significative:
                    mask_non_sig = new_df[err_label] > np.abs(new_df[val_label])
                    mask_pruned |= mask_non_sig
                    new_df.loc[mask_non_sig, [significative_col]] = 0
                if prune_threshold > 0:
                    mask_negligible = prune_threshold > np.abs(new_df[val_label])
                    mask_pruned |= mask_negligible
                    new_df.loc[mask_negligible, [above_threshold_col]] = 0

                mask_all_pruned &= mask_pruned
                new_df.loc[mask_pruned, [val_label]] = 0
                new_df.loc[mask_pruned, [err_label]] = 0

            new_df.loc[mask_all_pruned, [prune_col]] = 1
        return new_df
            
    def prune_systematics(self, prune_significative:Optional[bool]=None,
                          prune_threshold:Optional[float]=None):
        self.sanity_check(check_dataframe=True,
                          check_rel_effect=True)
        if prune_significative is None:
            prune_significative = self.config['prune_significative']
        if prune_threshold is None:
            prune_threshold = self.config['prune_threshold']
        self.dataframe = self._prune_systematics(self.dataframe,
                                                 prune_significative=prune_significative,
                                                 prune_threshold=prune_threshold)
     
    @semistaticmethod
    def _merge_smear_systematics(self, df):
        systematics_values = df.index.get_level_values('systematics')
        systematics_str = systematics_values.str
        index_smear = systematics_str.endswith("PDsmear") | systematics_str.endswith("MCsmear")
        final_df = df[~index_smear]
        target_df = df[index_smear]
        target_df_by_systematics = {}
        for systematics, new_df in target_df.groupby("systematics"):
            target_df_by_systematics[systematics] = new_df
        smear_systematics = list(systematics_values.unique())
        source_systematics = list(set([s.replace("_PDsmear","").replace("_MCsmear", "") for s in smear_systematics]))
        variations = list(self.DEFAULT_VARIATIONS)
        default_index = list(final_df.index.names)
        for source in source_systematics:
            pd_smear_df = target_df_by_systematics.get("{}_PDsmear".format(source), None)
            mc_smear_df = target_df_by_systematics.get("{}_MCsmear".format(source), None)
            # make sure both PDsmear and MCsmear systematics exist
            if (pd_smear_df is None) or (mc_smear_df is None):
                continue
            # make sure the dataframes for PDsmear and MCsmear have correct pairing of indexes
            pd_smear_df = pd_smear_df.reset_index(["systematics", "syst_theme"])
            mc_smear_df = mc_smear_df.reset_index(["systematics", "syst_theme"])
            common_index = pd_smear_df.index.intersection(mc_smear_df.index)
            pd_smear_df = pd_smear_df.loc[common_index]
            mc_smear_df = mc_smear_df.loc[common_index]
            # create dataframe for the combined systematics
            combined_df = pd_smear_df.copy()
            combined_df["systematics"] = combined_df["systematics"].str.replace("_PDsmear", "")
            combined_df["syst_theme"] = combined_df["syst_theme"].str.replace("JetSys4", "JetSys3+4")
            syst_types = self.get_syst_types()
            for syst_type in syst_types:
                # prune results are no longer valid
                prune_col = self.format_column("pruned", syst_type)
                if prune_col in combined_df:
                    combined_df[prune_col] = -1
                    for variation in variations:
                        significative_col = self.format_column(f"{variation}_significative", syst_type)
                        above_threshold_col = self.format_column(f"{variation}_above_threshold", syst_type)
                        combined_df[significative_col] = -1
                        combined_df[above_threshold_col] = -1
                for variation in variations:
                    val_label = self.format_column(f"{variation}_rel_effect_val", syst_type)
                    err_label = self.format_column(f"{variation}_rel_effect_err", syst_type)
                    # actual calculation of the combined relative effect and associated stat errors
                    combined_df[val_label] = mc_smear_df[val_label] - pd_smear_df[val_label]
                    combined_df[err_label] = np.sqrt(np.power(mc_smear_df[err_label],2) + \
                                                     np.power(pd_smear_df[err_label],2))
            combined_df = combined_df.reset_index().set_index(default_index)
            final_df = final_df.combine_first(combined_df)
        return final_df
    
    def merge_smear_systematics(self):
        self.dataframe = self._merge_smear_systematics(self.dataframe)
   
    def get_merged_systematics_by_max_effect(self, df, samples:Dict[str, List[str]]=None,
                                             syst_names:Dict[str, List[str]]=None,
                                             categories:Dict[str, List[str]]=None):
        grouped = {
            'samples': samples,
            'categories': categories,
            'syst_names': syst_names
        }
        index_components = {}
        for index in grouped:
            if grouped[index] is None:
                continue
            index_components[index] = list(grouped[index].keys())
        if not index_components:
            raise RuntimeError('nothing to merge')
        merge_indices = list(index_components.keys())
        n_index = len(merge_indices)
        combinations = list(itertools.product(*index_components.values()))
        syst_types = self.get_syst_types()
        index_names = list(df.index.names)
        index_map = {
            'samples': 'sample',
            'categories': 'category',
            'syst_names': 'systematics'
        }
        merge_index_names = [index_map[index] for index in merge_indices]
        outer_index = list(set(index_names) - set(merge_index_names))
        dfs_to_merge = []
        for combination in combinations:
            select_kwargs = {merge_indices[i]: grouped[merge_indices[i]][combination[i]] \
                             for i in range(n_index)}
            selected_df = self.get_dataframe(**select_kwargs)
            for _, group_df in selected_df.groupby(level=outer_index):
                group_merged_df = group_df.iloc[[0]].copy().reset_index()
                group_merged_df.loc[:, merge_index_names] = combination
                for syst_type in syst_types:
                    for variation in ['up', 'down']:
                        value_col = self.format_column(f"{variation}_rel_effect_val", syst_type)
                        error_col = self.format_column(f"{variation}_rel_effect_err", syst_type)
                        idxmax = group_df[value_col].abs().idxmax()
                        group_merged_df.loc[:, [value_col, error_col]] = group_df.loc[idxmax, [value_col, error_col]].values
                dfs_to_merge.append(group_merged_df)
        merged_df = pd.concat(dfs_to_merge)
        merged_df = merged_df.set_index(index_names)
        return merged_df
        
    @semistaticmethod
    def _fix_same_sign(self, df):
        fixed_df = df.copy()
        syst_types = self.get_syst_types()
        for syst_type in syst_types:
            rel_effect_up_label   = self.format_column("up_rel_effect_val", syst_type)
            rel_effect_down_label = self.format_column("down_rel_effect_val", syst_type)

            # find cases with same sign systematics
            criteria = fixed_df[rel_effect_up_label]*fixed_df[rel_effect_down_label] > 0
            case_up_greater = (np.abs(fixed_df[rel_effect_up_label]) > np.abs(fixed_df[rel_effect_down_label]))
            criteria_case_up_greater = criteria & case_up_greater
            criteria_case_up_smaller = criteria & ~criteria_case_up_greater

            # apply the fix: symmetrise by the larger uncertainty
            fixed_df.loc[criteria_case_up_greater, [rel_effect_down_label]] = \
            -fixed_df[criteria_case_up_greater][rel_effect_up_label]
            fixed_df.loc[criteria_case_up_smaller, [rel_effect_up_label]] = \
            -fixed_df[criteria_case_up_smaller][rel_effect_down_label]
        
        return fixed_df
    
    def fix_same_sign(self):
        self.sanity_check(check_dataframe=True,
                          check_rel_effect=True)
        self.dataframe = self._fix_same_sign(self.dataframe)
            
    def remove_failed_results(self):
        self.sanity_check(check_dataframe=True)
        self.dataframe = self.dataframe[self.dataframe['status'] == 1]
        
    def post_process(self, merge_config:Optional[Dict]=None):
        pass_check = self.sanity_check(check_dataframe=True,
                                       check_rel_effect=True,
                                       strict=False)
        if not pass_check:
            return None
        # remove systematics with failed status
        self.stdout.info("Filtering systematics with failed status")
        self.remove_failed_results()
        self.stdout.info("Merging JER systematics")
        self.merge_smear_systematics()
        self.stdout.info("Applying systematics pruning")
        self.prune_systematics()
        if merge_config is not None:
            self.stdout.info("Merging systematics by max effect")
            merged_dataframe = self.get_merged_systematics_by_max_effect(self.dataframe,
                                                                         **merge_config)
            self.dataframe = self.dataframe.combine_first(merged_dataframe)
            self.prune_systematics()
        self.stdout.info("Fixing systematics with same signs")
        self.fix_same_sign()
        """
        if merge_condition is not None:
            self.stdout.info("Merging systematics by maximum effect")
            self.dataframe = self.merge_df_by_max_effect(self.dataframe, merge_condition)
        """
        self.processed = True

    def save(self, filename:str):
        pass_check = self.sanity_check(check_dataframe=True, strict=False)
        if pass_check:
            self.dataframe.reset_index().to_csv(filename, index=False)
        
    def load(self, filename):
        self.dataframe = pd.read_csv(filename).set_index(self.INDICES)
        
    @classmethod
    def fill_hierarchical_data(cls, df, index_list, keys, scale=1./100):
        data = {}
        if len(index_list) == 0:
            values = tuple()
            for key in keys:
                key = key + ('val',)
                value = df[key].values[0]*scale
                values += (value,)
            if df['symmetric'][0]:
                return values[0]*scale
            return values
        for index, df_new in df.groupby(index_list[0]):
            data[index] = cls.fill_hierarchical_data(df_new, index_list[1:], keys)
        return data
    
    def get_simplified_data(self, scale=1./100):
        if self.dataframe is None:
            return
        data = {}
        for syst_type in self.PRIMARY_KEYS:
            df = self.get_valid_dataframe(syst_type)
            keys = self.PRIMARY_KEYS[syst_type]
            data[syst_type] = self.fill_hierarchical_data(df, self.INDICES, keys, scale=scale)
        return data
    
    def get_valid_dataframe(self, syst_type):
        if self.dataframe is None:
            return
        if (syst_type, "prune_status") in self.dataframe:
            return self.dataframe[self.dataframe[(syst_type, 'prune_status')] == 0]
        return self.dataframe
    
    def save_simplified_data(self, filename:str):
        data = self.get_simplified_data()
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def _discard(df, **expressions):
        new_df = df.copy()
        mask = pd.Series(True, index=df.index)
        for index in expressions:
            expression = expressions[index]
            mask &= new_df.index.get_level_values(index).str.contains(expression)
        new_df = new_df[~mask]
        return new_df
    
    def discard(self, **expressions):
        self.dataframe = self._discard(self.dataframe, **expressions)

    def _get_magnitude(self, errhi: float, errlo: float,
                       syst_name: Optional[str] = None):
        # fix sign
        if (errhi <= 0) and (errlo >= 0):
            if syst_name is not None:
                self.stdout.warning(
                    f'Systematics {syst_name} has negative up variation ({errhi:.2g}) and '
                    f'positive down variation ({errlo:.2g}). The variations will be swapped '
                    'and sign-flipped for consistency in the response function.'
                )
            return [-errlo, abs(errhi)]
        return [errhi, errlo]

    def _get_summary(self, prefix:str='',
                     get_df_func:Optional=None):
        self.sanity_check(check_dataframe=True,
                          check_rel_effect=True,
                          strict=False)
        if get_df_func is None:
            get_df_func = self.get_dataframe
        summary_data = {}
        categories = self.resolve_categories()
        samples = self.resolve_samples()
        for category in categories:
            if category not in summary_data:
                summary_data[category] = {}
            for sample in samples:
                if sample not in summary_data[category]:
                    summary_data[category][sample] = {}
                df = get_df_func(categories=[category], samples=[sample], remove_pruned=True)
                if len(df) == 0:
                    continue
                df = df.reset_index('systematics')
                data = df.to_dict('list')
                for syst_name, val_up, val_down in zip(data['systematics'],
                                                       data['up_rel_effect_val'],
                                                       data['down_rel_effect_val']):
                    full_syst_name = f"{prefix}{syst_name}"
                    magnitude = self._get_magnitude(
                        errhi=val_up / 100.,
                        errlo=val_down / 100.,
                        syst_name=full_syst_name
                    )
                    summary_data[category][sample][full_syst_name] = {
                        'Constr': 'asym',
                        'CentralValue': 1,
                        'Mag': magnitude
                    }
        return summary_data