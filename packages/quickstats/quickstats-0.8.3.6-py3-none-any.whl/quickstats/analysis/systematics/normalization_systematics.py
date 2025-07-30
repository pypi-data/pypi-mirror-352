from typing import Optional, List

import numpy as np

from quickstats import semistaticmethod
from quickstats.maths.statistics import get_sumw2
from quickstats.maths.statistics_jitted import (get_sys_rel_effect,
                                                get_sys_err_rel_effect_full_corr,
                                                get_sys_err_rel_effect_part_corr)
from .base_systematics import BaseSystematics

class NormalizationSystematics(BaseSystematics):

    def get_n_toys(self):
        if self.config['norm_syst_eval_method'] != 'bootstrap':
            return None
        return self.config['norm_syst_eval_options'].get('n_toys', 100)

    @semistaticmethod
    def _evaluate_relative_effect(self, df, variations:Optional[List]=None):
        if variations is None:
            variations = list(self.DEFAULT_VARIATIONS)
        for variation in variations:
            # relative effect on yield
            nom_val = df[f'{variation}_nom_val'].values
            sys_val = df[f'{variation}_sys_val'].values
            df[f'{variation}_rel_effect_val'] = get_sys_rel_effect(nom_val, sys_val)
            # error of relative effect on yield for fully correlated case
            full_corr_mask = df[f'{variation}_correlation'] =='full'
            df_full_corr = df[full_corr_mask]
            fc_nom_val = df_full_corr[f'{variation}_nom_val'].values
            fc_nom_err = df_full_corr[f'{variation}_nom_err'].values
            fc_sys_val = df_full_corr[f'{variation}_sys_val'].values
            fc_sys_err = df_full_corr[f'{variation}_sys_err'].values
            df.loc[full_corr_mask, [f'{variation}_rel_effect_err']] = get_sys_err_rel_effect_full_corr(
                fc_nom_val, fc_nom_err, fc_sys_val, fc_sys_err)
            # error of relative effect on yield for partially correlated case
            part_corr_mask = df[f'{variation}_correlation'] == 'partial'
            df_part_corr = df[part_corr_mask]
            pc_nom_val       = df_part_corr[f'{variation}_nom_val'].values
            pc_com_nom_val   = df_part_corr[f'{variation}_com_nom_val'].values
            pc_uncom_nom_val = df_part_corr[f'{variation}_uncom_nom_val'].values
            pc_com_nom_err   = df_part_corr[f'{variation}_com_nom_err'].values
            pc_uncom_nom_err = df_part_corr[f'{variation}_uncom_nom_err'].values
            pc_uncom_sys_val = df_part_corr[f'{variation}_uncom_sys_val'].values
            pc_uncom_sys_err = df_part_corr[f'{variation}_uncom_sys_err'].values
            df.loc[part_corr_mask, [f'{variation}_rel_effect_err']] = get_sys_err_rel_effect_part_corr(
                pc_nom_val, pc_com_nom_val, pc_uncom_nom_val , pc_com_nom_err,
                pc_uncom_nom_err, pc_uncom_sys_val, pc_uncom_sys_err)
        return df
    
    def process_systematics_dataframe(self, df, variations:Optional[List]=None):
        eval_method = self.config['norm_syst_eval_method']
        if eval_method == 'analytic':
            return self._evaluate_relative_effect(df, variations)
        return df
    
    def process_systematics_data_with_bootstrap(self, df_nom, df_sys, variation:str,
                                                n_toys:int, toy_weights_nom:np.ndarray=None,
                                                save_toy_as:Optional[str]=None):
        assert toy_weights_nom.shape[0] == n_toys
        toy_weights_sys = self.get_sys_toy_weights(df_nom, df_sys, n_toys, toy_weights_nom)
        weight_col = self.config['weight']
        weight_nom = df_nom[weight_col].values
        weight_sys = df_sys[weight_col].values
        yield_toys_nom = np.sum(toy_weights_nom * weight_nom, axis=1)
        yield_toys_sys = np.sum(toy_weights_sys * weight_sys, axis=1)
        rel_effect_toys = get_sys_rel_effect(yield_toys_nom, yield_toys_sys)
        result = {}
        result[f'{variation}_rel_effect_val'] = np.mean(rel_effect_toys)
        result[f'{variation}_rel_effect_err'] = np.std(rel_effect_toys)
        return result
    
    def process_systematics_data_with_analytic(self, df_nom, df_sys, variation:str):
        weight_col = self.config['weight']
        common_events = df_nom.index.intersection(df_sys.index)
        uncommon_nom_events = df_nom.index.difference(df_sys.index)
        uncommon_sys_events = df_sys.index.difference(df_nom.index)
        result = {}
        result[f'{variation}_nom_val'] = df_nom[weight_col].sum()
        result[f'{variation}_sys_val'] = df_sys[weight_col].sum()
        result[f'{variation}_nom_err'] = get_sumw2(df_nom[weight_col])
        result[f'{variation}_sys_err'] = get_sumw2(df_sys[weight_col])
        df_com_nom = df_nom.loc[common_events]
        df_com_sys = df_sys.loc[common_events]
        result[f'{variation}_com_nom_val'] = df_com_nom[weight_col].sum()
        result[f'{variation}_com_sys_val'] = df_com_sys[weight_col].sum()
        result[f'{variation}_com_nom_err'] = get_sumw2(df_com_nom[weight_col])
        result[f'{variation}_com_sys_err'] = get_sumw2(df_com_sys[weight_col])
        df_uncom_nom = df_nom.loc[uncommon_nom_events]
        df_uncom_sys = df_sys.loc[uncommon_sys_events]
        result[f'{variation}_uncom_nom_val'] = df_uncom_nom[weight_col].sum()
        result[f'{variation}_uncom_sys_val'] = df_uncom_sys[weight_col].sum()
        result[f'{variation}_uncom_nom_err'] = get_sumw2(df_uncom_nom[weight_col])
        result[f'{variation}_uncom_sys_err'] = get_sumw2(df_uncom_sys[weight_col])
        com_weight_allclose = np.allclose(df_com_nom[weight_col],
                                          df_com_sys[weight_col],
                                          atol=self.ATOL, rtol=self.RTOL)
        # only weight changed, kinematics remain the same
        if ((len(uncommon_nom_events) == 0) and (len(uncommon_sys_events) == 0) and
            (not com_weight_allclose)):
            result[f'{variation}_correlation'] = 'full'
        else:
            result[f'{variation}_correlation'] = 'partial'
        return result
    
    def process_systematics_data(self, df_nom, df_sys, variation:str, **kwargs):
        eval_method = self.config['norm_syst_eval_method']
        if eval_method == 'bootstrap':
            evaluator = self.process_systematics_data_with_bootstrap
        elif eval_method == 'analytic':
            evaluator = self.process_systematics_data_with_analytic
        else:
            raise ValueError(f'unsupported norm syst eval method: {eval_method}')
        eval_options = self.config['norm_syst_eval_options']
        return evaluator(df_nom=df_nom, df_sys=df_sys,
                         variation=variation, **eval_options,
                         **kwargs)
    
    def get_summary(self, prefix:str=''):
        return self._get_summary(prefix=prefix)