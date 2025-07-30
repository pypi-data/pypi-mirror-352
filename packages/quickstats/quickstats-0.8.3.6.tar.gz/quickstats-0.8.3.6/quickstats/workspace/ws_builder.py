from typing import Dict, Any, Optional, List, Union, Tuple
import os

import numpy as np

from quickstats import timer, cached_import, semistaticmethod
from quickstats.maths.numerics import is_float, pretty_value
from quickstats.utils.common_utils import (
    remove_list_duplicates,
    format_delimiter_enclosed_text
)
from quickstats.utils.string_utils import split_str
from quickstats.interface.root import RooWorkspace, RooDataSet, RooDataHist
from quickstats.interface.root.helper import get_default_print_content
from quickstats.interface.cppyy.vectorize import list2vec
from quickstats.workspace.settings import (
    DATA_SOURCE_COUNTING,
    DATA_SOURCE_ASCII,
    DATA_SOURCE_HISTOGRAM,
    DATA_SOURCE_NTUPLE,
    DATA_SOURCE_ARRAY,
    CATEGORY_KEYWORD,
    COUNTING_MODEL,
    USERDEF_MODEL,
    EXTERNAL_MODEL,
    HISTOGRAM_MODEL,
    SELF_SYST_DOMAIN_KEYWORD,
    COUNTING_ANALYSIS,
    SHAPE_ANALYSIS,
    EXT_MODEL_ACTION_ITEM,
    EXT_MODEL_ACTION_FIX,
    EXT_MODEL_ACTION_RENAME,
    EXT_MODEL_ACTION_EXTSYST,
    RANGE_NAME_SB_LO,
    RANGE_NAME_SB_HI,
    RANGE_NAME_BLIND,
    OBS_SET,
    POI_SET,
    NUIS_SET,
    GLOB_SET,
    DataStorageType,
    SampleFactorType,
    ConstraintType
)
from quickstats.workspace.translation import (
    get_glob_name,
    get_constr_name,
    get_nuis_name_from_constr_name
)
from quickstats.workspace.elements import (
    Workspace,
    Category,
    Sample,
    Systematic,
    SystematicDomain,
    CountingModel,
    UserDefinedModel,
    HistogramModel,
    ExternalModel,
    CountingData,
    ASCIIData,
    HistogramData,
    NTupleData,
    ArrayData
)
from .ws_base import WSBase
from .xml_ws_reader import XMLWSReader
from .argument_sets import CoreArgSets, SystArgSets

class WSBuilder(WSBase):

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 basedir: Optional[str] = None,
                 apply_fix: bool = False,
                 unlimited_stack:bool=True,
                 minimizer_config:Optional[Dict[str, Any]]=None,
                 verbosity: Optional[Union[int, str]] = "INFO"):
        super().__init__(unlimited_stack=unlimited_stack,
                         verbosity=verbosity)
        self.basedir = basedir
        self.apply_fix = apply_fix
        self.minimizer_config = minimizer_config
        self.read_config(config)

    def read_xml(self, filename: str, apply_fix: bool = False):
        reader = XMLWSReader(apply_fix=apply_fix,
                             verbosity=self.stdout.verbosity)
        config = reader.read_xml_file(filename, basedir=self.basedir)
        self.read_config(config)

    def read_config(self, config:Optional[Dict[str, Any]]=None):
        config = config or {}
        self.config = Workspace.model_validate(config)
        self.compiled_config = None

    def set_basedir(self, basedir:Optional[str]=None):
        if basedir is None:
            basedir = os.getcwd()
        self.basedir = basedir

    def get_compiled_config(self) -> Workspace:
        translated_config = self.config.translate(basedir=self.basedir)
        compiled_config = translated_config.compile(apply_fix=self.apply_fix)
        return compiled_config

    @semistaticmethod
    def set_data_storage_type(self, data_storage_type: Union[str, DataStorageType] = "vector") -> None:
        data_storage_type = DataStorageType(data_storage_type)        
        ROOT = cached_import('ROOT')
        if data_storage_type == DataStorageType.Tree:
            ROOT.RooAbsData.setDefaultStorageType(ROOT.RooAbsData.StorageType.Tree)
        elif data_storage_type == DataStorageType.Vector:
            ROOT.RooAbsData.setDefaultStorageType(ROOT.RooAbsData.StorageType.Vector)
        elif data_storage_type == DataStorageType.Composite:
            ROOT.RooAbsData.setDefaultStorageType(ROOT.RooAbsData.StorageType.Composite)            
        else:
            raise RuntimeError(f'Unknown data storage type: {data_storage_type}')
        self.stdout.info(f'Set data storage type to "{data_storage_type.name}"')
        
    @semistaticmethod
    def set_integrator(self, integrator: Optional[str] = None) -> None:
        if integrator:
            ROOT = cached_import('ROOT')
            self.stdout.warn(f'Set default integrator to "{integrator}".')
            ROOT.RooAbsReal.defaultIntegratorConfig().method1D().setLabel(integrator)    
        
    def _get_category_observable(self, category: Category,
                                 ws: "ROOT.RooWorkspace") -> "ROOT.RooRealVar":
        observable_name = category.observable_name
        observable = ws.var(observable_name)
        if not observable:
            raise RuntimeError(f'Obervable "{observable_name}" not initialized.')
        return observable

    def _build_category_systematics(self, category: Category,
                                    ws: "ROOT.RooWorkspace") -> SystArgSets:
        self.stdout.debug(f'({category.name}) Implementing systematics.')
        systematic_domains = category.systematic_domains
        syst_argsets = SystArgSets()
        for systematic_domain in systematic_domains:
            domain_syst_argsets = self._build_domain_systematics(systematic_domain, ws)
            syst_argsets.merge(domain_syst_argsets)
        return syst_argsets

    def _build_domain_systematics(self, systematic_domain: SystematicDomain,
                                  ws: "ROOT.RooWorkspace") -> SystArgSets:
        ROOT = cached_import('ROOT')
        nuis_list = ROOT.RooArgList()
        uncert_hi_list = ROOT.RooArgList()
        uncert_lo_list = ROOT.RooArgList()
        nominal_list = []
        interp_code_list = []
        for systematic in systematic_domain.systematics:
            nuis_name = self.import_expression(ws, systematic.nuis_expr)
            uncert_hi_name = self.import_expression(ws, systematic.uncert_hi_expr)
            uncert_lo_name = self.import_expression(ws, systematic.uncert_lo_expr)
            nuis_list.add(ws.var(nuis_name))
            uncert_hi_list.add(ws.obj(uncert_hi_name))
            uncert_lo_list.add(ws.obj(uncert_lo_name))
            nominal_list.append(systematic.central_value)
            interp_code_list.append(systematic.interp_code)
        # build response function
        if not getattr(ROOT, "ResponseFunction"):
            raise RuntimeError('ResponseFunction class undefined: may be you need to load the '
                               'corresponding macro...')
        nominal_list = list2vec(nominal_list)
        interp_code_list = list2vec(interp_code_list)
        resp_name = systematic_domain.response_name
        self.stdout.debug(f'Creating response function "{resp_name}".')
        resp_func = ROOT.ResponseFunction(resp_name, resp_name, nuis_list, nominal_list,
                                          uncert_lo_list, uncert_hi_list, interp_code_list)
        ws.Import(resp_func, ROOT.RooFit.RecycleConflictNodes())
        syst_argsets = SystArgSets()
        for systematic in systematic_domain.systematics:
            constr_expr = systematic.constr_expr
            if self.debug_mode:
                constr_type = systematic.constr_type
                if constr_type == ConstraintType.DFD:
                     self.stdout.debug(f'Creating DFD constraint term for NP "{systematic.name}".')
                else:
                     self.stdout.debug(f'Creating Gaussian constraint term for NP "{systematic.name}".')
            self.import_expression(ws, constr_expr, True)
            self.stdout.debug(f'Finished implementing the systematic "{systematic.name}".')
            nuis_var = ws.var(systematic.name)
            glob_var = ws.var(systematic.glob_name)
            constr_var = ws.function(systematic.constr_name)
            syst_argsets.add(constr=constr_var, nuis=nuis_var, glob=glob_var)
        return syst_argsets

    def _build_category_samples(self, category: Category, ws: "ROOT.RooWorkspace") -> SystArgSets:
        syst_argsets = SystArgSets()
        for sample in category.samples:
            self.stdout.debug(f'({category.name}) Implementing sample "{sample.name}".')
            self._build_sample_shape_factors(sample, ws)
            self._build_sample_norm_factors(sample, ws)
            sample_syst_argsets = self._build_sample_model(sample, ws)
            syst_argsets.merge(sample_syst_argsets)
        return syst_argsets

    def _build_sample_shape_factors(self, sample: Sample, ws: "ROOT.RooWorkspace") -> None:
        self.stdout.debug(f'Implementing shape factors for the sample "{sample.name}".')
        self.import_expressions(ws, sample.resolved_shape_factors)

    def _build_sample_norm_factors(self, sample: Sample, ws: "ROOT.RooWorkspace") -> None:
        self.stdout.debug(f'Implementing norm factors for the sample "{sample.name}".')
        norm_factor_names = self.import_expressions(ws, sample.resolved_norm_factors)
        category = sample.get_category()
        resp_func_map = category.response_function_map
        for syst_domain in sample.syst_domains:
            if syst_domain in resp_func_map:
                norm_factor_names.append(resp_func_map[syst_domain])
            # sample without systematics 
            elif syst_domain == sample.name:
                continue
            # no common systematics but included :common: in ImportSyst
            elif syst_domain == COMMON_SYST_DOMAIN_NAME:
                continue
            else:
                raise RuntimeError(f"Unknown systematic domain {syst_domain} in sample {sample.name}.")
        norm_factor_expr = sample.get_norm_factor_expr(norm_factor_names)
        self.import_expression(ws, norm_factor_expr)
        
        sample_yield = ws.function(sample.norm_name).getVal()
        self.stdout.info(f'Yield for category "{category.name}" sample "{sample.name}": {sample_yield}')

    def _build_sample_model(self, sample: Sample, ws: "ROOT.RooWorkspace") -> SystArgSets:
        model_name = sample.model_name
        self.stdout.debug(f'Implementing model "{model_name}" for the sample "{sample.name}".')
        # check if model has been implemented
        if ws.pdf(model_name):
            if sample.shared_pdf:
                # use shared pdf
                self.stdout.debug(f"PDF {model_name} has been created in the workpace.")
                return None
            else:
                raise RuntimeError(f"PDF {model_name} already exists but the user asks to create it again.")
        syst_argsets = SystArgSets()
        model = sample.model
        if model.type == COUNTING_MODEL:
            self._build_counting_model(model, ws)
        elif model.type == USERDEF_MODEL:
            self._build_userdef_model(model, ws)
        elif model.type == HISTOGRAM_MODEL:
            self._build_histogram_model(model, ws)
        elif model.type == EXTERNAL_MODEL:
            ext_syst_argsets = self._build_external_model(model, ws)
            syst_argsets.merge(ext_syst_argsets)
        else:
            raise RuntimeError(f'Failed to build sample model. Unknown model type: {model.type}')
        return syst_argsets

    def _build_counting_model(self, model: CountingModel,
                              ws: "ROOT.RooWorkspace") -> None:
        if not isinstance(model, CountingModel):
            raise ValueError(f'Not a counting model specification: \n{model}')
        self.import_expression(ws, model.pdf_expr)

    def _build_userdef_model(self, model: UserDefinedModel,
                             ws: "ROOT.RooWorkspace") -> None:
        if not isinstance(model, UserDefinedModel):
            raise ValueError(f'Not a user-defined model specification: \n{model}')
        observable_name = model.observable_name
        observable = ws.var(observable_name)
        if model.cache_binning > 0:
            if not observable:
                raise RuntimeError(f'Failed to set cache binning. Observable "{observable_name}" not initialized.')
            # for the accuracy of Fourier transformation
            observable.setBins(model.cache_binning, "cache")
        for expr in model.items:
            self.import_expression(ws, expr)
        self.import_expression(ws, model.pdf_expr)

    def _build_histogram_model(self, model: HistogramModel,
                               ws: "ROOT.RooWorkspace") -> None:
        if not isinstance(model, HistogramModel):
            raise ValueError(f'Not a histogram model specification: \n{model}')
        model_name = model.model_name
        observable_name = model.observable_name
        filename = model.filename
        if not os.path.exists(model.filename):
            raise FileNotFoundError(f'Input file "{filename}" for the model "{model_name}" not found.')
        ROOT = cached_import('ROOT')
        f = ROOT.TFile(filepath)
        histogram = f.Get(histname)
        if not isinstance(histogram, (ROOT.TH1, ROOT.TH2, ROOT.TH3)):
            raise RuntimeError(f'No histogram named "{histanme}" found in the input file "{filename}".')
        if model.rebin > 0:
            histogram.Rebin(model.rebin)
        observable = ws.var(observable_name)
        if not observable:
            raise RuntimeError(f'Obervable "{observable_name}" not initialized.')
        hist_data = ROOT.RooDataHist("hdata", "hdata", observable, histogram)
        hist_pdf = ROOT.RooHistPdf(model_name, model_name, observable, hist_data)
        self.import_object(ws, hist_pdf)
    
    def _build_external_model(self, model: ExternalModel,
                               ws: "ROOT.RooWorkspace") -> SystArgSets:
        if not isinstance(model, ExternalModel):
            raise ValueError(f'Not an external model specification: \n{model}')
        filename = model.filename
        workspace_name = model.workspace_name
        model_name = model.model_name
        obseravble_name = model.observable_name
        ext_model_name = model.ext_model_name
        ext_observable_name = model.ext_observable_name
        self.stdout.debug(f'Use existing PDF "{ext_model_name}" from the workspace "{filename}".')

        ROOT = cached_import('ROOT')
        from quickstats.components import ExtendedModel
        from quickstats.components.basics import WSArgument
        helper = ExtendedModel(filename, ws_name=workspace_name, data_name=None,
                               verbosity='warning')
        ws_ext = helper.workspace
        pdf_ext = ws_ext.function(ext_model_name)

        nuis_list, glob_list, constr_list = [], [], []
        name_maps = {}
        do_not_touch = [observable_name]

        paired_constraints = None
        for action in model.actions:
            if action.type == EXT_MODEL_ACTION_ITEM:
                self.import_object(ws, action.name)
            elif action.type == EXT_MODEL_ACTION_FIX:
                var_name = action.name
                var_value = action.value
                var = ws_ext.var(var_name)
                if not var:
                    raise RuntimeError(f'No variable named "{var_name}" found in the workspace "{filepath}".')
                var.setConstant(1)
                if var_value is not None:
                    var.setVal(var_value)
                self.stdout.debug(f'Fixed variable "{var.GetName()}" at "{var.getVal()}".')
            elif action.type == EXT_MODEL_ACTION_RENAME:
                # rename the object names in the input workspace
                do_not_touch.append(action.old_name)
                name_maps[action.old_name] = action.new_name
            elif action.type == EXT_MODEL_ACTION_EXTSYST:
                # adding external systematics
                nuis_name = action.nuis_name
                glob_name = action.glob_name
                constr_name = action.constr_name
                if (not glob_name) or (not constr_name):
                    if paired_constraints is None:
                        paired_constraints = helper.pair_constraints(fmt='dict', to_str=True)
                    if action.nuis_name not in paired_constraints['nuis']:
                        raise RuntimeError(f'No NP named "{action.nuis_name}" found in the workspace "{filepath}".')
                    index = paired_constraints['nuis'].index(action.nuis_name)
                    glob_name = paired_constraints['globs'][index]
                    constr_name = paired_constraints['pdf'][index]
                nuis_list.append(nuis_name)
                glob_list.append(glob_name)
                constr_list.append(constr_name)
                do_not_touch.append(nuis_name)
            else:
                raise RuntimeError(f'Unknown external model action "{action.type}".')
        # remove duplicated variables
        do_not_touch = ",".join(remove_list_duplicates(do_not_touch))

        sample = model.get_sample()
        # rename everything in the model by adding a tag to it
        ws_temp = ROOT.RooWorkspace("ws_temp")
        self.import_object(ws, pdf_ext, ROOT.RooFit.RenameAllNodes(sample.tag_name),
                           ROOT.RooFit.RenameAllVariablesExcept(sample.tag_name, do_not_touch))
        #ws_temp.importClassCode()
        if self.debug_mode:
            ws_temp.Print()
            
        pdf = ws_temp.function(f"{ext_model_name}_{sample.tag_name}")
        obs_ext = ws_temp.var(ext_observable_name)
        if not obs_ext:
            raise RuntimeError(f'Observable "{ext_observable_name}" not found in the workspace "{filepath}".')
        if not isinstance(pdf, ROOT.RooAbsPdf):
            self.stdout.warning(f'The object {ext_model_name} is not a p.d.f as seen from RooFit')
            self.stdout.warning('Constructing RooRealSumPdf for the pdf from histFactory')
            dummy_pdf = ROOT.RooUniform(f'{model_name}_dummpy_pdf', 'for RooRealSumPdf construction', obs_ext)
            frac = ROOT.RooRealVar(f'{model_name}_real_pdf_frac', 'for RooRealSumPdf construction', 1)
            pdf = ROOT.RooRealSumPdf(model_name, "from histFactory", ROOT.RooArgList(pdf, dummy_pdf),
                                     ROOT.RooArgList(frac))
        else:
            name_maps[pdf.GetName()] = sample.model_name
        
        # rename observable (this step should never happen for a HistFactory workspace)
        if ext_observable_name != observable_name:
            name_maps[ext_observable_name] = observable_name
        self.stdout.info('The following variables will be renamed:')
        old_str = ",".join(name_maps.keys())
        new_str = ",".join(name_maps.values())
        self.stdout.info(f'Old: {old_str}')
        self.stdout.info(f'New: {new_str}')
        
        self.import_object(ws, pdf, ROOT.RooFit.RenameVariable(old_str, new_str),
                           ROOT.RooFit.RecycleConflictNodes())
        syst_argsets = SystArgSets()
        # import constraint terms
        for nuis_name, glob_name, constr_name in zip(nuis_list, glob_list, constr_list):
            new_nuis_name = nuis_name
            # check wheterh NP has been renamed. If yes, update the NP name
            for old_name, new_name in name_maps.items():
                if nuis_name == old_name:
                    new_nuis_name == new_name
                    break
            if (not ws_ext.var(nuis_name)) or (not ws_ext.var(glob_name)) or (not ws_ext.pdf(constr_name)):
                raise RuntimeError(f"Constraint pdf {constr_name} with NP = {nuis_name} and "
                                   f"GlobObs = {glob_name} does not exist.")
            new_constr_name = get_constr_name(new_nuis_name)
            new_glob_name = get_glob_name(new_nuis_name)
            constr_pdf = ws_ext.pdf(constr_name)
            old_str = ",".join([constr_name, glob_name, nuis_name])
            new_str = ",".join([new_constr_name, new_glob_name, new_nuis_name])
            self.import_object(ws, constr_pdf, 
                               ROOT.RooFit.RenameVariable(old_str, new_str))
            self.stdout.debug(f"Import systematics {new_nuis_name} with constraint term {new_constr_name}")
            nuis_var = ws.var(new_nuis_name)
            glob_var = ws.var(new_glob_name)
            constr_var = ws.pdf(new_constr_name)
            nuis_var.setConstant(False)
            syst_argsets.add(constr=constr_var, nuis=nuis_var, glob=glob_var)
        return syst_argsets

    def _build_category_luminosity(self, category: Category,
                                   ws: "ROOT.RooWorkspace") -> Optional["ROOT.RooRealVar"]:
        self.stdout.debug(f'({category.name}) Implementing luminosity.')
        lumi_expr = category.lumi_expr
        if lumi_expr is not None:
            lumi_name = self.import_expression(ws, lumi_expr)
            return ws.var(lumi_name)
        return None

    def _build_category_observable(self, category: Category,
                                   ws: "ROOT.RooWorkspace") -> "ROOT.RooRealVar":
        self.stdout.debug(f'({category.name}) Implementing observable.')
        obs_name = self.import_expression(ws, category.data.observable)
        observable = ws.var(obs_name)
        obs_min, obs_max = observable.getMin(), observable.getMax()
        if obs_min >= obs_max:
            raise RuntimeError(f'Invalid range for the observable "{observable_name}": '
                               f'min = {obs_min}, max = {obs_max}"')

        if category.type == COUNTING_ANALYSIS:
            observable.setBins(1)
        else:
            observable.setBins(category.data.binning)
        return observable

    def _build_category_high_priority_items(self, category: Category,
                                            ws: "ROOT.RooWorkspace") -> None:
        item_priority_map = category.item_priority_map
        self.stdout.debug(f'({category.name}) High priority items:')
        for item in item_priority_map['high_priority']:
            self.stdout.debug(f"  {item}", bare=True)
        self.stdout.debug(f'({category.name}) Implementing high priority items.')
        self.import_expressions(ws, item_priority_map['high_priority'])

    def _build_category_low_priority_items(self, category: Category,
                                           ws: "ROOT.RooWorkspace") -> None:
        item_priority_map = category.item_priority_map
        self.stdout.debug(f'({category.name}) Low priority items:')
        for item in item_priority_map['low_priority']:
            self.stdout.debug(f"  {item}", bare=True)
        self.stdout.debug(f'({category.name}) Implementing low priority items.')
        self.import_expressions(ws, item_priority_map['low_priority'])

    def _build_category_sum_pdf(self, category: Category,
                                ws: "ROOT.RooWorkspace") -> "ROOT.RooAbsPdf":
        self.stdout.debug(f'({category.name}) Implementing category sum pdf.')
        sum_pdf_name = self.import_expression(ws, category.sum_pdf_expr)
        sum_pdf = ws.pdf(sum_pdf_name)
        return sum_pdf
        
    def _build_category(self, category: Category) -> "ROOT.RooWorkspace":
        """
        Generate workspace for a single category.
        
        Parameters
        ----------
        category: Category
            Category specification.
        """
        workspace = category.parent
        title_str = format_delimiter_enclosed_text(f"Category {category.name}", "-")
        self.stdout.info(title_str, bare=True)
        
        ROOT = cached_import("ROOT")
        ws_factory = ROOT.RooWorkspace(f"factory_{category.name}")
        core_argsets = CoreArgSets()

        # implement luminosity
        self._build_category_luminosity(category, ws_factory)
        
        # implement observable
        observable = self._build_category_observable(category, ws_factory)
        core_argsets.obs_set = ROOT.RooArgSet(observable)

        # first implement high priority items: common variables 
        # and functions not involving systematic uncertainties        
        self._build_category_high_priority_items(category, ws_factory)
        
        # secondly implement systematics and import them into the workspace
        syst_argsets = self._build_category_systematics(category, ws_factory)
        core_argsets.add_syst_argsets(syst_argsets)

        # work on remaining common variables and functions to be implemented
        self._build_category_low_priority_items(category, ws_factory)
        
        if self.debug_mode:
            ws_factory.Print()
        
        # implement the scale factors on each sample
        syst_argsets = self._build_category_samples(category, ws_factory)
        core_argsets.add_syst_argsets(syst_argsets)
        
        if self.debug_mode:
            ws_factory.Print()
        
        # generate the combined signal + background pdf
        sum_pdf = self._build_category_sum_pdf(category, ws_factory)

        # create range names for the observable
        range_name = self._create_category_blind_range(category, ws_factory)
        
        self._check_category_nuisance_parameters(category, sum_pdf, core_argsets.nuis_set)
        
        # keep track of correlated variables
        correlated_terms = self._get_category_correlated_terms(category, ws_factory,
                                                               core_argsets.nuis_set)
        correlated_str = ",".join(correlated_terms)
        
        self.stdout.debug(f"The following correlated variables will not be renamed: {correlated_str}")
        # import pdf to new workspace, rename objects as appropriate
        ws = ROOT.RooWorkspace(f"__Cat_{category.name}")
        self.import_object(ws, sum_pdf,
                           ROOT.RooFit.RenameAllNodes(category.name),
                           ROOT.RooFit.RenameAllVariablesExcept(category.name, correlated_str))
        
        # import constraint terms and implement category pdf
        self._attach_category_constraints(category, ws, core_argsets.constr_set)
        
        # define variable sets: observable, POIs, nuisance parameters, global observables
        core_argsets.poi_set = RooWorkspace.create_argset_from_var_names(ws, workspace.pois)
        self._build_category_argsets(category, ws, core_argsets)
        
        if self.debug_mode:
            ws.Print()

        # handle datasets
        dataset = self._build_category_dataset(category, ws)
        self.import_object(ws, dataset)

        if workspace.generate_binned_data:
            binned_dataset = self._build_category_binned_dataset(category, ws, dataset)
            self.import_object(ws, binned_dataset)
        
        if workspace.generate_hist_data:
            datahist = self._build_category_datahist(category, ws, dataset)
            self.import_object(ws, datahist)

        return ws

    def _create_category_blind_range(self, category: Category,
                                     ws: "ROOT.RooWorkapce") -> Optional[str]:
        self.stdout.debug(f'({category.name}) Creating observable ranges.')
        # range_name = "" : fully blinded
        # range_name = None: no blinding
        # otherwise partially blinded
        observable_name = category.observable_name
        observable = ws.var(observable_name)
        if not observable:
            raise RuntimeError(f'Obervable "{observable_name}" not initialized.')
        observable_range = [observable.getMin(), observable.getMax()]
        workspace = category.get_workspace()
        # now handle blinding if needed
        if workspace.blind:
            blind_range = category.data.blind_range
            if blind_range:
                self.stdout.info(f"Implementing blind range [{blind_range[0]}, {blind_range[1]}]")
                sideband_lo_range_name = f"{RANGE_NAME_SB_LO}_{category.name}"
                sideband_hi_range_name = f"{RANGE_NAME_SB_HI}_{category.name}"
                blind_range_name = f"{RANGE_NAME_BLIND}_{category.name}"
                observable.setRange(sideband_lo_range_name, observable_range[0], blind_range[0])
                observable.setRange(blind_range_name, blind_range[0], blind_range[1])
                observable.setRange(sideband_hi_range_name, blind_range[1], observable_range[1])
                if (blind_range[0] == observable_range[0]) and \
                   (blind_range[1] == observable_range[1]):
                    self.stdout.info(f'Category "{category}" is fully blinded. No side-band exists.')
                    range_name = ""
                elif (blind_range[1] == observable_range[1]):
                    range_name = sideband_lo_range_name
                elif (blind_range[0] == observable_range[0]):
                    range_name = sideband_hi_range_name
                else:
                    range_name = f"{sideband_lo_range_name},{sideband_hi_range_name}"
            # do blind but no range specified : fully blinded
            else:
                range_name = ""
        else:
            range_name = None
        return range_name

    def _check_category_nuisance_parameters(self, category: Category, pdf: "ROOT.RooAbsPdf",
                                            nuis_set: "ROOT.RooArgSet") -> None:
        self.stdout.debug(f'({category.name}) Checking validity of nuisance parameters.')
        ROOT = cached_import('ROOT')
        workspace = category.get_workspace()
        observable_name = category.observable_name   
        var_set = pdf.getVariables()
        float_set = ROOT.RooArgSet()
        for var in var_set:
            if (not var.isConstant()):
                if var.getMin() == var.getMax():
                    self.stdout.info(f"Fixing {var.GetName()} to constant as it has the same upper and lower boundary.")
                    var.setConstant(True)
                else:
                    float_set.add(var)
        poi_obs_names = workspace.pois + [observable_name]
        # reove POI and observable from float set
        for name in poi_obs_names:
            float_var = float_set.find(name)
            if float_var:
                float_set.remove(float_var)
        num_nuis = len(nuis_set)
        num_poi = len(workspace.pois)
        for var in float_set:
            if not nuis_set.find(var):
                nuis_set.add(var)
                self.stdout.info(f"Adding {var.GetName()} to the nuisance parameter set")
        num_float = len(float_set)
        if num_float < num_nuis:
            self.stdout.warning(f"There are supposed to be {num_poi + num_nuis} free parameters, "
                                f"but only {num_float} seen in the category {category.name}. "
                                f"This is in principle not an issue, but please make sure you "
                                f"understand what you are doing.")
            if self.debug_mode:
                self.stdout.debug("All free parameters: ")
                float_set.Print()
                self.stdout.debug("All nuisance parameters: ")
                nuis_set.Print()
        else:
            self.stdout.info("Number of nuisance parameters looks good!")

    def _get_category_correlated_terms(self, category: Category,
                                       ws: "ROOT.RooWorkspace",
                                       nuis_set: "ROOT.RooArgSet") -> List[str]:
        self.stdout.debug(f'({category.name}) Accumulating correlated terms.')
        workspace = category.get_workspace()
        correlated_terms = []
        # correlate custom variables
        correlated_terms.extend(category.resolved_correlate_terms)
        # correlate POIs
        correlated_terms.extend(workspace.pois)
        # correlate nuisance parameters
        nuis_names = [nuis.GetName() for nuis in nuis_set]
        correlated_terms.extend(nuis_names)
        # correlate observable
        correlated_terms.append(category.observable_name)
        # remove duplicate terms
        correlated_terms = remove_list_duplicates(correlated_terms)
        # check validity of variables
        valid_correlated_terms = []
        for name in correlated_terms:
            # does not exist
            if (not ws.obj(name)):
                continue
            if (not ws.var(name)):
                raise RuntimeError(f'Correlated variable "{name}" is not properly implemented '
                                   f'as a RooRealVar object in the workspace.')
            valid_correlated_terms.append(name)
        return valid_correlated_terms

    def _attach_category_constraints(self, category: Category,
                                     ws: "ROOT.RooWorkspace",
                                     constr_set: "ROOT.RooArgSet") -> None:
        self.stdout.debug(f'({category.name}) Attaching constraint pdfs to workspace and implement category pdf.')
        ROOT = cached_import('ROOT')
        remove_set = ROOT.RooArgSet()
        sum_pdf = ws.pdf(category.sum_pdf_name)
        if not sum_pdf:
            raise RuntimeError(f'Sum pdf "{category.sum_pdf_name}" for the category "{category.name}" is not defined.')
        for constr in constr_set:
            constr_name = constr.GetName()
            nuis_name = get_nuis_name_from_constr_name(constr_name)
            if not sum_pdf.getVariables().find(nuis_name):
                self.stdout.warning(f'Constraint term "{constr_name}" with NP  {nuis_name} '
                                    f'is redundant in the category {category.name}. '
                                    f'It will be removed...', "red")
                remove_set.add(constr)
            else:
                self.import_object(ws, constr)
        for constr in remove_set:
            constr_set.remove(constr)
        final_pdf_expr = category.get_final_pdf_expr(constr_set)
        self.import_expression(ws, final_pdf_expr)

    def _build_category_argsets(self, category: Category,
                                ws: "ROOT.RooWorkspace",
                                argsets: CoreArgSets) -> None:
        self.stdout.debug(f'({category.name}) Implementing argument sets.')
        argsets.sanity_check()
        for name, argset in argsets.named_map.items():
            ws.defineSet(name, argset)
            self.stdout.debug(f'Defined argument set "{name}" for the workspace "{ws.GetName()}".')

    def _build_category_dataset(self, category: Category,
                                ws: "ROOT.RooWorkspace") -> "ROOT.RooDataSet":
        self.stdout.debug(f'({category.name}) Generating dataset.')
        workspace = category.get_workspace()
        data = category.data
        if data.type == DATA_SOURCE_COUNTING:
            dataset = self._build_counting_dataset(data, ws)
        elif data.type == DATA_SOURCE_ASCII:
            dataset = self._build_ascii_dataset(data, ws)
        elif data.type == DATA_SOURCE_HISTOGRAM:
            dataset = self._build_histogram_dataset(data, ws)
        elif data.type == DATA_SOURCE_NTUPLE:
            dataset = self._build_ntuple_dataset(data, ws)
        elif data.type == DATA_SOURCE_ARRAY:
            dataset = self._build_array_dataset(data, ws)            
        else:
            raise RuntimeError(f'Failed to build dataset. Unknown data type: {data.type}')
        data_scale = data.combined_scale_factor
        if data_scale != 1.:
            dataset = RooDataSet.scale_dataset(dataset, data_scale, ignore_ghost=True)
        if self.debug_mode:
            dataset.Print("v")
        num_events = pretty_value(dataset.sumEntries(), 5)
        self.stdout.info(f"Number of data events: {num_events}")
        return dataset

    def _build_counting_dataset(self, data: CountingData,
                                ws: "ROOT.RooWorkspace") -> "ROOT.RooDataSet":
        if not isinstance(data, CountingData):
            raise ValueError(f'Not a counting data specification: \n{data}')
        category = data.get_category()
        observable = self._get_category_observable(category, ws)
        workspace = category.get_workspace()
        if workspace.blind and data.blind_range:
            blind_condition = data.blind_range
        else:
            blind_condition = None
        dataset = RooDataSet.from_counting(data.num_data,
                                           observable=observable,
                                           apply_ghost=data.inject_ghost,
                                           blind_condition=blind_condition,
                                           name=data.default_dataset_name)
        return dataset
                                           
    def _build_ascii_dataset(self, data: ASCIIData,
                             ws: "ROOT.RooWorkspace") -> "ROOT.RooDataSet":
        if not isinstance(data, ASCIIData):
            raise ValueError(f'Not a ascii data specification: \n{data}')
        category = data.get_category()
        observable = self._get_category_observable(category, ws)
        workspace = category.get_workspace()
        if workspace.blind and data.blind_range:
            blind_condition = data.blind_range
        else:
            blind_condition = None

        dataset = RooDataSet.from_txt(data.filename,
                                      observable=observable,
                                      apply_ghost=data.inject_ghost,
                                      blind_condition=blind_condition,
                                      name=data.default_dataset_name)

        return dataset
        
    def _build_histogram_dataset(self, data: HistogramData,
                                 ws: "ROOT.RooWorkspace") -> "ROOT.RooDataSet":
        if not isinstance(data, HistogramData):
            raise ValueError(f'Not a histogram data specification: \n{data}')
        category = data.get_category()
        observable = self._get_category_observable(category, ws)
        workspace = category.get_workspace()
        if workspace.blind and data.blind_range:
            blind_condition = data.blind_range
        else:
            blind_condition = None
        ROOT = cached_import('ROOT')
        file = ROOT.TFile.Open(data.filename)
        histogram = file.Get(data.histname)
        if not isinstance(histogram, ROOT.TH1):
            raise RuntimeError(f'Histogram data must be an instance of TH1, but got '
                               f'{type(histogram).__name__}')

        dataset = RooDataSet.from_histogram(histogram,
                                            observable=observable,
                                            apply_ghost=data.inject_ghost,
                                            blind_condition=blind_condition,
                                            name=data.default_dataset_name)
        return dataset

    def _build_ntuple_dataset(self, data: NTupleData,
                              ws: "ROOT.RooWorkspace") -> "ROOT.RooDataSet":
        if not isinstance(data, NTupleData):
            raise ValueError(f'Not a ntuple data specification: \n{data}')
        category = data.get_category()
        observable = self._get_category_observable(category, ws)
        workspace = category.get_workspace()
        if workspace.blind and data.blind_range:
            blind_condition = data.blind_range
        else:
            blind_condition = None
        if data.weightname:
            weight_name = RooDataSet.DEFAULT_WEIGHT_NAME
            weight_branchname = data.weightname
        else:
            weight_name = None
            weight_branchname = None
        dataset = RooDataSet.from_ntuples(data.filename,
                                          observable=observable,
                                          treename=data.treename,
                                          observable_branchname=data.varname,
                                          weight_branchname=weight_branchname,
                                          selection=data.selection,
                                          weight_name=weight_name,
                                          apply_ghost=data.inject_ghost,
                                          blind_condition=blind_condition,
                                          name=data.default_dataset_name)
        return dataset

    def _build_array_dataset(self, data: ArrayData,
                             ws: "ROOT.RooWorkspace") -> "ROOT.RooDataSet":
        if not isinstance(data, ArrayData):
            raise ValueError(f'Not an array data specification: \n{data}')
        category = data.get_category()
        observable = self._get_category_observable(category, ws)
        workspace = category.get_workspace()
        if workspace.blind and data.blind_range:
            blind_condition = data.blind_range
        else:
            blind_condition = None
        obs_name = observable.GetName()
        array_data = {}
        array_data[obs_name] = data.x
        array_data['weight'] = data.y or np.ones_like(data.x)
        ROOT = cached_import('ROOT')
        variables = ROOT.RooArgSet(observable)
        dataset = RooDataSet.from_numpy(data=array_data,
                                        variables=variables,
                                        weight_name='weight',
                                        apply_ghost=data.inject_ghost,
                                        blind_condition=blind_condition,
                                        name=data.default_dataset_name)
        return dataset

    def _build_category_binned_dataset(self, category: Category,
                                       ws: "ROOT.RooWorkspace",
                                       dataset: "ROOT.RooDataSet") -> "ROOT.RooDataSet":    
        self.stdout.debug(f'({category.name}) Generating binned dataset.')
        workspace = category.get_workspace()
        observable = self._get_category_observable(category, ws)
        # consider that blinded analysis the number of bins will reduce
        if workspace.blind and category.data.blind_range:
            blind_range = category.data.blind_range
            blind_sf = 1 - (blind_range[1] - blind_range[0]) / (observable.getMax() - observable.getMin())
        else:
            blind_sf = 1
        binned_dataset_name = category.data.default_binned_dataset_name
        if (dataset.numEntries() > (observable.numBins() * blind_sf)):
            binned_dataset = RooDataSet.bin_dataset(dataset,
                                                    name=binned_dataset_name,
                                                    title=binned_dataset_name)
        else:
            binned_dataset = dataset.Clone(binned_dataset_name)
        return binned_dataset

    def _build_category_datahist(self, category: Category,
                                 ws: "ROOT.RooWorkspace",
                                 dataset: "ROOT.RooDataSet") -> "ROOT.RooDataHist":
        self.stdout.debug(f'({category.name}) Generating datahist.')
        hist_dataset_name = category.data.default_datahist_name
        datahist = dataset.binnedClone(hist_dataset_name)
        return datahist

    def _build_workspace_argsets(self, workspace: Workspace,
                                 ws: "ROOT.RooWorkspace",
                                 argsets: CoreArgSets) -> None:
        self.stdout.debug(f'Implementing workspace argument sets.')
        argsets.sanity_check()
        for name, argset in argsets.named_map.items():
            ws.defineSet(name, argset)
            self.stdout.debug(f'Defined argument set "{name}" for the workspace "{ws.GetName()}".')

    def _build_model_config(self, workspace: Workspace,
                            ws: "ROOT.RooWorkspace") -> "ROOT.RooStats.ModelConfig":
        self.stdout.debug(f'Implementing workspace model config.')
        ROOT = cached_import('ROOT')
        mc = ROOT.RooStats.ModelConfig(workspace.modelconfig_name, ws)
        pdf = ws.pdf(workspace.combined_pdf_name)
        if not pdf:
            raise RuntimeError(f'Workspace model pdf "{workspace.combined_pdf_name}" not initialized.')
        mc.SetPdf(pdf)
        argsets = CoreArgSets.from_workspace(ws)
        argsets.set_modelconfig(mc)
        self.import_object(ws, mc, silent=False)
        return mc
        
    def _build_workspace_data(self, workspace: Workspace,
                              ws_map: Dict[str, "ROOT.RooWorkspace"],
                              cat_store: "ROOT.RooCategory",
                              data_type: str = 'dataset') -> "ROOT.RooAbsData":
        self.stdout.debug(f'Building workspace {data_type}.')
        ROOT = cached_import('ROOT')
        data_map = {}
        variables = ROOT.RooArgSet()
        for category in workspace.categories:
            if category.name not in ws_map:
                raise KeyError(f'Missing category key "{category.name}".')
            category_ws = ws_map[category.name]
            if data_type == 'dataset':
                data_name = category.data.default_dataset_name
            elif data_type == 'binned dataset':
                data_name = category.data.default_binned_dataset_name
            elif data_type == 'datahist':
                data_name = category.data.default_datahist_name             
            else:
                raise RuntimeError(f'Unknown data type: {data_type}')
            category_data = category_ws.data(data_name)
            if not category_data:
                raise RuntimeError(f'Data "{data_name}" for the category '
                                   f'"{category.name}" not initialized.')
            data_map[category.name] = category_data
            observable = self._get_category_observable(category, category_ws)
            variables.add(observable)
            
        weight_var = RooDataSet.get_default_weight_var()
        variables.add(weight_var)

        if data_type == 'datahist':
            cdata_map = RooDataSet.get_datahist_map(data_map)
            cls = ROOT.RooDataHist
        else:
            cdata_map = RooDataSet.get_dataset_map(data_map)
            cls = ROOT.RooDataSet

        if data_type == 'dataset':
            data_name = workspace.dataset_name
        elif data_type == 'binned dataset':
            data_name = f'{workspace.dataset_name}binned'
        elif data_type == 'datahist':
            data_name = f'{workspace.dataset_name}hist'
        else:
            raise RuntimeError(f'Unknown data type: {data_type}')
        data = cls(data_name, data_name, variables,
                   ROOT.RooFit.Index(cat_store),
                   ROOT.RooFit.Import(cdata_map),
                   ROOT.RooFit.WeightVar(weight_var))
        return data

    def _generate_asimov(self, workspace: Workspace,
                         ws: "ROOT.RooWorkspace") -> None:
        self.stdout.debug(f'Executing asimov actions.')
        asimov_actions = workspace.asimov_actions
        if not asimov_actions:
            return
        if workspace.binned_fit:
            data_name = workspace.binned_dataset_name
            if not ws.data(data_name):
                data_name = workspace.dataset_name
            else:
                self.stdout.warning("Fitting binned dataset.", "red")
        else:
            data_name = workspace.dataset_name

        from quickstats.components.workspaces import AsimovHandler
        asimov_handler = AsimovHandler(ws,
                                       data_name=data_name,
                                       range_name=workspace.fit_range_name,
                                       minimizer_config=self.minimizer_config,
                                       verbosity=self.stdout.verbosity)
        asimov_handler.title_indent_str = "\t"
        for asimov_action in asimov_actions:
            asimov_handler.generate_single_asimov(asimov_action.dict(),
                                                  translate=False)

    def _import_class_code(self, workspace: Workspace,
                           ws: "ROOT.RooWorkspace") -> None:
        self.stdout.debug(f'Importing class code.')
        decl_dir = workspace.class_decl_import_dir
        impl_dir = workspace.class_impl_import_dir
        if decl_dir and impl_dir:
            self.stdout.info('Importing class code in the following paths: ')
            self.stdout.info(f'\tDeclaration: {decl_dir}', bare=True)
            self.stdout.info(f'\tImplementation: {impl_dir}', bare=True)
            ws.addClassDeclImportDir(decl_dir)
            ws.addClassImplImportDir(impl_dir)
            ws.importClassCode()

    def _get_workspace_summary(self, workspace: Workspace, ws: "ROOT.RooWorkspace") -> None:
        from quickstats.components import ExtendedModel
        model = ExtendedModel(ws, data_name=workspace.dataset_name, 
                              verbosity='warning')
        main_pdf = model.pdf
        index_cat = main_pdf.indexCat()
        n_cat = len(index_cat)
        dataset = model.data
        category_datasets = dataset.split(index_cat, True)
        summary = ""
        summary += "=" * 74 + "\n"
        summary += format_delimiter_enclosed_text("Begin summary", "~") + '\n'
        summary += f'  There are {n_cat} sub channels:\n'
        for i in range(n_cat):
            index_cat.setBin(i)
            category_name = index_cat.getLabel()
            category_pdf = main_pdf.getPdf(category_name)
            category_dataset = category_datasets.FindObject(category_name)
            sum_entries = pretty_value(category_dataset.sumEntries(), 5)
            summary += (f'    Index: {i}, Pdf: {category_pdf.GetName()}, '
                        f'Data: {category_dataset.GetName()}, '
                        f'SumEntries: {sum_entries}\n')
        summary += format_delimiter_enclosed_text("POI", "-") + '\n'
        summary += model._format_variable_summary(model.pois, indent='  ')
        summary += format_delimiter_enclosed_text("Dataset", "-") + '\n'
        for dataset in model.workspace.allData():
            summary += get_default_print_content(dataset)
        summary += format_delimiter_enclosed_text("End Summary", "~") + '\n'
        summary += "=" * 74 + "\n"
        return summary

    def _save_workspace(self, ws: "ROOT.RooWorkspace", filename: str) -> None:
        self.stdout.debug(f'Saving workspace.')
        filename = os.path.abspath(filename)
        extension = os.path.splitext(filename)[-1]
        if extension != '.root':
            self.stdout.warning(f'Output filename does not contain ".root" postfix. Adding it to avoid confusion.')
            filename = os.path.splitext(filename)[0] + '.root'
        dirname = os.path.dirname(filename)
        os.makedirs(dirname, exist_ok=True)
        ws.writeToFile(filename, True)
        self.stdout.info(f'Saved workspace as "{filename}".')

    def _setup_env(self, workspace: Workspace) -> None:
        self.suppress_roofit_message()
        self.set_data_storage_type(workspace.data_storage_type)
        self.set_integrator(workspace.integrator)
        self.load_extension()

    def build(self, saveas: Optional[str] = None):
        
        with timer() as t:
            
            workspace = self.get_compiled_config()
            self._setup_env(workspace)
            
            ROOT = cached_import('ROOT')
            combined_ws = ROOT.RooWorkspace(workspace.workspace_name)
            category_store = ROOT.RooCategory(workspace.category_store_name,
                                              workspace.category_store_name)
            combined_pdf = ROOT.RooSimultaneous(workspace.combined_pdf_name,
                                                workspace.combined_pdf_name,
                                                category_store)
            combined_argsets = CoreArgSets()
            
            category_ws_map = {}
            for category in workspace.categories:
                category_ws = self._build_category(category)
    
                category_store.defineType(category.name)
                
                category_pdf = category_ws.pdf(category.final_pdf_name)
                if not category_pdf:
                    raise RuntimeError(f'Model pdf "{category.final_pdf_name}" for the category '
                                       f'"{category.name}" is not defined')
                combined_pdf.addPdf(category_pdf, category.name)
                category_argsets = CoreArgSets.from_workspace(category_ws)
                combined_argsets.merge(category_argsets)
                
                if self.debug_mode:
                    category_ws.Print()
                    
                category_ws_map[category.name] = category_ws
                
            self.stdout.info("Building combined workspace.")
                    
            # implement main pdf
            self.import_object(combined_ws, combined_pdf)
            
            # implement argument sets and model config
            self._build_workspace_argsets(workspace, combined_ws, combined_argsets)
            self._build_model_config(workspace, combined_ws)

            # implement datasets
            dataset = self._build_workspace_data(workspace,
                                                 category_ws_map,
                                                 category_store,
                                                 data_type='dataset')
            self.import_object(combined_ws, dataset, silent=False)

            if workspace.generate_binned_data:
                binned_dataset = self._build_workspace_data(workspace,
                                                            category_ws_map,
                                                            category_store,
                                                            data_type='binned dataset')

                if binned_dataset.numEntries() < dataset.numEntries():
                    self.import_object(combined_ws, binned_dataset, silent=False)
                else:
                    self.stdout.warning("No need to keep binned dataset, as the "
                                        "number of data events is smaller than or equal "
                                        "to the number of bins in all categories", "red")                  

            if workspace.generate_hist_data:
                datahist = self._build_workspace_data(workspace,
                                                      category_ws_map,
                                                      category_store,
                                                      data_type='datahist')
                self.import_object(combined_ws, datahist, silent=False)
                
            self._generate_asimov(workspace, combined_ws)
            
            self._import_class_code(workspace, combined_ws)

            summary_text = self._get_workspace_summary(workspace, combined_ws)
            self.stdout.info(summary_text, bare=True)

            if saveas:
                self._save_workspace(combined_ws, saveas)

        time_taken = t.interval
        self.stdout.info(f'Workspace built successfully. Total time taken: {time_taken:.3f}s.')
        return combined_ws