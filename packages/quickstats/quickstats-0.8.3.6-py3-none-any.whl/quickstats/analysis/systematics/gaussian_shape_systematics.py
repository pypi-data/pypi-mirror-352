from typing import Optional, List

import numpy as np
import pandas as pd

from .base_systematics import BaseSystematics
from quickstats.interface.root import TH1
from quickstats.maths.statistics_jitted import (get_sys_rel_effect,
                                                get_sys_err_rel_effect_uncorr,
                                                get_interquartile_data)

class GaussianShapeSystematics(BaseSystematics):
    
    SYST_TYPES = ['position', 'spread']
    
    def get_n_toys(self):
        if self.config['shape_syst_eval_method'] != 'bootstrap':
            return None
        return self.config['shape_syst_eval_options'].get('n_toys', 100)
    
    def get_systematics_data_with_mean_IQR_estimator(self, df_nom, df_sys,
                                                     xmin:float, xmax:float, nbins:int,
                                                     observable:str, weight:str):
        x_nom, weight_nom = df_nom[observable].values, df_nom[weight].values
        x_sys, weight_sys = df_sys[observable].values, df_sys[weight].values
        h_nom = TH1.from_numpy_data(x=x_nom, bins=nbins, bin_range=(xmin, xmax),
                                    normalize=True, weights=weight_nom)
        h_sys = TH1.from_numpy_data(x=x_sys, bins=nbins, bin_range=(xmin, xmax),
                                    normalize=True, weights=weight_sys)
        nom_val, nom_err = h_nom.GetMean(), h_nom.GetMeanError()
        sys_val, sys_err = h_sys.GetMean(), h_sys.GetMeanError()
        rel_effect_position_shape = get_sys_rel_effect(nom_val, sys_val)
        err_rel_effect_position_shape = get_sys_err_rel_effect_uncorr(nom_val, nom_err,
                                                                      sys_val, sys_err)
        h_cumul_nom = h_nom.GetCumulativeHist()
        h_cumul_sys = h_sys.GetCumulativeHist()
        try:
            h_cumul_nom = h_nom.GetCumulativeHist()
            IQR_nom_val, IQR_nom_err = get_interquartile_data(h_cumul_nom.bin_content,
                                                              h_cumul_nom.bin_error,
                                                              h_cumul_nom.bin_center)
            IQR_sys_val, IQR_sys_err = get_interquartile_data(h_cumul_sys.bin_content,
                                                              h_cumul_sys.bin_error,
                                                              h_cumul_sys.bin_center)
        except Exception:
            return None
        result = {
            'position_nom_val': nom_val,
            'position_nom_err': nom_err,
            'position_sys_val': sys_val,
            'position_sys_err': sys_err,
            'spread_nom_val': IQR_nom_val,
            'spread_nom_err': IQR_nom_err,
            'spread_sys_val': IQR_sys_val,
            'spread_sys_err': IQR_sys_err,
        }
        return result
    
    def get_shape_estimator(self, name:Optional[str]=None):
        if name is None:
            name = self.config['shape_estimator']
        if name == 'mean_IQR':
            return self.get_systematics_data_with_mean_IQR_estimator
        raise ValueError(f'unsupported shape estimator: {name}')
        
    def get_dataframe(self, samples:List[str]=None,
                      syst_themes:List[str]=None,
                      syst_names:List[str]=None,
                      categories:List[str]=None,
                      simplified:bool=True,
                      remove_position_pruned:bool=False,
                      remove_spread_pruned:bool=False):
        selected_df = super().get_dataframe(samples=samples,
                                            syst_themes=syst_themes,
                                            syst_names=syst_names,
                                            categories=categories,
                                            simplified=False,
                                            remove_pruned=False)
        if remove_position_pruned and ('position_pruned' in selected_df.columns):
            selected_df = selected_df[selected_df['position_pruned'] != 1]
        if remove_spread_pruned and ('spread_pruned' in selected_df.columns):
            selected_df = selected_df[selected_df['spread_pruned'] != 1]
        if simplified:
            primary_keys = self.resolve_primary_keys(self.SYST_TYPES)
            return selected_df[primary_keys]
        return selected_df
    
    def get_position_shape_dataframe(self, samples:List[str]=None,
                                     syst_themes:List[str]=None,
                                     syst_names:List[str]=None,
                                     categories:List[str]=None,
                                     simplified:bool=True,
                                     remove_pruned:bool=True):
        selected_df = self.get_dataframe(samples=samples,
                                         syst_themes=syst_themes,
                                         syst_names=syst_names,
                                         categories=categories,
                                         simplified=simplified,
                                         remove_position_pruned=remove_pruned)
        # remove non-position columns
        selected_df = selected_df[selected_df.columns[selected_df.columns.str.startswith("position")]]
        # remove position prefix
        columns = selected_df.columns
        rename_map = dict(zip(columns.values, columns.str.replace("position_", "")))
        selected_df = selected_df.rename(columns=rename_map)
        return selected_df
    
    def get_spread_shape_dataframe(self, samples:List[str]=None,
                                   syst_themes:List[str]=None,
                                   syst_names:List[str]=None,
                                   categories:List[str]=None,
                                   simplified:bool=True,
                                   remove_pruned:bool=True):
        selected_df = self.get_dataframe(samples=samples,
                                         syst_themes=syst_themes,
                                         syst_names=syst_names,
                                         categories=categories,
                                         simplified=simplified,
                                         remove_spread_pruned=remove_pruned)
        # remove non-spread columns
        selected_df = selected_df[selected_df.columns[selected_df.columns.str.startswith("spread")]]
        # remove spread prefix
        columns = selected_df.columns
        rename_map = dict(zip(columns.values, columns.str.replace("spread_", "")))
        selected_df = selected_df.rename(columns=rename_map)
        return selected_df
        
    def process_systematics_data_with_bootstrap(self, df_nom, df_sys, variation:str, n_toys:int,
                                                toy_weights_nom:np.ndarray=None,
                                                save_toy_as:Optional[str]=None):
        assert toy_weights_nom.shape[0] == n_toys
        toy_weights_sys = self.get_sys_toy_weights(df_nom, df_sys, n_toys, toy_weights_nom)
        weight_col = self.config['weight']
        toy_weight_col = "weight_toy"
        shape_estimator = self.get_shape_estimator()
        kwargs = {
            "observable" : self.config['observable'],
            "weight"     : toy_weight_col,
            **self.config['shape_estimator_options']
        }
        toy_results = []
        df_nom = df_nom.copy()
        df_sys = df_sys.copy()
        for i in range(n_toys):
            df_nom.loc[:, [toy_weight_col]] = df_nom[weight_col] * toy_weights_nom[i]
            df_sys.loc[:, [toy_weight_col]] = df_sys[weight_col] * toy_weights_sys[i]
            result = shape_estimator(df_nom, df_sys, **kwargs)
            toy_results.append(result)
        toy_result_df = pd.DataFrame(toy_results)
        toy_result_df['position_rel_effect'] = get_sys_rel_effect(toy_result_df['position_nom_val'],
                                                                  toy_result_df['position_sys_val'])
        toy_result_df['spread_rel_effect']   = get_sys_rel_effect(toy_result_df['spread_nom_val'],
                                                                  toy_result_df['spread_sys_val'])
        if save_toy_as:
            toy_result_df.to_csv(save_toy_as, index=False)
        final_result = {
            f'position_{variation}_rel_effect_val': np.mean(toy_result_df['position_rel_effect']),
            f'position_{variation}_rel_effect_err': np.std(toy_result_df['position_rel_effect']),
            f'spread_{variation}_rel_effect_val': np.mean(toy_result_df['spread_rel_effect']),
            f'spread_{variation}_rel_effect_err': np.std(toy_result_df['spread_rel_effect'])
        }
        return final_result
    
    def process_systematics_data(self, df_nom, df_sys, variation:str, **kwargs):
        eval_method = self.config['shape_syst_eval_method']
        if eval_method == 'bootstrap':
            evaluator = self.process_systematics_data_with_bootstrap
        else:
            raise ValueError(f'unsupported shape syst eval method: {eval_method}')
        eval_options = self.config['shape_syst_eval_options']
        return evaluator(df_nom=df_nom, df_sys=df_sys,
                         variation=variation, **eval_options,
                         **kwargs)
    
    def get_position_shape_summary(self, prefix:str=''):
        return self._get_summary(prefix=prefix,
                                 get_df_func=self.get_position_shape_dataframe)
    
    def get_spread_shape_summary(self, prefix:str=''):
        return self._get_summary(prefix=prefix,
                                 get_df_func=self.get_spread_shape_dataframe)