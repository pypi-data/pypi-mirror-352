from typing import List, Optional, Union, Dict, Callable, Tuple, Any
from itertools import repeat
import os
import copy
import json
import uuid

import numpy as np

from quickstats import semistaticmethod, timer, cached_import
from quickstats.core import mappings as mp
from quickstats.core.typing import ArrayType
from quickstats.concepts import Binning, RealVariable, RealVariableSet, Range, NamedRanges
from quickstats.components import ROOTObject
from quickstats.components.modelling import PdfFitTool
from quickstats.interface.root import RooDataSet, RooRealVar
from quickstats.utils.py_utils import get_argnames
from quickstats.utils.common_utils import (
    combine_dict,
    in_notebook,
    dict_of_list_to_list_of_dict
)
from quickstats.utils.roofit_utils import dataset_to_histogram, pdf_to_histogram
from .data_source import DataSource
from .model_parameters import (
    ParametersType,
    ModelParameters,
)
from .model_parameters import get as get_model_parameters 

class DataModelling(ROOTObject):
    """
    Class for modeling data distributions with analytic functions.
    
    The DataModelling class provides tools for fitting, evaluating, 
    and visualizing analytic models for data distributions using ROOT's 
    RooFit functionality. It supports various probability density functions,
    parameter estimation, and visualization tools.
    
    Parameters
    ----------
    functional_form : Union[str, Callable]
        The functional form to be used for the modeling. Can be a string
        representing a predefined model or a callable model class.
    fit_range : Union[ArrayType, Dict[str, ArrayType]]
        Range over which the fit is performed. Can be a tuple (min, max) or
        a dictionary of named ranges.
    bin_range : Optional[ArrayType], default=None
        The range for binning. If None and multiple fit ranges are defined,
        this must be provided.
    parameters : Optional[ParametersType], default=None
        Model parameters specification. If None, default parameters for the
        given functional form will be used.
    nbins : Optional[int], default=None
        Number of bins for the observable.
    fit_options : Optional[Dict], default=None
        Dictionary of options for the fitting procedure.
    plot_options : Optional[Dict], default=None
        Dictionary of options for plotting.
    observable_name : str, default='observable'
        Name of the observable variable.
    norm_name : str, default='norm'
        Name for the normalization parameter (used for extended fits).
    weight_name : Optional[str], default='weight'
        Name for the weight variable.
    extended : bool, default=False
        Whether to use an extended likelihood fit.
    verbosity : str, default='INFO'
        Verbosity level for logging.
    
    Attributes
    ----------
    plot_options : Dict[str, Any]
        Options for plotting.
    fit_options : Dict[str, Any]
        Options for fitting.
    functional_form : str
        The functional form being used.
    model_class : Callable
        The model class being used.
    observable : RealVariable
        The observable variable.
    parameters : RealVariableSet
        The set of model parameters.
    norm : Optional[RealVariable]
        The normalization parameter (None if not extended).
    fit_range : NamedRanges
        The named ranges for fitting.
    result : Optional[Any]
        The result of the most recent fit.
    
    Methods
    -------
    configure_model(functional_form, parameters)
        Configure the model to be used.
    configure_observable(name, fit_range, bin_range, nbins)
        Configure the observable variable.
    get_model_class(source)
        Get the model class from a source.
    create_model_pdf(extended=False)
        Create the model PDF.
    create_data_source(data, weights=None)
        Create a data source from various input formats.
    fit(data, weights=None)
        Fit the model to the data.
    sample_parameters(size=1, seed=None, code=None)
        Sample from the parameter distributions.
    get_summary()
        Get a summary of the model and fit results.
    create_observable()
        Create a ROOT RooRealVar for the observable.
    create_observables()
        Create a ROOT RooArgSet of observables.
    create_histogram(bin_range=None, nbins=None)
        Create a histogram of the model.
    create_plot(data, weights=None, saveas=None)
        Create a plot comparing the model to the data.
    """
    
    _DEFAULT_FIT_OPTION_ = {
        'prefit': True,
        'print_level': -1,
        'min_fit': 2,
        'max_fit': 3,
        'minos': False,
        'hesse': True,
        'sumw2': True,
        'asymptotic': False,
        'strategy': 1,
        'range_expand_rate': 1,
        'use_asym_error': False
    }

    _DEFAULT_EVAL_OPTION_ = {
        'bin_range': None,
        'nbins': None
    }
    
    _DEFAULT_PLOT_OPTION_ = {
        'bin_range': None,
        'nbins_data': None,
        'nbins_pdf': 1000,
        'show_comparison': True,
        'show_params': True,
        'show_stats': True,
        'show_fit_error': True,
        'show_bin_error': True,
        'value_fmt': "{:.3g}",
        'stats_list': ["chi2/ndf"],
        'init_options': {
            'label_map': {
                'data' : "MC",
                'pdf'  : "Fit",
                'pdf.masked': "Fit (Masked)"
            }
        },
        'draw_options': {
            'comparison_options':{
                "mode": "difference",
                "ylabel": "MC - Fit",
            }
        },
        'summary_text_option': {
            'x': 0.05,
            'y': 0.9
        },
        'extra_text_option': None,
    }

    # pdf class defined in macros
    _EXTERNAL_PDF_ = ['RooTwoSidedCBShape']

    # name aliases for various pdfs
    _PDF_MAP_ = {
        'RooCrystalBall_DSCB' : 'RooCrystalBall',
        'DSCB'                : 'RooTwoSidedCBShape',
        'RooDSCB'             : 'RooCrystalBall',
        'RooDSCBShape'        : 'RooCrystalBall',
        'ExpGaussExp'         : 'RooExpGaussExpShape',
        'Exp'                 : 'RooExponential',
        'Exponential'         : 'RooExponential',
        'Bukin'               : 'RooBukinPdf',
        'Gaussian'            : 'RooGaussian',
        'Gauss'               : 'RooGaussian',
        'ExpPoly'             : 'RooLegacyExpPoly',
        'Power'               : 'RooPowerSum',
        'PowerSum'            : 'RooPowerSum'
    }
    
    _DEFAULT_ROOT_CONFIG_ = {
        "SetBatch" : True,
        "TH1Sumw2" : True
    }
    
    _REQUIRE_CONFIG_ = {
        "ROOT"  : True,
        "RooFit": True
    }
    
    @property
    def fit_options(self) -> Dict[str, Any]:
        return self._fit_options

    @property
    def eval_options(self) -> Dict[str, Any]:
        return self._eval_options

    @property
    def plot_options(self) -> Dict[str, Any]:
        return self._plot_options
        
    @property
    def functional_form(self) -> str:
        return self._functional_form
    
    @property
    def model_class(self) -> Callable:
        return self._model_class

    @property
    def observable(self) -> RealVariable:
        return self._observable
    
    @property
    def parameters(self) -> RealVariableSet:
        return self._parameters

    @property
    def norm(self) -> Optional[RealVariable]:
        return self._norm

    @property
    def fit_range(self) -> NamedRanges:
        return self.observable.named_ranges

    @property
    def ranged_fit(self) -> bool:
        subranges = self.observable.named_ranges.to_list()
        return (len(subranges) > 1) or (len(subranges) == 0 and
                ((subranges[0][0] != self.observable.range.min) or
                 (subranges[0][1] != self.observable.range.max)))

    def __init__(
        self,
        functional_form: Union[str, Callable],
        fit_range: Union[ArrayType, Dict[str, ArrayType]],
        bin_range: Optional[ArrayType]=None,
        parameters: Optional[ParametersType]=None,
        nbins: Optional[int]=None,
        fit_options: Optional[Dict]=None,
        eval_options: Optional[Dict]=None,
        plot_options: Optional[Dict]=None,
        observable_name: str = 'observable',
        norm_name: str = 'norm',
        weight_name: Optional[str]='weight',        
        extended: bool=False,
        verbosity: str='INFO'
    ):
        """
        Modelling of a data distribution by a simple analytic function.
        
        Parameters:
            observable: str
                Name of observable.
        """
        self._fit_options  = mp.concat((self._DEFAULT_FIT_OPTION_, fit_options), copy=True)
        self._plot_options = mp.concat((self._DEFAULT_PLOT_OPTION_, plot_options), copy=True)
        self._eval_options = mp.concat((self._DEFAULT_EVAL_OPTION_, eval_options), copy=True)
        roofit_config = {
            "MinimizerPrintLevel": self.fit_options.get("print_level", -1)
        }
        super().__init__(
            roofit_config=roofit_config,
            verbosity=verbosity
        )
        self.extended = extended
        self.norm_name = norm_name
        self.weight_name = weight_name
        self.result = None
        self.configure_model(functional_form, parameters)
        self.configure_observable(
            name=observable_name,
            bin_range=bin_range,
            fit_range=fit_range,
            nbins=nbins
        )

    def configure_model(
        self,
        functional_form: Union[str, Callable],
        parameters: Optional[ParametersType] = None
    ) -> None:
        self._model_class = self.get_model_class(functional_form)
        if not isinstance(functional_form, str):
            functional_form = type(functional_form).__name__
        self._functional_form = functional_form
        self._parameters = get_model_parameters(parameters or functional_form)
        if self.extended:
            self._norm = RealVariable(name=self.norm_name, value=1)
        else:
            self._norm = None

    def configure_observable(
        self,
        name: str = 'observable',
        fit_range: Optional[Union[ArrayType, Dict[str, ArrayType]]] = None,
        bin_range: Optional[ArrayType] = None,
        nbins: Optional[int] = None
    ):
        if fit_range is None:
            fit_range = (-np.infty, np.infty)
        if not isinstance(fit_range, dict):
            fit_range = {
                'fitRange': fit_range
            }
        if bin_range is None:
            if len(fit_range) > 1:
                raise ValueError('`bin_range` must be given if multiple fit ranges are defined')
            bin_range = next(iter(fit_range.values()))
        observable = RealVariable(
            name=name,
            range=bin_range,
            named_ranges=fit_range,
            nbins=nbins
        )
        self._observable = observable
        
    @semistaticmethod
    def get_model_class(self, source:Union[str, Callable]):
        """
        Resolves the pdf class that describes the data model.

        Parameters
        ----------
            source : string or callable
                Name of the pdf or a callable representing the pdf class.
        """
        if isinstance(source, Callable):
            return source
        ROOT = cached_import("ROOT")
        pdf_name = self._PDF_MAP_.get(source, source)
        if hasattr(ROOT, pdf_name):
            return getattr(ROOT, pdf_name)

        if pdf_name in self._EXTERNAL_PDF_:
            # load definition of external pdfs
            self.load_extension(pdf_name)
            return self.get_model_class(pdf_name)
        
        raise ValueError(f'Failed to load model pdf: "{source}"')

    def create_model_pdf(self, extended: bool = False) -> "ROOT.RooAbsPdf":
        return self._create_model_pdf(extended=extended)[0]

    def _create_model_pdf(self, extended: bool = False) -> Tuple["ROOT.RooAbsPdf", "ROOT.RooArgSet"]:
        model_name = f"model_{self.model_class.Class_Name()}"
        observable = RooRealVar(self.observable).to_root()
        ROOT = cached_import("ROOT")
        model_args = self.parameters.get_model_args()
        base_pdf = self.model_class(model_name, model_name, observable, *model_args)
        if not extended:
            return base_pdf, observable, *model_args
        norm_var = RooRealVar(self.norm).to_root()
        ROOT.SetOwnership(norm_var, False)
        ROOT.SetOwnership(base_pdf, False)
        sum_pdf = ROOT.RooAddPdf(
            f'{model_name}_extended',
            f'{model_name}_extended',
            ROOT.RooArgList(base_pdf),
            ROOT.RooArgList(norm_var)
        )
        return sum_pdf, observable, *model_args, norm_var

    def create_data_source(
        self,
        data: Union[np.ndarray, "ROOT.RooDataSet", "ROOT.TTree", "DataSource"],
        weights: Optional[np.ndarray]=None
    ) -> DataSource:
        ROOT = cached_import("ROOT")
 
        if isinstance(data, DataSource):
            return data
        kwargs = {
            'observable': self.observable,
            'weight_name': self.weight_name,
            'verbosity': self.stdout.verbosity
        }
        if isinstance(data, np.ndarray):
            from quickstats.components.modelling import ArrayDataSource
            return ArrayDataSource(data, weights=weights, **kwargs)
        elif isinstance(data, ROOT.RooDataSet):
            from quickstats.components.modelling import RooDataSetDataSource
            return RooDataSetDataSource(data, **kwargs)
        elif isinstance(data, ROOT.TTree):
            from quickstats.components.modelling import TreeDataSource
            return TreeDataSource(data, **kwargs)
        else:
            raise ValueError(f'Unsupported data type: "{type(data).__name__}"')
        
    def fit(
        self,
        data: Union[np.ndarray, "ROOT.RooDataSet", "ROOT.TTree", DataSource],
        weights: Optional[np.ndarray]=None,
        reset_parameters: bool = False,
        data_error: str = 'poisson',
    ):
        with timer() as t:
            data_source = self.create_data_source(data, weights=weights)
            dataset = data_source.as_dataset()
            if dataset.numEntries() == 0:
                raise RuntimeError('No events found in the dataset. Please make sure you have specified the '
                                   'correct fit range and that the input data is not empty.')
            fit_options = combine_dict(self.fit_options)
            do_prefit = fit_options.pop('prefit', True)

            if reset_parameters:
                self.parameters.reset()
            if do_prefit:
                self.parameters.prefit(data_source)
            model_pdf = self.create_model_pdf(extended=self.extended)
            fit_tool = PdfFitTool(model_pdf, dataset, verbosity=self.stdout.verbosity)
            fit_kwargs = {}
            for key in get_argnames(fit_tool.mle_fit):
                if key in fit_options:
                    fit_kwargs[key] = fit_options[key]
            fit_kwargs['fit_range'] = ','.join(self.fit_range.names)
            fit_kwargs['eval_bin_range'] = self.eval_options.get('bin_range', None)
            fit_kwargs['eval_nbins'] = self.eval_options.get('nbins', None)
            fit_kwargs['use_asym_error'] = self.fit_options.get('use_asym_error', True)
            fit_kwargs['data_error'] = data_error
            fit_result = fit_tool.mle_fit(**fit_kwargs)
        if fit_result is not None:
            self.parameters.copy_data(fit_result.parameters)
        self.result = fit_result
        self.stdout.info(f"Task finished. Total time taken: {t.interval:.3f}s")
        return fit_result

    def sample_parameters(
        self,
        size: int = 1,
        seed: Optional[int] = None,
        code: Optional[int] = None,
    ) -> Dict[str, np.ndarray]:
        if not self.result:
            raise RuntimeError('No fit result available. Did you perform a fit?')
        return self.result.randomize_parameters(size=size, seed=seed, code=code, fmt='dict')

    def get_summary(self):
        summary = {
            'configuration': {
                'functional_form': self.functional_form,
                'parameters': self.parameters.data,
                'observable': self.observable.data,
                'fit_options': mp.concat((self.fit_options,), copy=True)
            },
            'fit_result': None if self.result is None else self.result.to_dict()
        }
        return summary

    def create_observable(self):
        return RooRealVar(self.observable).to_root()

    def create_observables(self):
        ROOT = cached_import("ROOT")
        return ROOT.RooArgSet(self.create_observable())

    def create_histogram(
        self,
        bin_range: Optional[ArrayType]=None,
        nbins: Optional[int] = None
    ):
        pdf = self.create_model_pdf()
        nbins = nbins or self.observable.nbins
        if not nbins:
            raise ValueError(f'`nbins` must be given when observable binning is not specified')
        bin_range = Range.create(bin_range) if bin_range else self.observable.range
        if not bin_range.is_finite():
            raise ValueError(f'`bin_range` cannot be infinite')
        observables = self.create_observables()
        histogram = pdf_to_histogram(
            pdf,
            observables,
            nbins=nbins,
            bin_range=bin_range
        )
        return histogram
        
    def create_plot(
        self,
        data: Union[np.ndarray, "ROOT.RooDataSet", "ROOT.TTree", DataSource],
        weights: Optional[np.ndarray] = None,
        saveas: Optional[str] = None,
    ):
        if not self.result:
            raise RuntimeError('No fit result available. Did you perform a fit?')
        from quickstats.plots import DataModelingPlot
        ROOT = cached_import("ROOT")
        data_source = self.create_data_source(data, weights=weights)
        dataset = data_source.as_dataset()
        pdf = self.create_model_pdf()
        plot_options = mp.concat((self.plot_options,), copy=True)
        if plot_options.get('nbins_data') is None:
            if self.observable.nbins is None:
                raise RuntimeError('`nbins_data` not set in plot options')
            plot_options['nbins_data'] = self.observable.nbins
        if plot_options.get('bin_range') is None:
            obs_range = self.observable.range
            if not obs_range.is_finite():
                raise RuntimeError('`bin_range` not set in plot options')
            plot_options['bin_range'] = (obs_range.min, obs_range.max)
        data_hist = dataset_to_histogram(
            dataset,
            nbins=plot_options['nbins_data'],
            bin_range=plot_options['bin_range'],
            evaluate_error=plot_options['show_bin_error'],
        )
        observables = self.create_observables()
        pdf_hist = self.create_histogram(
            nbins=plot_options['nbins_pdf'],
            bin_range=plot_options['bin_range']
        )
        pdf_hist_data_binning = self.create_histogram(
            nbins=plot_options['nbins_data'],
            bin_range=plot_options['bin_range'],
        )
        subranges = self.observable.named_ranges.to_list()
        pdf_hist.reweight(data_hist, subranges=subranges, inplace=True)
        pdf_hist_data_binning.reweight(data_hist, subranges=subranges, inplace=True)
        if self.ranged_fit:
            def blind_condition(x, y):
                mask = np.full(x.shape, True)
                for subrange in subranges:
                    mask &= ~((x > subrange[0]) & (x < subrange[1]))
                return mask
            data_hist.mask(blind_condition)
            pdf_hist.mask(blind_condition)
            pdf_hist_data_binning.mask(blind_condition)
        data_map = {
            'data': data_hist,
            'pdf': pdf_hist,
            'pdf_data_binning': pdf_hist_data_binning
            
        }
        plotter = DataModelingPlot(
            data_map=data_map,
            analytic_model=True,
            **plot_options['init_options']
        )

        summary_kwargs = {
            "value_fmt" : plot_options["value_fmt"],
            "show_params" : plot_options['show_params'],
            "show_stats" : plot_options["show_stats"],
            "show_fit_error" : plot_options["show_fit_error"],
            "stats_list" : plot_options["stats_list"],
            "show_header": False
        }
        summary_text = self.result.get_summary_text(**summary_kwargs)
        if summary_text:
            options = plot_options.get('summary_text_option', {})
            plotter.add_text(summary_text, **options)
        
        extra_text_option = plot_options.get("extra_text_option", None)
        if extra_text_option is not None:
            if isinstance(extra_text_option, dict):
                plotter.add_text(**extra_text_option)
            elif isinstance(extra_text_option, list):
                for options in extra_text_option:
                    plotter.add_text(**options)
            else:
                raise ValueError('invalid format for the plot option "extra_text_option"')
                
        draw_options = mp.concat((plot_options.get('draw_options'),), copy=True)
        draw_options.setdefault('xlabel', self.observable.name)
        draw_options['primary_target'] = 'data'
        if plot_options['show_comparison']:
            comparison_options = mp.concat((draw_options.get('comparison_options'),), copy=True)
            comparison_options['components'] = [
                {
                    "reference": "pdf_data_binning",
                    "target": "data",
                }
            ]
        else:
            comparison_options = None
        draw_options['comparison_options'] = comparison_options

        axes = plotter.draw(
            data_targets=['data'],
            model_targets=['pdf'],
            **draw_options
        )
        if saveas is not None:
            plotter.figure.savefig(saveas, bbox_inches="tight")
        if in_notebook():
            import matplotlib.pyplot as plt
            plt.show()
        return axes