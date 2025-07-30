##################################################################################################
# Based on https://gitlab.cern.ch/atlas-physics/stat/tools/StatisticsTools by Stefan Gadatsch
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
from typing import Union, Optional, List, Dict
import math

import numpy as np

import cppyy

import quickstats
from quickstats import AbstractObject, timer, cached_import
from quickstats.utils.string_utils import split_str
from quickstats.utils.common_utils import combine_dict
from quickstats.interface.root import RooArgSet
from .discrete_nuisance import DiscreteNuisance
from .caching_nll_wrapper import CachingNLLWrapper

from quickstats import DescriptiveEnum

class RetryPolicy(DescriptiveEnum):
    NORETRY = (0, 'Do not retry')
    DYNAMIC_STRATEGY = (1, 'Update strategy dynamically')
    DYNAMIC_EPS = (2, 'Update eps dynamically')

class ExtendedMinimizer(AbstractObject):
    _SCAN_EXCLUDE_CONFIG_ = ['scan', 'minos', 'save']
    _NLL_COMMANDS_ = ['NumCPU', 'Constrain', 'CloneData', 'GlobalObservables', 
                      'GlobalObservablesTag', 'OffsetLikelihood', 'Offset']

    _DEFAULT_MINIMIZER_OPTION_ = {
        'minimizer_type': 'Minuit2',
        'minimizer_algo': 'Migrad',        
        'optimize': 2,
        'verbose': 0,
        'save': 0,
        'timer': 0,
        'hesse': 0,
        'minos': 0,
        'scan': 0,
        'improve': 0,
        'num_ee': 5,
        'do_ee_wall': 1,
        'minimizer_offset': 1,
        'retry': 1,
        'retry_policy': 1,
        'eigen': 0,
        'reuse_minimizer': 0,
        'reuse_nll': 0,
        'eps': 1.0,
        'max_calls': -1,
        'max_iters': -1,
        'n_sigma': 1,
        'precision': 0.001,
        'strategy': 1,
        'print_level': -1,
        'error_level': -1,
        # extra configs
        'check_boundary': 1,
        'prefit_hesse': 0,
        'postfit_hesse': 0,
        'minuit2_storage_level': 0,
        'prefit_eps': 0,
        'prefit_strategy': 0,
        'retry_eps_ratio': 10,
        'retry_from_initial': 0,
        # cms dedicated configs
        'set_zero_point': 1, # change the reference point of the NLL to be zero during minimization
        # discrete nuisance configs
        'discrete_min_tol': 0.001,
        'do_discrete_iteration': 1,
        'freeze_disassociated_params': 1,
        'do_short_combination': 1,
        'max_short_combination_iteration': 15,
        'multimin_hide_constants': 1,
        'multimin_mask_constraints': 1,
        'multimin_mask_channels': 2
    }
    
    _DEFAULT_NLL_OPTION_ = {
        'num_cpu': 1,
        'offset': True,
        'batch_mode': False,
        'int_bin_precision': -1
    }

    _DEFAULT_RUNTIMEDEF_ = {
        "OPTIMIZE_BOUNDS": 1,
        "ADDNLL_RECURSIVE": 1,
        "ADDNLL_GAUSSNLL": 1,
        "ADDNLL_HISTNLL": 1,
        "ADDNLL_CBNLL": 1,
        "TMCSO_AdaptivePseudoAsimov": 1,
        "ADDNLL_ROOREALSUM_FACTOR": 1,
        "ADDNLL_ROOREALSUM_NONORM": 1,
        "ADDNLL_ROOREALSUM_BASICINT": 1,
        "ADDNLL_ROOREALSUM_KEEPZEROS": 1,
        "ADDNLL_PRODNLL": 1,
        "ADDNLL_HFNLL": 1,
        "ADDNLL_HISTFUNCNLL": 1,
        "ADDNLL_ROOREALSUM_CHEAPPROD": 1,
        "REMOVE_CONSTANT_ZERO_POINT": 1,
        "SILENT_CACHENLL": 1,
        "FAST_VERTICAL_MORPH": 1,
    }    
    
    @property
    def config(self):
        return self._config
    
    def __init__(self, minimizer_name:str="Minimizer",
                 pdf:Optional["ROOT.RooAbsPdf"]=None,
                 data:Optional["ROOT.RooAbsData"]=None,
                 poi:Optional["ROOT.RooArgSet"]=None,
                 minimizer_options:Optional[Dict]=None,
                 runtimedef_expr:Optional[str]=None,
                 discrete_nuisance:Optional[DiscreteNuisance]=None,
                 verbosity:Optional[Union[int, str]]="INFO",
                 **kwargs):
        super().__init__(verbosity=verbosity)
        """
            Minimizr Options:
                precision: precision for the find sigma algorithm
        """
        ROOT = cached_import("ROOT")
        self.name = minimizer_name
        self.pdf = pdf
        self.data = data
        self.minimizer = None
        self.nll = None
        self.fit_result = None
        self.status = None
        
        self._config = self._DEFAULT_MINIMIZER_OPTION_ 
        if minimizer_options is not None:
            self._config.update(minimizer_options)
        self.minos_set = ROOT.RooArgSet()
        self.cond_set  = ROOT.RooArgSet()
        self.scan_set  = ROOT.RooArgSet()
        
        self.Hessian_matrix = None
        self.nom_nll = None
        self.min_nll = None
        
        self.eigen_values = ROOT.TVectorD()
        self.eigen_vectors = ROOT.TMatrixD()
        
        self.fit_options = {}
        self.scan_options = {}
        #self.nll_command_list = ROOT.RooLinkedList()
        self.nll_commands = {}
        
        self.configure_default_minimizer_options()
        self.set_pdf(pdf)
        self.set_data(data)
        self.set_poi(poi)

        # CMS specific implementations
        self.set_discrete_nuisance(discrete_nuisance)
        self.caching_nll = CachingNLLWrapper(verbosity=self.stdout.verbosity)
        self.set_pois_for_auto_bounds()
        self.set_pois_for_max_bounds()
        self.set_runtimedef(runtimedef_expr)

        self.apply_discrete = 0 # 0: no discrete, 1: CMS discrete, 2: RooFit discrete
        if self.pdf.InheritsFrom("RooSimultaneousOpt") and self.has_discrete_nuisance():
            self.apply_discrete = 1
        elif self.has_discrete_nuisance():
            self.apply_discrete = 2
        
        self.stdout.info(f'Created ExtendedMinimizer("{self.name}") instance')
        
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, val):
        ROOT = cached_import("ROOT")
        assert isinstance(val, ROOT.RooAbsData)
        self._data = val
        self.nll = None
        self.minimizer = None
    
    @property
    def pdf(self):
        return self._pdf

    @pdf.setter
    def pdf(self, val):
        ROOT = cached_import("ROOT")
        assert isinstance(val, ROOT.RooAbsPdf)
        self._pdf = val
        self.nll = None
        self.minimizer = None
        
    @property
    def discrete_nuisance(self):
        return self._discrete_nuisance

    @property
    def poi(self):
        return self._poi
    
    @property
    def auto_bounds_pois(self):
        return self._auto_bounds_pois
    
    @property
    def max_bounds_pois(self):
        return self._max_bounds_pois
            
    @staticmethod
    def _configure_default_minimizer_options(minimizer_type='Minuit2', minimizer_algo='Migrad',
                                             strategy=0, print_level=-1,
                                             minuit2_storage_level=0, debug_mode=False):
        ROOT = cached_import("ROOT")
        ROOT.Math.MinimizerOptions.SetDefaultMinimizer(minimizer_type, minimizer_algo)
        ROOT.Math.MinimizerOptions.SetDefaultStrategy(strategy)
        ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(print_level)
        if debug_mode:
            ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(1)
        else:
            ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(-1)
            ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)
        if ROOT.Math.MinimizerOptions.DefaultPrintLevel() < 0:
            ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)
        if minimizer_type == 'Minuit2':
            options = ROOT.Math.MinimizerOptions.Default('Minuit2')
            options.SetValue('StorageLevel', minuit2_storage_level)
        return None
            
    def configure_default_minimizer_options(self):
        self._configure_default_minimizer_options(self.config['minimizer_type'],
                                                  self.config['minimizer_algo'],
                                                  self.config['strategy'],
                                                  self.config['print_level'],
                                                  self.config['minuit2_storage_level'])
        return None
    
    def set_discrete_nuisance(self, discrete_nuisance:Optional[DiscreteNuisance]=None):
        if discrete_nuisance is None:
            self._discrete_nuisance = DiscreteNuisance()
        else:
            self._discrete_nuisance = discrete_nuisance
            
    def has_discrete_nuisance(self):
        return self.discrete_nuisance.has_discrete_nuisance()

    def set_runtimedef(self, expr:Optional[Union[str, Dict]]=None, ignore_if_not_applicable:bool=True):
        if not hasattr(cppyy.gbl, 'runtimedef'):
            if not ignore_if_not_applicable:
                raise RuntimeError('can not set minimizer runtime defines: namespace "runtimedef" not defined')
            return None
        runtimedef_map = combine_dict(self._DEFAULT_RUNTIMEDEF_)
        if expr is None:
            pass
        elif isinstance(expr, str):
            tokens = split_str(expr, ',', remove_empty=True)
            for token in tokens:
                runtimedef = split_str(token, '=')
                if (len(runtimedef) != 2) or (not runtimedef[1].isdigit()):
                    raise ValueError(f'invalid token in runtimedef expression: "{token}"')
                name, value = runtimedef[0], int(runtimedef[1])
                runtimedef_map[name] = value
        elif isinstance(expr, dict):
            runtimedef_map = combine_dict(runtimedef_map, expr)
        else:
            raise ValueError(f'invalid runtimedef expression: "{expr}"')
        for name, value in runtimedef_map.items():
            cppyy.gbl.runtimedef.set(name, value)
            self.stdout.info(f'Set runtimedef "{name}" = {value}')

    def set_pdf(self, pdf:"ROOT.RooAbsPdf"):
        self.pdf = pdf
    
    def set_data(self, data:"ROOT.RooAbsData"):
        self.data = data

    def set_poi(self, pois:Optional[Union["ROOT.RooRealVar", "ROOT.RooArgSet"]]=None):
        if pois is None:
            ROOT = cached_import("ROOT")
            pois = ROOT.RooArgSet()
        self._poi = pois
        
    def set_pois_for_auto_bounds(self, pois:Optional["ROOT.RooArgSet"]=None):
        self._auto_bounds_pois = pois
    
    def set_pois_for_max_bounds(self, pois:Optional["ROOT.RooArgSet"]=None):
        self._max_bounds_pois = pois
        
    def _bug_fix_create_nll(self, dataset:"ROOT.RooDataSet", nll_commands:List["ROOT.RooCmdArg"]):
        ROOT = cached_import("ROOT")
        # fix range bug
        use_named_range = any([i.GetName() == "RangeWithName" for i in nll_commands])
        use_split_range = any([i.GetName() == "SplitRange" for i in nll_commands])
        if (use_named_range and use_split_range) and isinstance(self.pdf, ROOT.RooSimultaneous):
            named_range_cmd = [i for i in nll_commands if i.GetName() == "RangeWithName"][0]
            named_ranges = named_range_cmd.getString(0).split(",")
            index_cat = self.pdf.indexCat()
            n_cat = index_cat.size()
            for named_range in named_ranges:
                for i in range(n_cat):
                    index_cat.setIndex(i)
                    cat_label = index_cat.getLabel()
                    pdf_cat = self.pdf.getPdf(cat_label)
                    observable = pdf_cat.getObservables(dataset).first()
                    range_name = f"{named_range}_{cat_label}"
                    if observable.hasRange(range_name):
                        value_range = observable.getRange(range_name)
                        observable.setRange(named_range, value_range[0], value_range[1])
            index = [i for i, cmd in enumerate(nll_commands) if cmd.GetName() == "SplitRange"][0]
            nll_commands.pop(index)
            self.stdout.warning("Renamed observable ranges to fix a bug in ROOT")
    
    def _create_nll(self, nll_commands:List["ROOT.RooCmdArg"]=None, 
                    dataset:Optional["ROOT.RooDataSet"]=None):
        ROOT = cached_import("ROOT")
        if self.pdf is None:
            raise RuntimeError('pdf not initialized')
        if nll_commands is None:
            nll_commands = list(self.nll_commands.values())
        #self.nll = self.pdf.createNLL(self.data, nll_command_list)
        for command in nll_commands:
            if command.GetName() == "RangeWithName":
                range_name = command.getString(0)
                self.stdout.info(f"Using the range \"{range_name}\" for NLL calculation")
        if dataset is None:
            if not self.data:
                raise RuntimeError('dataset not initialized')
            dataset = self.data
        if quickstats.root_version >= (6, 26, 0):
            if quickstats.root_version < (6, 28, 0):
                self._bug_fix_create_nll(dataset, nll_commands)
            nll_command_list = ROOT.RooLinkedList()
            for command in nll_commands:
                nll_command_list.Add(command)
            #nll = self.pdf.createNLL(dataset, *nll_commands)
            if self.pdf.InheritsFrom("RooSimultaneousOpt") and quickstats.root_version >= (6, 30, 0):
                self.stdout.info("Using createNLLImpl for RooSimultaneousOpt")
                nll = self.pdf.createNLLImpl(dataset, nll_command_list)
            else:
                nll = self.pdf.createNLL(dataset, nll_command_list)
        else:
            if len(nll_commands) <= 6:
                nll = self.pdf.createNLL(dataset, *nll_commands)
            # bug: can't have more than 6 arguments
            elif len(nll_commands) == 7:
                reduced_command_list = [i for i in nll_commands if i.GetName() != 'NumCPU']
                self.stdout.warning("Maximum number (6) of NLL commands reached. "
                                    "Will remove `NumCPU` from the command list")
                if len(reduced_command_list) <= 6:
                    nll = self.pdf.createNLL(dataset, *reduced_command_list)
                else:
                    raise RuntimeError("due to a bug in ROOT, nll can not have more than 6 arguments")
            elif len(nll_commands) == 8:
                reduced_command_list = [i for i in nll_commands if i.GetName() not in ['NumCPU', 'IntegrateBins']]
                self.stdout.warning("Maximum number (6) of NLL commands reached. "
                                    "Will remove `NumCPU` and `IntegrateBins` from the command list")
                if len(reduced_command_list) <= 6:
                    nll = self.pdf.createNLL(dataset, *reduced_command_list)
                else:
                    raise RuntimeError("due to a bug in ROOT, nll can not have more than 6 arguments")
            else:
                raise RuntimeError("due to a bug in ROOT, nll can not have more than 6 arguments")
        if not nll.GetName():
            nll_name = f"nll_{self.pdf.GetName()}_{dataset.GetName()}"
            nll.SetName(nll_name)
        # fix memory leak
        ROOT.SetOwnership(nll, True)
        return nll
            
    def create_nll(
        self,
        nll_commands:List["ROOT.RooCmdArg"]=None,
        dataset:Optional["ROOT.RooDataSet"]=None
    ) -> None:
        if (not self.nll) or (not self.config['reuse_nll']):
            self.nll = self._create_nll(nll_commands, dataset)
        
    def create_minimizer(self) -> None:
        ROOT = cached_import("ROOT")
        if not self.nll:
            raise RuntimeError('NLL not initialized')

        self.caching_nll.set_nll(self.nll)
        self.caching_nll.set_hide_categories(True)

        if (self.minimizer is None) or (not self.config['reuse_minimizer']):
            self.configure_default_minimizer_options()
            self.minimizer = ROOT.RooMinimizer(self.nll)
            self.minimizer.setOffsetting(self.config['minimizer_offset'])
            self.minimizer.setPrintLevel(self.config['print_level'])
            if self.config['error_level'] >= 0:
                self.minimizer.setErrorLevel(self.config['error_level'])
            self.minimizer.optimizeConst(self.config['optimize'])
            self.minimizer.setMinimizerType(self.config['minimizer_type'])
            self.minimizer.setEvalErrorWall(self.config['do_ee_wall'])
            self.minimizer.setPrintEvalErrors(self.config['num_ee'])
            self.minimizer.setVerbose(self.config['verbose'])
            self.minimizer.setProfile(self.config['timer'])
            self.minimizer.setStrategy(self.config['strategy'])
            self.minimizer.setEps(self.config['eps'])
            # https://root.cern/doc/master/VariableMetricBuilder_8cxx_source.html
            if self.config['max_calls'] != -1: 
                self.minimizer.setMaxFunctionCalls(self.config['max_calls'])
            else:
                max_calls = 5000 * self.pdf.getVariables().getSize()
                self.minimizer.setMaxFunctionCalls(max_calls)
                
            if self.config['max_iters'] != -1:
                self.minimizer.setMaxIterations(self.config['max_iters'])

        self.caching_nll.set_hide_categories(False)
    
    def construct_nll_commands(self, constrain=None, global_observables=None, 
                               conditional_observables=None, **kwargs):
        ROOT = cached_import("ROOT")
        commands = []
        if 'num_cpu' in kwargs:
            commands.append(ROOT.RooFit.NumCPU(kwargs['num_cpu'], 3))
        if 'offset' in kwargs:
            commands.append(ROOT.RooFit.Offset(kwargs['offset']))
        if ('range' in kwargs) and (kwargs['range']):
            commands.append(ROOT.RooFit.Range(kwargs['range']))
        if ('split_range' in kwargs) and (kwargs['split_range']):
            commands.append(ROOT.RooFit.SplitRange())
        if ('batch_mode' in kwargs) and hasattr(ROOT.RooFit, "BatchMode"):
            commands.append(ROOT.RooFit.BatchMode(kwargs['batch_mode']))
        if ('eval_backend' in kwargs) and hasattr(ROOT.RooFit, "EvalBackend") and quickstats.root_version >= (6, 30, 0):
            commands.append(ROOT.RooFit.EvalBackend(kwargs['eval_backend']))
        if ('int_bin_precision' in kwargs) and hasattr(ROOT.RooFit, "IntegrateBins"):
            commands.append(ROOT.RooFit.IntegrateBins(kwargs['int_bin_precision']))
        if constrain is not None:
            commands.append(ROOT.RooFit.Constrain(constrain))
            #self.stdout.warning("WARNING: Use of `Constrain` option from createNLL is not recommended", "red")
        if global_observables is not None:
            commands.append(ROOT.RooFit.GlobalObservables(global_observables))
        if conditional_observables is not None:
            commands.append(ROOT.RooFit.ConditionalObservables(conditional_observables))
        command_dict = {}
        for command in commands:
            command_dict[command.GetName()] = command
        return command_dict
    
    def set_nll_commands(
        self, nll_commands:List["ROOT.RooCmdArg"]
    ):
        command_dict = {}
        for command in nll_commands:
            command_dict[command.GetName()] = command
        self.nll_commands = command_dict
        
    def configure_nll(
        self,
        constrain=None,
        global_observables=None,
        conditional_observables=None,
        update:bool=False,
        **kwargs
    ):
        command_dict = self.construct_nll_commands(constrain=constrain, 
                                                   global_observables=global_observables,
                                                   conditional_observables=conditional_observables,
                                                   **kwargs)
        if update:
            self.nll_commands.update(command_dict)
        else:
            self.nll_commands = command_dict
        if ('range' in kwargs) and (not kwargs['range']):
            self.nll_commands.pop("RangeWithName", None)
        if ('split_range' in kwargs) and (not kwargs['split_range']):
            self.nll_commands.pop("SplitRange", None)
        self.nll = None
    
    def configure(self, **kwargs):
        minos_set = kwargs.pop('minos_set', None)
        cond_set  = kwargs.pop('cond_set' , None)
        scan_set  = kwargs.pop('scan_set' , None)
        if minos_set is not None:
            self.minos_set = minos_set
        if cond_set is not None:
            self.cond_set = cond_set
        if scan_set is not None:
            self.scan_set = scan_set
        # parse nll commands 
        nll_commands = kwargs.pop('nll_commands', [])
        if nll_commands:
            self.nll_commands = {cmd.GetName():cmd for cmd in nll_commands}
        
        # configure minimizer settings
        for arg in kwargs:
            if arg not in self._config:
                raise ValueError('{} is not a valid minimizer config'.format(arg))
            self._config[arg] = kwargs[arg]
        
        self.fit_options = kwargs
        self.scan_options = {k:v for k,v in kwargs.items() if k not in self._SCAN_EXCLUDE_CONFIG_}

    def set_fit_range(self, name: Optional[str], split_range: bool = True) -> None:
        ROOT = cached_import("ROOT")
        self.nll = None
        if name is not None:
            self.nll_commands["RangeWithName"] = ROOT.RooFit.Range(name)
        else:
            self.nll_commands.pop("RangeWithName", None)
        if split_range:
            self.nll_commands['SplitRange'] = ROOT.RooFit.SplitRange()
        else:
            self.nll_commands.pop("SplitRange", None)

    def unset_fit_range(self) -> None:
        self.set_fit_range(None, False)
        
    def expand_poi_bounds(self, threshold:float=0.1):
        ROOT = cached_import("ROOT")
        if (not self.auto_bounds_pois) and (not self.max_bounds_pois):
            return False
        expanded_bounds = False
        for bound_type, pois in [('max', self.max_bounds_pois),
                                 ('both', self.auto_bounds_pois)]:
            if not pois:
                continue
            orig_pois_at_min = ROOT.RooArgSet()
            new_pois_at_min = ROOT.RooArgSet()
            orig_pois_at_max = ROOT.RooArgSet()
            new_pois_at_max = ROOT.RooArgSet()
            if bound_type == "max":
                RooArgSet.expand_parameters_range(pois, threshold, True, False,
                                                  orig_pois_at_min,
                                                  new_pois_at_min,
                                                  orig_pois_at_max,
                                                  new_pois_at_max)
            elif bound_type == 'both':
                RooArgSet.expand_parameters_range(pois, threshold, True, True,
                                                  orig_pois_at_min,
                                                  new_pois_at_min,
                                                  orig_pois_at_max,
                                                  new_pois_at_max)
            else:
                raise ValueError(f'unknown bound type: {bound_type}')
            threshold_pc = threshold * 100
            for orig_poi, new_poi in zip(orig_pois_at_min, new_pois_at_min):
                expanded_bounds = True
                self.stdout.info(f'Parameter {orig_poi.GetName()} has value {orig_poi.getVal()} which is within '
                                 f'{threshold_pc}% from the low boundary {orig_poi.getMin()}. Will enlarge range '
                                 f'to [{new_poi.getMin()}, {new_poi.getMax()}].')
            for orig_poi, new_poi in zip(orig_pois_at_max, new_pois_at_max):
                expanded_bounds = True
                self.stdout.info(f'Parameter {orig_poi.GetName()} has value {orig_poi.getVal()} which is within '
                                 f'{threshold_pc}% from the max boundary {orig_poi.getMax()}. Will enlarge range '
                                 f'to [{new_poi.getMin()}, {new_poi.getMax()}].')
        return expanded_bounds
    
    def check_param_boundary(self):
        ROOT = cached_import("ROOT")
        if not self.nll:
            self.stdout.warning('Failed to check boundary values: nll not set')
            return None
        nll_params = self.nll.getParameters(self.data.get())
        nll_params.remove(self.poi)
        ROOT.RooStats.RemoveConstantParameters(nll_params)
        nll_params = RooArgSet.select_by_class(nll_params, 'RooRealVar')
        boundary_params = RooArgSet.get_boundary_parameters(nll_params)
        if boundary_params:
            self.stdout.warning('Found parameters near boundary (within 1 sigma) after fit.')
            for param in boundary_params:
                self.stdout.warning(f'    Parameter = {param.GetName()}, Value = {param.getVal()}, '
                                    f'RangeLo = {param.getMin()}, RangeHi = {param.getMax()}, '
                                    f'ErrorLo = {param.getErrorLo()}, ErrorHi = {param.getErrorHi()}',
                                    bare=True)
                
    def save_fit_result(
        self,
        named:bool=False
    ):
        ROOT = cached_import("ROOT")
        if not self.minimizer:
            self.stdout.warning('Failed to save fit result: minimizer not set')
            return None
        if named:
            data_name = self.data.GetName()
            save_name = f"fitresult_{self.name}_{data_name}"
            save_title = f"Result of fit of p.d.f. {self.name} to dataset {data_name}"
            self.stdout.info(f'ExtendedMinimizer::minimize("{self.name}") saving results as {save_name}')
            self.fit_result = self.minimizer.save(save_name, save_title)
        else:
            self.fit_result = self.minimizer.save()
        ROOT.SetOwnership(self.fit_result, True)
        
    def get_nll_val(self):
        if self.apply_discrete==2:
            correction = 0
            for mp in self.discrete_nuisance.multipdfs:
                correction += mp.getCorrection()
            return self.nll.getVal() + correction
        else:
            return self.nll.getVal()
        
    def minimize(self, nll=None, cascade:bool=True, **kwargs):
        self.configure(**kwargs)
        if self.apply_discrete == 2:
            self.config["optimize"] = 0
            self.stdout.info(f'Set optimize to 0 when using discrete nuisance minimization mode for RooFit PDF.')
        if nll is None:
            self.create_nll()
        else:
            self.nll = nll
            
        self.nom_nll = self.get_nll_val()
        self.min_nll = None
        self.discrete_nuisance.set_freeze_flag(self.config['freeze_disassociated_params'])
            
        if self.cond_set:
            nll_variables = self.nll.getVariables()
            selected_variables = nll_variables.selectCommon(self.cond_set)
            selected_variables.assignValueOnly(self.cond_set)
            RooArgSet.set_constant_state(selected_variables, True)
                    
        self.create_minimizer()
        
        status = 0
        nll_variables = self.nll.getVariables()
        perform_minimization = RooArgSet.select_by_constant_state(nll_variables, False)
        if not perform_minimization:
            self.stdout.info('ExtendedMinimizer::minimize("{}") no floating parameters found '
                             '-- skipping minimization'.format(self.name))
            self.min_nll = self.get_nll_val()
        else:
            self.discrete_nuisance.freeze_discrete_params(True)

            if self.config['prefit_eps'] > 0:
                self.stdout.info('ExtendedMinimizer::minimize("{}") prefit minimization'.format(self.name))
                # prefit minimization
                self.minimizer.setStrategy(self.config['prefit_strategy'])
                self.minimizer.setEps(self.config['prefit_eps'])
                self.robust_minimize(cascade=cascade, is_prefit=True)
                self.minimizer.setStrategy(self.config['strategy'])
                self.minimizer.setEps(self.config['eps'])

            # actual minimization done here
            if (self.has_discrete_nuisance() and self.config['do_discrete_iteration']):
                status = self.discrete_minimize(cascade=cascade)
            else:
                status = self.robust_minimize(cascade=cascade)

            # Evaluate errors with improve
            if self.config['improve']:
                self.minimizer.improve()
                
            # Evaluate errors with Hesse
            if self.config['hesse']:
                self.minimizer.hesse()
    
            # Eigenvalue and eigenvector analysis
            if self.config['eigen']:
                self.eigen_analysis()
            
            # Evaluate errors with Minos
            if self.config['minos']:
                if self.minos_set.size() > 0:
                    self.minimizer.minos(self.minos_set)
                else:
                    self.minimizer.minos()
                    
            self.discrete_nuisance.freeze_discrete_params(False)
            
            # post-processing
            if self.config['check_boundary']:
                self.check_param_boundary()
        
            self.min_nll = self.get_nll_val()
        
            if self.config['scan']:
                self.find_sigma()

            # if the 'scan' option is used, minimizer will get deleted before this line
            if self.minimizer is not None:
                self.save_fit_result(named=self.config['save'])
                
            if self.cond_set:
                nll_variables = self.nll.getVariables()
                selected_variables = nll_variables.selectCommon(self.cond_set)
                selected_variables.assign(self.cond_set)

        # dispose of minimizer
        if not self.config['reuse_minimizer']:
            self.minimizer = None
            
        self.status = status
        return status

    def robust_minimize(self, cascade:bool=True, is_prefit:bool=False):
        self.stdout.debug('Begin robust minimization.')
        retry    = self.config['retry']
        eps_init = self.config['prefit_eps'] if is_prefit else self.config['eps']
        strategy_init = self.config['prefit_strategy'] if is_prefit else self.config['strategy']
        minimizer_type = self.config['minimizer_type']
        minimizer_algo = self.config['minimizer_algo']
        
        def require_cascade(fit_status:int) -> bool:
            return cascade and (fit_status not in [0, 1])
        status = self.single_minimize(minimizer_type, minimizer_algo)
        # repeat if fit failed or poi(s) at boundary
        expanded_pois = self.expand_poi_bounds()

        retry_policy = RetryPolicy.parse(self.config['retry_policy'])
        if retry_policy == RetryPolicy.NORETRY:
            retry = 0

        if self.config['retry_from_initial']:
            initial_params_all = self.nll.getParameters(0)
            initial_snapshot = initial_params_all.snapshot()
            self.stdout.info("Save initial snapshot")
        else:
            initial_snapshot = None

        eps = eps_init
        strategy = strategy_init

        while ((require_cascade(status) or expanded_pois or (eps != eps_init)) and (retry > 0)):
            retry -= 1
            last_status = status

            self.stdout.warning(f'ExtendedMinimizer::robust_minimize("{self.name}"): eps {eps}; strategy {strategy}; status {status}.')
            if not expanded_pois:
                if retry_policy == RetryPolicy.DYNAMIC_EPS:
                    if require_cascade(status):
                        eps *= self.config['retry_eps_ratio']
                    else:
                        eps /= self.config['retry_eps_ratio']
                elif retry_policy == RetryPolicy.DYNAMIC_STRATEGY and strategy < 2:
                    strategy += 1
            self.stdout.info(f'Retrying with eps {eps} and strategy {strategy}')
            self.minimizer.setEps(eps)
            self.minimizer.setStrategy(strategy)
            
            if initial_snapshot is not None:
                initial_params_all.assign(initial_snapshot)
                self.stdout.info("Load initial snapshot")
            
            status = self.single_minimize(minimizer_type, minimizer_algo)
            expanded_pois = self.expand_poi_bounds()

            if not require_cascade(last_status) and require_cascade(status) and retry > 1:
                retry = 1
            
        if status not in [0, 1]:
            self.stdout.error(f'ExtendedMinimizer::robust_minimize("{self.name}") fit failed with status {status}')
        
        self.minimizer.setStrategy(strategy_init)
        self.minimizer.setEps(eps_init)
        
        return status

    def single_minimize(self, minimizer_type:str, minimizer_algo:str):
        self.stdout.debug('Begin single minimization.')
        if self.minimizer is None:
            self.create_minimizer()
        self.discrete_nuisance.freeze_discrete_params(True)
        if self.config['set_zero_point']:
            self.caching_nll.set_nll(self.nll)
        else:
            self.caching_nll.set_nll()
        self.caching_nll.set_zero_point()
        if self.config['prefit_hesse']:
            self.minimizer.hesse()
            self.caching_nll.update_zero_point()
        #nll_params = self.nll.getParameters(0)
        #RooArgSet.save_data_as_txt(nll_params, 'minimizer_prefit_result.txt', 8)
        status = self.minimizer.minimize(minimizer_type, minimizer_algo)
        #RooArgSet.save_data_as_txt(nll_params, 'minimizer_postfit_result.txt', 8)
        if self.config['postfit_hesse']:
            self.caching_nll.update_zero_point()
            self.minimizer.hesse()
        self.caching_nll.clear_zero_point()
        self.discrete_nuisance.freeze_discrete_params(False)
        return status

    def discrete_minimize(self, cascade:bool=True):
        """Minimization involving discrete nuisances
        """
        ROOT = cached_import("ROOT")
        status = 0
        
        do_short_combination = self.config['do_short_combination']
        if do_short_combination:
            self.stdout.info('Begin discrete minimization with short combinations.')
            with timer() as t:
                status = self.robust_minimize(cascade=cascade)
                self.min_nll = self.get_nll_val()
                prev_nll = self.min_nll
            self.stdout.info(f'First overall minimization finished in {t.interval:.3f} s.')
            with timer() as t:
                max_iteration = self.config['max_short_combination_iteration']
                min_tol = self.config['discrete_min_tol']
                for i in range(max_iteration):
                    self.stdout.info(f'Current iteration: {i + 1}')
                    status = self.iterative_minimize(cascade=cascade)
                    delta_nll = abs(prev_nll - self.min_nll)
                    self.stdout.info(f'Previous NLL = {prev_nll}, Minimum NLL = {self.min_nll}, Delta NLL = {delta_nll}')
                    if delta_nll < min_tol:
                        self.stdout.info(f'Delta NLL is within the required tolerence of {min_tol}.')
                        break
                    prev_nll = self.min_nll
                num_iteration = i + 1
            self.stdout.info(f'Discrete minimization finished in {num_iteration} iterations. Iterations time taken: {t.interval:.3f} s')
        else:
            self.stdout.info('Begin discrete minimization with full combinations.')
            with timer() as t:
                clean_snapshot = ROOT.RooArgSet()
                nll_params = self.nll.getParameters(0)
                nll_params.remove(self.discrete_nuisance.multipdf_cats)
                nll_params.snapshot(clean_snapshot)
                #??
                #min_nll = 10 + nll.getVal()
                self.multiple_minimize(mode=0, clean_snapshot=clean_snapshot, cascade=cascade)
                if len(self.discrete_nuisance.multipdfs) > 1:
                    self.multiple_minimize(mode=1, clean_snapshot=clean_snapshot, cascade=cascade)
                    self.multiple_minimize(mode=2, clean_snapshot=clean_snapshot, cascade=cascade)
                if self.discrete_nuisance.freeze_flag:
                    self.discrete_nuisance.freeze_discrete_params(True)
                    status = self.robust_minimize(cascade=cascade)
                    self.discrete_nuisance.freeze_discrete_params(False)
            self.stdout.info(f'Discrete minimization finished. Total time taken: {t.interval:.3f} s')
        final_combination = self.discrete_nuisance.get_current_pdf_indices()
        self.stdout.info(f'Final index combination: {list(final_combination)}')
        return status
        
    # taken from https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/blob/main/src/CascadeMinimizer.cc
    def iterative_minimize(self, cascade:bool=True):
        ROOT = cached_import("ROOT")
        with timer() as t:
            min_tol = self.config['discrete_min_tol']
            if self.min_nll is None:
                self.min_nll = self.get_nll_val()
            if abs(self.min_nll - self.get_nll_val()) > min_tol:
                self.robust_minimize(cascade=cascade)
            nll_params_all = self.nll.getParameters(0)
            all_snapshot = nll_params_all.snapshot()
            pre_min_nll = self.min_nll
    
            self.discrete_nuisance.freeze_discrete_params(True)
    
            params_to_freeze = ROOT.RooArgSet(self.discrete_nuisance.all_params)
            params_to_freeze.remove(self.discrete_nuisance.multipdf_params)
            params_to_freeze.add(self.poi)
            ROOT.RooStats.RemoveConstantParameters(params_to_freeze)
            RooArgSet.set_constant_state(params_to_freeze, True)
            nll_params = self.nll.getParameters(0)
            nll_params.remove(self.discrete_nuisance.multipdf_cats)
            ROOT.RooStats.RemoveConstantParameters(nll_params)
            clean_snapshot = nll_params.snapshot()
            # now cycle and fit
            status = 0
            # start frm simplest scan, this is the full scan if do_short_combination is off
            new_pdfIndex = self.multiple_minimize(clean_snapshot=clean_snapshot, cascade=cascade, mode=0)
            RooArgSet.set_constant_state(params_to_freeze, False)
            if new_pdfIndex:
                # run one last fully floating fit to maintain RooFitResult
                status = self.robust_minimize(cascade=cascade)
            else:
                nll_params_all.assign(all_snapshot)
                self.min_nll = pre_min_nll
    
            self.discrete_nuisance.freeze_discrete_params(False)
        self.stdout.info(f'Finished iteration. Total time taken: {t.interval:.3f} s.')
        return status
        
    # taken from https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/blob/main/src/CascadeMinimizer.cc
    def multiple_minimize(self, clean_snapshot:"ROOT.RooArgSet", cascade:bool=True, mode:int=0,
                          contributing_indices:Optional[List[np.ndarray]]=None):
        if not self.has_discrete_nuisance():
            raise RuntimeError('multiple minimize should only be used when discrete nuisances are available')
        hide_constants = self.config['multimin_hide_constants']
        mask_constraints = self.config['multimin_mask_constraints']
        mask_channels = self.config['multimin_mask_channels']
        mask_channels_ex = (mask_channels == 2)
        self.caching_nll.set_nll(self.nll)

        strategy_tmp = self.config['strategy']
        self.config['strategy'] = 0

        new_discrete_minimum = False
        multipdf_cats = self.discrete_nuisance.multipdf_cats
        num_cats = len(multipdf_cats)
        pdf_sizes = self.discrete_nuisance.get_pdf_sizes()
        best_indices = self.discrete_nuisance.get_current_pdf_indices()
        self.stdout.info(f'Current index combination: {list(best_indices)}')
        self.stdout.info(f'Current NLL: {self.get_nll_val()}')

        if (mode == 0) or (contributing_indices is None):
            contributing_indices = self.discrete_nuisance.create_contributing_indices()
        
        # keep hold of best fitted parameters
        nll_params = self.nll.getParameters(0)
        nll_params.remove(self.discrete_nuisance.multipdf_cats)
        nll_params_snapshot = nll_params.snapshot()

        if mask_channels:
            self.caching_nll.set_mask_non_discrete_channels(True)
        if hide_constants:
            self.caching_nll.set_hide_constants(True)
            if mask_constraints:
                self.caching_nll.set_mask_constraints(True)
            self.minimizer = None

        if (mode in [0, 1]):
            n_combination = self.discrete_nuisance.get_n_orthogonal_combination()
            self.stdout.info(f'Generating {n_combination} orthogonal index combinations.')
            combinations = self.discrete_nuisance.get_orthogonal_combinations()
        else:
            n_combination = self.discrete_nuisance.get_n_orthogonal_combination(contributing_indices)
            self.stdout.info(f'Generating {n_combination} index combinations.')
            combinations = self.discrete_nuisance.get_total_combinations(contributing_indices)

        # reorder combinations starting from indices closest to the best indices
        combinations = self.discrete_nuisance.reorder_combinations(combinations, best_indices)
        
        # filter combinations that are not contributing
        combinations = self.discrete_nuisance.filter_combinations(combinations, contributing_indices)

        self.stdout.info(f'Total number of combinations after filtering contributing indices: {len(combinations)}')

        new_discrete_minimum = False
        # skip the best fit case if already done
        i_start = 1 if (mode != 0) else 0
        self.stdout.info(f'Begin fast loop minimization of {len(combinations)} index combinations.')
        with timer() as t:
            fit_counter = 0
            max_deviation = 5
            multipdf_cats = self.discrete_nuisance.multipdf_cats
            # the overhead in this for loop should be way less than the fit time
            for combination in combinations[i_start:]:
                changed_index = self.discrete_nuisance.set_category_indices(combination)
                if fit_counter > 0:
                    nll_params.assignValueOnly(clean_snapshot)
                if mask_channels_ex:
                    self.discrete_nuisance.fix_non_target_cats(changed_index)
                    self.caching_nll.set_mask_non_discrete_channels(True)
                self.discrete_nuisance.freeze_discrete_params(True)
                status = self.robust_minimize(cascade=cascade)
                if mask_channels_ex:
                    self.discrete_nuisance.float_all_cats()
                    self.caching_nll.set_mask_non_discrete_channels(False)
                
                self.discrete_nuisance.freeze_discrete_params(False)
                fit_counter += 1
                current_nll = self.get_nll_val()
                delta_nll = current_nll - self.min_nll
                self.stdout.debug(f'Index combination: {list(combination)}, NLL = {current_nll}, delta NLL = {delta_nll}')
                # found new minimum
                if (delta_nll < 0):
                    self.min_nll = current_nll
                    nll_params_snapshot.assignValueOnly(nll_params)
                    # set the best indices again
                    if not np.array_equal(best_indices, combination):
                        self.stdout.info(f'Found a better minimum at {list(combination)}. '
                                         f'New NLL = {current_nll}, delta NLL =  {delta_nll}.')
                        new_discrete_minimum = True
                        best_indices = combination.copy()
                # discard pdf that gives large nll
                if (mode == 1):
                    if (delta_nll > max_deviation):
                        index_diff = np.where(best_indices != combination)[0]
                        diff_count = index_diff.shape[0]
                        if diff_count == 1:
                            index_diff = index_diff[0]
                            cat = self.discrete_nuisance.multipdf_cats.at(index_diff)
                            cat_index = cat.getIndex()
                            if (cat_index != best_indices[index_diff]):
                                contributing_indices[index_diff][cat_index] = 0
                                pdf_name = self.discrete_nuisance.multipdfs.at(index_diff).GetName()
                                self.stdout.info(f'Found pdf index that gives large nll. Discarding pdf index '
                                                 f'{cat_index} from the multipdf "{pdf_name}"')
            # assign best indices
            self.discrete_nuisance.set_category_indices(best_indices)
            nll_params.assignValueOnly(nll_params_snapshot)
        n_combination_run = len(combinations) - i_start
        time_per_combination = (t.interval / n_combination_run)
        
        self.stdout.info(f'Done {n_combination_run} combinations in {t.interval:.3f} s '
                         f'({time_per_combination:.4f} s per combination). New discrete minimum? {new_discrete_minimum}')
 
        self.config['strategy'] = strategy_tmp
        
        if mask_channels:
            self.caching_nll.set_mask_non_discrete_channels(False)
            
        if hide_constants:
            self.caching_nll.set_hide_constants(False)
            if mask_constraints:
                self.caching_nll.set_mask_constraints(False)
            self.minimizer = None
            
        return new_discrete_minimum

    def use_limits(self, par:"ROOT.RooRealVar", val:float):
        if (val < par.getMin()):
            self.stdout.warning(f'ExtendedMinimizer::use_limits("{self.name}") {par.GetName()} = {val} '
                                f'limited by minimum at {par.getMin()}')
            return par.getMin()
        elif (val > par.getMax()):
            self.stdout.warning(f'ExtendedMinimizer::use_limits("{self.name}") {par.GetName()} = {val} '
                                f'limited by maximum at {par.getMax()}')
            return par.getMax()
        else:
            return val
    
    def find_sigma(self):
        ROOT = cached_import("ROOT")
        if self.scan_set.getSize() == 0:
            attached_set = self.nll.getVariables()
            ROOT.RooStats.RemoveConstantParameters(attached_set)
            self.scan_set = attached_set

        for v in self.scan_set:
            variables = self.pdf.getVariables()
            ROOT.RooStats.RemoveConstantParameters(variables)
            variables.add(v, ROOT.kTRUE)
            snapshot = variables.snapshot()
            
            self.config['n_sigma'] = abs(self.config['n_sigma'])
            val = v.getVal()
            err = self.config['n_sigma'] * v.getError()
            
            min_nll = self.min_nll
            hi = self._find_sigma(min_nll, val+err, val, v, 
                                  self.scan_options, self.config['n_sigma'],
                                  self.config['precision'], self.config['eps'])
            variables.__assign__(snapshot)
            lo = self._find_sigma(min_nll, val-err, val, v, 
                                  self.scan_options, -self.config['n_sigma'],
                                  self.config['precision'], self.config['eps'])
            variables.__assign__(snapshot)
            self.min_nll = min_nll
            
            _lo = lo if not math.isnan(lo) else 1.0
            _hi = hi if not math.isnan(hi) else -1.0
            v.setAsymError(_lo, _hi)
            
            self.stdout.info(f'ExtendedMinimizer::minimize("{self.name}")')
            v.Print()

    # _____________________________________________________________________________
    # Find the value of sigma evaluated at a specified nsigma, assuming NLL -2logL is roughly parabolic in par.
    # The precision is specified as a fraction of the error, or based on the Minuit default tolerance.
    # Based on https://svnweb.cern.ch/trac/atlasoff/browser/PhysicsAnalysis/HiggsPhys/HSG3/WWDileptonAnalysisCode/HWWStatisticsCode/trunk/macros/findSigma.C
    # by Aaron Armbruster <aaron.james.armbruster@cern.ch> and adopted by Tim Adye <T.J.Adye@rl.ac.uk>.
    def _find_sigma(self, nll_min:float, val_guess:float, val_mle:float,
                    par:"ROOT.RooRealVar", scan_options:Dict, n_sigma:float,
                    precision:float, fit_tol:float):
        '''
        args:
            precision: fit precision
            fit_tol: fit tolerance
        '''
        ROOT = cached_import("ROOT")
        max_iter = 25

        param_name = par.GetName()
        val_guess = self.use_limits(par, val_guess)
        direction = +1 if n_sigma >= 0.0 else -1
        n_damping = 1
        damping_factor = 1.0
        guess_to_corr = {}
        t_mu = ROOT.TMath.QuietNaN()
        front_str = f'ExtendedMinimizer::findSigma("{self.name}") '
        
        
        if precision <= 0.0:
            # RooFit default tolerance is 1.0
            tol = fit_tol if fit_tol > 0.0 else 1.0
            eps = 0.001 * tol
            precision = 5.0*eps / (n_sigma**2)
        
        temp_options = {**scan_options}
        snapshot = self.cond_set.snapshot()
        for i in range(max_iter):
            self.stdout.info(f'{front_str} Parameter {par.GetName()} {n_sigma}sigma '
                             f'iteration {i + 1}: start {val_guess} (MLE {val_guess - val_mle})', bare=True)
            val_pre = val_guess
            
            poi_set = ROOT.RooArgSet(par).snapshot()
            poi_set.first().setVal(val_guess)
            
            scan_options['reuse_nll'] = 1
            scan_options['scan']      = 0
    
            self.minimize(cond_set=poi_set, 
                          **scan_options)
            
            self.cond_set = snapshot
            scan_options.clear()
            scan_options.update(temp_options)
            
            nll = self.min_nll
            poi_set = None
            
            t_mu = 2.0 * (nll - nll_min)
            sigma_guess = abs(val_guess-val_mle)
            if (t_mu > 0.01):
                sigma_guess /= math.sqrt(t_mu)
            else:
                sigma_guess *= 10.0 # protect against t_mu <=0 and also don't move too far
            
            corr = damping_factor*(val_pre - val_mle - n_sigma*sigma_guess)
            
            for guess in guess_to_corr:
                if (abs(guess - val_pre) < direction*val_pre*0.02):
                    damping_factor *= 0.8
                    self.stdout.info(f'{front_str} Changing damping factor to {damping_factor}', bare=True)
                    n_damping += 1
                    if n_damping > 10:
                        n_damping = 1
                        damping_factor = 1.0
                    corr *= damping_factor
                    break
            
            # subtract off the difference in the new and damped correction
            val_guess -= corr
            guess_to_corr[val_pre] = corr          
            val_guess = self.use_limits(par, val_guess)
            rel_precision = precision*abs(val_guess-val_mle)
            delta = val_guess - val_pre
            
            
            self.stdout.info('{} {} {:.3f} (MLE {:.3f}) -> {:.3f} (MLE {:.3f}), '
                             'change {:.3f}, precision {:.3f}, -2lnL {:.4f}, sigma(guess) {:.3f})'.format(
                             front_str, param_name, val_pre, val_pre - val_mle, val_guess, val_guess - val_mle,
                             delta, rel_precision, t_mu, sigma_guess), bare=True)
            self.stdout.info('{} NLL:                 {}'.format(front_str, nll), bare=True)
            self.stdout.info('{} delta(NLL):          {}'.format(front_str, nll - nll_min), bare=True)
            self.stdout.info('{} nsigma*sigma(pre):   {}'.format(front_str, abs(val_pre - val_mle)), bare=True)
            self.stdout.info('{} sigma(guess):        {}'.format(front_str, sigma_guess), bare=True)
            self.stdout.info('{} par(guess):          {}'.format(front_str, val_guess + corr), bare=True)
            self.stdout.info('{} best-fit val:        {}'.format(front_str, val_mle), bare=True)
            self.stdout.info('{} tmu:                 {}'.format(front_str, t_mu), bare=True)
            self.stdout.info('{} Precision:           {}'.format(front_str, direction*val_guess*precision), bare=True)
            self.stdout.info('{} Correction:          {}'.format(front_str, -corr), bare=True)
            self.stdout.info('{} nsigma*sigma(guess): {}'.format(front_str, abs(val_guess-val_mle)), bare=True)
            
            if abs(delta) <= rel_precision:
                break
        if i >= max_iter:
            self.stdout.error(f'find_sigma failed after {i + 1} iterations')
            return ROOT.TMath.QuietNan()
        
        err = val_guess - val_mle
        self.stdout.info('{} {} {}sigma = {:.3F} at -2lnL = {:4f} after {} iterations'.format(
                         front_str, par.GetName(), n_sigma, err, t_mu, i+1), bare=True)
        
        return err
    
    def create_profile(self, var:"ROOT.RooRealVar", lo:float, hi:float, nbins:int):
        ROOT = cached_import("ROOT")
        map_poi2nll = {}
        
        ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(-1)
        ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)
        
        variables = self.pdf.getVariables()
        ROOT.RooStats.RemoveConstantParameters(variables)
        
        # unconditional fit
        buffer_scan_options = self.scan_options.copy()
        
        buffer_scan_options['reuse_nll'] = 1
        
        self.minimize(**buffer_scan_options)
        
        map_poi2nll[var.getVal()] = 2 * self.min_nll
        snapshot = variables.snapshot()
        
        ## these lines should be improved
        buffer_scan_options.pop('reuse_nll')
        self.scan_options.clear()
        self.scan_options.update(buffer_scan_options)
        
        # perform the scan
        delta_x = (hi - lo) / nbins
        for i in range(nbins):
            variables.__assign__(snapshot)
            var.setVal(lo + i * delta_x)
            var.setConstant(1)
            
            buffer_scan_options['reuse_nll'] = 1
            
            self.minimize(**buffer_scan_options)
            map_poi2nll[var.getVal()] = 2 * self.min_nll
            
            ## these lines should be improved
            buffer_scan_options.pop('reuse_nll')
            self.scan_options.clear()
            self.scan_options.update(buffer_scan_options)
            
            var.setConstant(0)
        variables.__assign__(snapshot)
        graphs = self.prepare_profile(map_poi2nll)
        return graphs
    
    def prepare_profile(self, map_poi2nll:Dict):
        ROOT = cached_import("ROOT")
        x, y = [], []
        nbins = len(map_poi2nll) - 1
        
        xlo = float('inf') 
        xhi = float('-inf') 
        
        for nll_prev in map_poi2nll:
            nll = map_poi2nll[nll_prev]
            if (not math.isinf(nll)) and (abs(nll) < 10**20):
                x.append(nll_prev)
                y.append(nll)
        
        nr_points = len(x)
        
        if nr_points == 0:
            raise ValueError("map_poi2nll is empty")
            
        x, y = zip(*sorted(zip(x, y)))
        x = np.array(x, dtype=float)
        y = np.array(y, dtype=float)
            
        if (x[0] < xlo):
            xlo = x[0]
            
        if x[-1] > xhi:
            xhi = x[-1]
        
        g = ROOT.TGraph(nr_points, x, y)
        
        min_nll = ROOT.TMath.Infinity()
        min_nll_x = 0.0
        
        for i in range(g.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g.GetPoint(i, tmpX, tmpY)
            if (tmpY < min_nll):
                min_nll = tmpY
                min_nll_x = tmpX
                
        for i in range(g.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g.GetPoint(i, tmpX, tmpY)
            tmpY -= min_nll
            g.SetPoint(i, tmpX, tmpY)

        min_nll = ROOT.TMath.Infinity()
        min_nll_x = 0.0
        
        # Make smooth interpolated graph for every folder in poi range, find minimum nll
        x_interpolated_coarse, y_interpolated_coarse = [], []
        
        stepsize_coarse = abs(xhi - xlo) / nbins
        tmpX = xlo
        while (tmpX <= xhi):
            tmpY = g.Eval(tmpX, 0)
            x_interpolated_coarse.append(tmpX)
            y_interpolated_coarse.append(tmpY)
            tmpX += stepsize_coarse
            
        x_interpolated_coarse = np.array(x_interpolated_coarse, dtype=float)
        y_interpolated_coarse = np.array(y_interpolated_coarse, dtype=float)
        nr_points_interpolated_coarse = len(x_interpolated_coarse)
        g_interpolated_coarse = ROOT.TGraph(nr_points_interpolated_coarse,
                                            x_interpolated_coarse,
                                            y_interpolated_coarse)
        
        x_interpolated, y_interpolated = [], []
        two_step_interpolation = False
        stepsize = abs(xhi - xlo) / (10 * nbins)
        while (tmpX <= xhi):
            tmpY = 0.0
            if two_step_interpolation:
                tmpY = g_interpolated_coarse.Eval(tmpX, 0, "S")
            else:
                tmpY = g.Eval(tmpX, 0, "S")
            x_interpolated.append(tmpX)
            y_interpolated.append(tmpY)
            tmpX += stepsize
            
        x_interpolated = np.array(x_interpolated, dtype=float)
        y_interpolated = np.array(y_interpolated, dtype=float)
        nr_points_interpolated = len(x_interpolated)
        g_interpolated = ROOT.TGraph(nr_points_interpolated,
                                     x_interpolated,
                                     y_interpolated)
        
        for i in range(g_interpolated.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g_interpolated.GetPoint(i, tmpX, tmpY)
            if (tmpY < min_nll):
                min_nll = tmpY
                min_nll_x = tmpX
        
        for i in range(g.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g.GetPoint(i, tmpX, tmpY)
            tmpY -= min_nll
            g.SetPoint(i, tmpX, tmpY)
        
        for i in range(g_interpolated.GetN()):
            tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
            g_interpolated.GetPoint(i, tmpX, tmpY)
            tmpY -= min_nll
            g_interpolated.SetPoint(i, tmpX, tmpY)
        
        g.SetLineWidth(2)
        g.SetMarkerStyle(20)
        
        g_interpolated.SetLineWidth(2)
        g_interpolated.SetMarkerStyle(20)
        
        return (g, g_interpolated)

    def eigen_analysis(self):
        ROOT = cached_import("ROOT")
        if not self.minimizer:
            self.stdout.warning('Failed to get Hessian matrix: minimizer not set')
            return None
        # Obtain Hessian matrix either from patched Minuit or after inversion
        # TMatrixDSym G = Minuit2::MnHesse::lastHessian();
        last_fit = self.minimizer.lastMinuitFit()
        if not last_fit:
            self.stdout.warning('Failed to get Hessian matrix: no fit performed')
            return None
        
        self.Hessian_matrix = last_fit.covarianceMatrix().Invert()
            
        if not isinstance(self.Hessian_matrix, ROOT.TMatrixDSym):
            raise ValueError('invalid Hessian matrix')
        n = self.Hessian_matrix.GetNrows()
        
        # construct reduced Hessian matrix
        Gred = ROOT.TMatrixDSym(n)
        for i in range(n):
            for j in range(n):
                norm = math.sqrt(self.Hessian_matrix(i, i)*self.Hessian_matrix(j, j))
                Gred[i][j] = self.Hessian_matrix(i, j)/norm
        
        # perform eigenvalue analysis using ROOT standard tools
        Geigen = ROOT.TMatrixDSymEigen(Gred)
        
        self.eigen_values = Geigen.GetEigenValues()
        self.eigen_vectors = Geigen.GetEigenVectors()
        
        # simple printing of eigenvalues and eigenvectors
        self.eigen_values.Print()
        self.eigen_vectors.Print()

    def get_floating_nll_params(self):
        ROOT = cached_import("ROOT")
        if not self.nll:
            raise RuntimeError('NLL not initialized')
        nll_params = self.nll.getParameters(0)
        ROOT.RooStats.RemoveConstantParameters(nll_params)
        return nll_params

    def print_floating_nll_params(self):
        nll_params = self.get_floating_nll_params()
        for param in nll_params:
            if param.InheritsFrom('RooRealVar'):
                self.stdout.info(f'{param.GetName()} {param.getVal()}')
            elif param.InheritsFrom('RooCategory'):
                self.stdout.info(f'{param.GetName()} {param.currentIndex()}')
            else:
                self.stdout.info(f'{param.GetName()}')
