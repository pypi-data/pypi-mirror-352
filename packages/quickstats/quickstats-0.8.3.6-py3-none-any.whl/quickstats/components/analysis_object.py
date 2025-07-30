from typing import Optional, Union, List, Dict, Sequence

from quickstats import AbstractObject, cached_import
from quickstats.components import ExtendedModel, ExtendedMinimizer, DiscreteNuisance
from quickstats.components.basics import WSArgument, SetValueMode
from quickstats.utils.common_utils import update_config_dict, combine_dict
from quickstats.utils.string_utils import split_str
from quickstats.utils.roostats_utils import set_prior_pdf
from quickstats.interface.root import RooArgSet, ModelConfig

class AnalysisObject(AbstractObject):
    
    kInitialSnapshotName = "initialSnapshot"
    kCurrentSnapshotName = "currentSnapshot"
    kTempSnapshotName    = "tmpSnapshot"
    
    def __init__(self, filename:Optional[str]=None, poi_name:Optional[Union[str, List[str]]]=None,
                 data_name:str='combData', binned_likelihood:bool=True,
                 fix_param:str='', profile_param:str='', ws_name:Optional[str]=None, 
                 mc_name:Optional[str]=None, snapshot_name:Optional[Union[List[str], str]]=None,
                 minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', precision:float=0.001, 
                 eps:float=1.0, retry:int=1, retry_policy:int=1, strategy:int=1, print_level:int=-1,
                 num_cpu:int=1, offset:bool=True, optimize:int=2, constrain_nuis:bool=True,
                 batch_mode:bool=False, prior_type:Optional[str]=None, runtimedef_expr:Optional[str]=None,
                 int_bin_precision:float=-1., preset_param:bool=False, minimizer_offset:int=1,
                 extra_minimizer_options:Optional[Union[Dict, str]]=None,
                 minimizer_cls=None, verbosity:Optional[Union[int, str]]="INFO",
                 **kwargs):
        super().__init__(verbosity=verbosity)
        self.model = None
        self.minimizer = None
        self._use_blind_range = False
        if minimizer_cls is None:
            self.minimizer_cls = ExtendedMinimizer
        else:
            self.minimizer_cls = minimizer_cls
        if filename is not None:
            model_options = {
                "filename"          : filename,
                "ws_name"           : ws_name,
                "mc_name"           : mc_name,
                "data_name"         : data_name,
                "snapshot_name"     : snapshot_name,
                "binned_likelihood" : binned_likelihood
            }
            self.setup_model(**model_options)
            self.model._load_floating_auxiliary_variables()
            self.save_snapshot(self.kInitialSnapshotName, WSArgument.MUTABLE)
            minimizer_options = {
                "constrain_nuis"    : constrain_nuis,
                "minimizer_type"    : minimizer_type,
                "minimizer_algo"    : minimizer_algo,
                "precision"         : precision,
                "eps"               : eps,
                "strategy"          : strategy,
                "minimizer_offset"  : minimizer_offset,
                "offset"            : offset,
                "optimize"          : optimize,
                "retry"             : retry,
                "retry_policy"      : retry_policy,
                "num_cpu"           : num_cpu,
                "print_level"       : print_level,
                "batch_mode"        : batch_mode,
                "int_bin_precision" : int_bin_precision,
                "runtimedef_expr"   : runtimedef_expr,
                "verbosity"         : verbosity
            }
            if kwargs:
                minimizer_options = combine_dict(minimizer_options, kwargs)
            minimizer_options = update_config_dict(minimizer_options, extra_minimizer_options)
            self.setup_minimizer(discrete_nuisance=self.model._discrete_nuisance,
                                 **minimizer_options)
            self.set_poi(poi_name)
            
            if preset_param:
                self.preset_parameters()
            self.setup_parameters(fix_param, profile_param, update_snapshot=True)
            set_prior_pdf(self.model.workspace,
                          self.model.model_config,
                          self.poi, prior_type)
            self.sanity_check()
            
        
    def sanity_check(self):
        ROOT = cached_import("ROOT")
        def check_aux_vars_are_fixed():
            aux_vars = self.model.get_variables("auxiliary")
            ROOT.RooStats.RemoveConstantParameters(aux_vars)
            if self.model.has_discrete_nuisance():
                aux_vars = RooArgSet.get_set_difference(aux_vars, self.model.discrete_nuisance.multipdf_params)
                aux_vars = RooArgSet.get_set_difference(aux_vars, ROOT.RooArgSet(self.model.discrete_nuisance.multipdf_cats))
            if len(aux_vars) > 0:
                aux_var_names = [v.GetName() for v in aux_vars]
                self.stdout.warning("The following auxiliary variables (variables that are not "
                                    "part of the POIs, observables, nuisance parameters, global "
                                    "observables and discrete nuisances) are floating: "
                                    f"{','.join(aux_var_names)}. If this is not intended, please "
                                    "make sure to fix them before fitting.", "red")
            passed = len(aux_vars) == 0
            return passed
        
        def check_model_config():
            passed = ModelConfig(verbosity=self.stdout.verbosity).sanity_check(self.model.model_config)
            return passed
        
        for task_name, task in [('Auxiliary variable', check_aux_vars_are_fixed),
                                ('Model config', check_model_config)]:
            passed = task()
            if passed:
                self.stdout.info(f"{task_name} sanity check: PASSED")
            else:
                self.stdout.info(f"{task_name} sanity check: FAILED")
            
    def preset_parameters(self, fix_pois:bool=True, fix_globs:bool=True, float_nuis:bool=False):
        ROOT = cached_import("ROOT")
        if fix_pois:
            ROOT.RooStats.SetAllConstant(self.model.pois, True)
            self.stdout.info("Preset POIs as constant parameters.")
        if fix_globs:
            ROOT.RooStats.SetAllConstant(self.model.global_observables, True)
            self.stdout.info("Preset global observables as constant parameters.")
        if float_nuis:
            ROOT.RooStats.SetAllConstant(self.model.nuisance_parameters, False)
            self.stdout.info("INFO: Preset nuisance parameters as floating parameters.")
    
    @property
    def use_blind_range(self):
        return self._use_blind_range
    
    @property
    def minimizer_options(self):
        return self.minimizer.config
    
    @property
    def nll_commands(self):
        return self.minimizer.nll_commands
    
    @property
    def get_poi(self):
        return self.model.get_poi

    @property
    def poi(self):
        return self.minimizer._poi
    
    @property
    def generate_asimov(self):
        return self.model.generate_asimov
    
    # black magic
    def _inherit_init(self, init_func, **kwargs):
        import inspect
        this_parameters = list(inspect.signature(AnalysisObject.__init__).parameters)
        if "self" in this_parameters:
            this_parameters.remove("self")
        that_parameters = list(inspect.signature(init_func).parameters)
        is_calling_this = set(this_parameters) == set(that_parameters)
        if is_calling_this:
            init_func(**kwargs)
        else:
            that_kwargs = {k:v for k,v in kwargs.items() if k in that_parameters}
            this_kwargs = {k:v for k,v in kwargs.items() if k not in that_parameters}
            init_func(config=this_kwargs, **that_kwargs)

    def set_poi(self, expr:Optional[Union[str, List[str], "ROOT.RooRealVar", "ROOT.RooArgSet"]]=None):
        ROOT = cached_import("ROOT")
        pois = self.get_poi(expr)
        self.minimizer.set_poi(pois)
        if isinstance(pois, ROOT.RooRealVar):
            poi_names = [pois.GetName()]
        else:
            poi_names = [poi.GetName() for poi in pois]
        if len(poi_names) == 1:
            self.stdout.info(f'POI set to "{poi_names[0]}"')
        elif len(poi_names) > 1:
            text = ", ".join([f'"{name}"' for name in poi_names])
            self.stdout.info(f'POIs set to {text}')
        
    def setup_model(self, **kwargs):
        model = ExtendedModel(**kwargs, verbosity=self.stdout.verbosity)
        model.stdout = self.stdout
        self.model = model
    
    def setup_parameters(self, fix_param:str='', profile_param:str='', update_snapshot:bool=True):
        if not self.model:
            raise RuntimeError('uninitialized analysis object')
        fixed_parameters = []
        profiled_parameters = []
        if fix_param:
            fixed_parameters = self.model.fix_parameters(fix_param)
        if profile_param:
            profiled_parameters = self.model.profile_parameters(profile_param)
        self._update_floating_auxiliary_variables(fixed_parameters, profiled_parameters)
        if update_snapshot:
            self.save_snapshot(self.kCurrentSnapshotName, WSArgument.MUTABLE)
        self._check_poi_setup(fixed_parameters, profiled_parameters)

    def set_parameters(
        self,
        param_setup: Optional[Union[str, Sequence, Dict]] = None,
        params: Optional["ROOT.RooArgSet"] = None,
        mode: Union[str, SetValueMode] = SetValueMode.UNCHANGED,
        strict: bool = False,
        update_snapshot:bool=True
    ) -> List["ROOT.RooRealVar"]:
        modified_parameters = self.model.set_parameters(
            param_setup=param_setup,
            params=params,
            mode=mode,
            strict=strict
        )
        if update_snapshot:
            self.save_snapshot(self.kCurrentSnapshotName, WSArgument.MUTABLE)

    def fix_parameters(
        self,
        param_setup_expr: Optional[str] = None,
        source: Optional["ROOT.RooArgSet"] = None
    ) -> List["ROOT.RooRealVar"]:
        """Fix parameters according to the provided setup."""
        return self.set_parameters(param_setup_expr, source, mode=SetValueMode.FIX)

    def profile_parameters(
        self,
        param_setup_expr: Optional[str] = None,
        source: Optional["ROOT.RooArgSet"] = None
    ) -> List["ROOT.RooRealVar"]:
        """Profile parameters according to the provided setup."""
        return self.set_parameters(param_setup_expr, source, mode=SetValueMode.FREE)    
    
    def _update_floating_auxiliary_variables(self, fixed_parameters:List, profiled_parameters:List):
        if self.model.floating_auxiliary_variables is None:
            self.model._load_floating_auxiliary_variables()
        fixed_parameters    = RooArgSet.from_list(fixed_parameters)
        profiled_parameters = RooArgSet.from_list(profiled_parameters)
        core_variables = self.get_variables(WSArgument.CORE)
        fixed_parameters.remove(core_variables)
        profiled_parameters.remove(core_variables)
        self.model._floating_auxiliary_variables.add(profiled_parameters)
        self.model._floating_auxiliary_variables.remove(fixed_parameters)
        
    def _check_poi_setup(self, fixed_parameters:List, profiled_parameters:List):
        ROOT = cached_import("ROOT")
        # pois defined in workspace
        ws_pois  = self.model.pois
        # pois defined in this analysis
        ana_pois = ROOT.RooArgSet(self.poi)
        if ana_pois.size() == 0:
            return None
        aux_pois = ROOT.RooArgSet(ws_pois)
        aux_pois.remove(ana_pois)
        for profiled_param in profiled_parameters:
            if aux_pois.contains(profiled_param):
                param_name = profiled_param.GetName()
                self.stdout.warning(f"Attemping to profile the parameter \"{param_name}\" which is a "
                                    f"POI defined in the workspace but not a POI used in this study. This "
                                    f"parameter will still be fixed during likelihood fit / limit setting. "
                                    f"Please designate the parameter as a POI in this study if intended.",
                                    "red")
        for fixed_param in fixed_parameters:
            if ana_pois.contains(fixed_param):
                param_name = fixed_param.GetName()
                self.stdout.warning(f"Attemping to fix the parameter \"{param_name}\" which is a "
                                    f"POI used in this study. This parameter will still be floated during "
                                    f"unconditional likelihood fit / limit setting.", "red")
            
    def setup_minimizer(self, constrain_nuis:bool=True,
                        discrete_nuisance:Optional["DiscreteNuisance"]=None,
                        runtimedef_expr:Optional[str]=None, **kwargs):
        minimizer = self.minimizer_cls("Minimizer", self.model.pdf, self.model.data,
                                       workspace=self.model.workspace,
                                       runtimedef_expr=runtimedef_expr,
                                       verbosity=self.stdout.verbosity,
                                       discrete_nuisance=discrete_nuisance)
        
        nll_options = {k:v for k,v in kwargs.items() if k in ExtendedMinimizer._DEFAULT_NLL_OPTION_}
        
        if constrain_nuis:
            nll_options['constrain'] = self.model.nuisance_parameters
            nll_options['global_observables'] = self.model.global_observables
            conditional_obs = self.model.model_config.GetConditionalObservables()
            if conditional_obs:
                nll_options['conditional_observables'] = conditional_obs
            #nll_commands.append(ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet()))
        
        minimizer_options = {k:v for k,v in kwargs.items() if k in ExtendedMinimizer._DEFAULT_MINIMIZER_OPTION_}
        minimizer.configure_nll(**nll_options)
        minimizer.configure(**minimizer_options)
        minimizer.stdout = self.stdout
        self.minimizer = minimizer
        self.model.set_minimizer(self.minimizer)
        self.default_nll_options = nll_options
        self.default_minimizer_options = minimizer_options
    
    def set_data(self, data_name:str='combData'):
        ROOT = cached_import("ROOT")
        if isinstance(data_name, ROOT.RooDataSet):
            data = data_name
        else:
            data = self.model.workspace.data(data_name)
            if not data:
                raise RuntimeError(f'workspace does not contain the dataset "{data_name}"')
        self.minimizer.set_data(data)
        self.model._data = data

    def set_observable_range(
        self,
        name: str, 
        range_min: float,
        range_max: float,
        categories: Optional[List[str]] = None
    ) -> None:
        category_observables = self.model.get_category_observables(allow_multi=False)
        categories = categories or list(category_observables.keys())
        for category in categories:
            if category not in category_observables:
                raise ValueError(f'Category not found in workspace: "{category}"')
            range_name = f'{name}_{category}'
            category_observables[category].setRange(range_name, range_min, range_max)

    def set_fit_range(
        self,
        name: Optional[str] = None
    ) -> None:
        
        if not name:
            self.minimizer.unset_fit_range

        # check that range exist for all observables
        range_names = split_str(name, sep=',', remove_empty=True)
        category_observables = self.model.get_category_observables(allow_multi=False)
        for range_name in range_names:
            for category, observable in category_observables.items():
                category_range_name = f'{range_name}_{category}'
                if not observable.hasRange(category_range_name):
                    raise RuntimeError(
                        f'Observable "{observable.GetName()}" in the category "{category}" '
                        f'does not contain the range "{category_range_name}"'
                    )
        self.minimizer.set_fit_range(name, split_range=True)

    def unset_fit_range(self) -> None:
        self.minimizer.unset_fit_range()

    def set_fit_range_expression(
        self,
        expression: str
    ) -> None:
        tokens = split_str(expression, sep=',', remove_empty=True)
        all_categories = self.model.get_categories()
        names = []
        for token in tokens:
            if '=' not in token:
                names.append(token)
                continue
            name, range_data = split_str(token, sep='=', remove_empty=True)
            range_min, range_max = split_str(range_data, sep='_', remove_empty=True)
            range_min, range_max = float(range_min), float(range_max)
            if '@' in name:
                name, category = split_str(name, sep='@', remove_empty=True)
                categories = [category]
            else:
                categories = all_categories
            self.set_observable_range(name, range_min, range_max, categories)
            names.append(name)
        self.set_fit_range(','.join(names))
        
    def set_blind_range(self, blind_range:List[float], categories:Optional[List[str]]=None):
        self.model.create_blind_range(blind_range, categories)
        sideband_range_name = self.model.get_sideband_range_name()
        self.minimizer.configure_nll(range=sideband_range_name, split_range=True, update=True)
        self._use_blind_range = True
        
    def unset_blind_range(self):
        self.minimizer.nll = None
        self.minimizer.nll_commands.pop("RangeWithName", None)
        self.minimizer.nll_commands.pop("SplitRange", None)
        self.stdout.info("Blind range removed from list of  NLL commands. NLL is reset.")
        self._use_blind_range = False
                
    def restore_prefit_snapshot(self):
        self.load_snapshot(self.kCurrentSnapshotName)
        
    def restore_init_snapshot(self):
        self.load_snapshot(self.kInitialSnapshotName)
        self.save_snapshot(self.kCurrentSnapshotName)
    
    def get_variables(self, variable_type:Union[str, WSArgument], sort:bool=True):
        return self.model.get_variables(variable_type, sort=sort)
    
    def save_snapshot(self, snapshot_name:Optional[str]=None, 
                      variables:Optional[Union["ROOT.RooArgSet", str, WSArgument]]=None):
        self.model.save_snapshot(snapshot_name, variables=variables)
        
    def load_snapshot(self, snapshot_name:Optional[str]=None):
        self.model.load_snapshot(snapshot_name)
        
    def save(self, filename:str, recreate:bool=True, rebuild:bool=True, float_all_nuis:bool=False, remove_fixed_nuis:bool=False):
        self.model.save(filename, recreate=recreate, rebuild=rebuild, float_all_nuis=float_all_nuis, remove_fixed_nuis=remove_fixed_nuis)
        self.stdout.info(f'Saved workspace file as "{filename}"')
                
    def decompose_nll(self, fmt:str="pandas"):
        from quickstats.utils.roofit_utils import decompose_nll
        if not self.minimizer.nll:
            self.minimizer.create_nll()
            result = decompose_nll(self.minimizer.nll, self.model.global_observables, fmt=fmt)
            self.minimizer.nll = None
            return result
        return decompose_nll(self.minimizer.nll, self.model.global_observables, fmt=fmt)