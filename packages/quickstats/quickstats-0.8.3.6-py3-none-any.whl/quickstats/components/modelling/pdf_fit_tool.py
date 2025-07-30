from typing import List, Optional, Dict, Any, Union

from quickstats import AbstractObject, semistaticmethod, cached_import, timer, DescriptiveEnum
from quickstats.core.typing import ArrayLike
from quickstats.utils.string_utils import split_str, unique_string
from quickstats.interface.root import RooFitResult

class DataErrorType(DescriptiveEnum):
    POISSON = (0, 'Poisson error')
    SUMW2 = (1, 'SumW2 error')
    NONE = (2, 'No error')
    AUTO = (4, 'Error determined automatically')

class PdfFitTool(AbstractObject):
    
    def __init__(self, pdf:"ROOT.RooAbsPdf", data:"ROOT.RooAbsData",
                 verbosity:str="INFO"):
        super().__init__(verbosity=verbosity)
        self.pdf = pdf
        self.data = data
        self.result = None
        
    @staticmethod
    def is_fit_success(fit_result:"ROOT.RooFitResult") -> bool:
        status   = fit_result.status()
        cov_qual = fit_result.covQual()
        return (status == 0) and (cov_qual in [-1, 3])
    
    @staticmethod
    def _set_pdf_param_values(pdf:"ROOT.RooAbsPdf", observable:"ROOT.RooRealVar", param_values:Dict) -> None:
        params = pdf.getParameters(observable)
        for param in params:
            param_name = param.GetName()
            if param_name not in param_values:
                raise RuntimeError(f"missing value for the parameter: {param_name}")
            param_value = param_values[param_name]
            param.setVal(param_value)
            
    @semistaticmethod
    def _get_fit_stats(
        self,
        model:"ROOT.RooAbsPdf",
        data:"ROOT.RooAbsData",
        bin_range:Optional[Union[ArrayLike, str]]=None,
        fit_range:Optional[str]=None,
        nbins:Optional[int]=None,
        n_float_params:int=0,
        data_error:str='poisson'
    ) -> Dict[str, Any]:
        ROOT = cached_import("ROOT")
        observable = self.get_observable(data)
        if nbins is None:
            nbins = observable.numBins()
        if bin_range is None:
            range_name = ''
            bin_low, bin_high = observable.getMin(), observable.getMax()
        elif isinstance(bin_range, str):
            range_name = bin_range
            if not observable.hasRange(range_name):
                raise RuntimeError(
                    f'Observable "{observable.GetName()}" does not have a range named "{range_name}"'
                )
            obs_bin_range = observable.getRange(bin_range)
            bin_low, bin_high = obs_bin_range.first, obs_bin_range.second
        else:
            bin_low, bin_high = bin_range
            range_name = unique_string()
            observable.setRange(range_name, bin_low, bin_high)
        # +1 is there to account for the normalization that is done internally in RootFit
        ndf = nbins - (n_float_params + 1)
        frame = observable.frame(bin_low, bin_high, nbins)
        data_args = []
        model_args = [ROOT.RooFit.Range(range_name)]
        if fit_range is not None:
            data_range = fit_range
            data_args.append(ROOT.RooFit.CutRange(fit_range))
            model_args.append(ROOT.RooFit.NormRange(fit_range))
        else:
            data_range = range_name
        data_error = DataErrorType.parse(data_error)
        if data_error == DataErrorType.POISSON:
            data_error_code = ROOT.RooAbsData.ErrorType.Poisson
        elif data_error == DataErrorType.SUMW2:
            data_error_code = ROOT.RooAbsData.ErrorType.SumW2
        elif data_error == DataErrorType.AUTO:
            data_error_code = ROOT.RooAbsData.ErrorType.Auto
        elif data_error == DataErrorType.NONE:
            data_error_code = getattr(ROOT.RooAbsData.ErrorType, 'None')
        else:
            raise ValueError(
                f'Unsupported data error value: {data_error}'
            )
        data_args.append(ROOT.RooFit.DataError(data_error_code))
        n_data = data.sumEntries('', data_range)
        model_args.append(ROOT.RooFit.Normalization(n_data, ROOT.RooAbsReal.NumEvent))
        data.plotOn(frame, *data_args)
        model.plotOn(frame, *model_args)
        curve = frame.findObject('', ROOT.RooCurve.Class())
        hist = frame.findObject('', ROOT.RooHist.Class())
        chi2_reduced = frame.chiSquare(n_float_params)
        chi2 = chi2_reduced * ndf
        pvalue = ROOT.TMath.Prob(chi2, ndf)

        fit_stats = {
            'nbins': nbins,
            'n_float_params': n_float_params,
            'ndf': ndf,
            'chi2/ndf': chi2_reduced,
            'chi2': chi2,
            'pvalue': pvalue
        }
        return fit_stats
    
    def get_fit_stats(
        self,
        bin_range:Optional[Union[ArrayLike, str]]=None,
        fit_range:Optional[str]=None,
        nbins:Optional[int]=None,
        n_float_params:int=0,
        data_error:str='poisson'
    ) -> Dict[str, Any]:
        """
        Parameters
        ----------
        nbins: int, optional
            Number of bins used for chi2 calculation. If not specified, the number of bins of the 
            observable is used.
        n_float_params: int, default = 0
            Number of floating parameters in the fit. This decreases the number of degrees of freedom
            used in chi2 calculation.
        """
        return self._get_fit_stats(
            self.pdf, self.data,
            bin_range=bin_range,
            fit_range=fit_range,
            nbins=nbins,
            n_float_params=n_float_params,
            data_error=data_error
        )
    
    @semistaticmethod
    def print_fit_stats(self, fit_stats: Dict) -> None:
        self.stdout.info(f"chi^2/ndf = {fit_stats['chi2/ndf']}, "
                         f"Number of Floating Parameters + Normalization = {fit_stats['n_float_params'] + 1}, "
                         f"Number of bins = {fit_stats['nbins']}, "
                         f"ndf = {fit_stats['ndf']}, "
                         f"chi^2 = {fit_stats['chi2']}, "
                         f"p_value = {fit_stats['pvalue']}")
    
    @staticmethod
    def get_observable(data: "ROOT.RooAbsData") -> "ROOT.RooRealVar":
        observables = data.get()
        if len(observables) > 1:
            raise RuntimeError("only single-observable fit is allowed")
        observable = observables.first()
        return observable
        
    def mle_fit(
        self,
        minos:bool=False,
        hesse:bool=True,
        sumw2:bool=True,
        asymptotic:bool=False,
        fit_range:Optional[Union[ArrayLike, str]]=None,
        strategy:int=1,
        min_fit:int=2,
        max_fit:int=3,
        range_expand_rate:Optional[int]=None,
        print_level:int=-1,
        use_asym_error: bool = True,
        eval_bin_range:Optional[Union[ArrayLike, str]]=None,
        eval_nbins:Optional[int]=None,
        data_error:str='poisson'
    ):

        ROOT = cached_import("ROOT")
        observable = self.get_observable(self.data)
        tmp_range = (observable.getMin(), observable.getMax())
        if isinstance(fit_range, str):
            range_name = fit_range
        else:
            range_name = 'fitRange'
            if fit_range is not None:
                vmin, vmax = fit_range
            else:
                vmin = observable.getMin()
                vmax = observable.getMax()
            observable.setRange("fitRange", vmin, vmax)
        
        model_name = self.pdf.GetName()
        data_name  = self.data.GetName()
        obs_name   = observable.GetName()
        
        self.stdout.info("Begin model fitting...")
        self.stdout.info("      Model : ".rjust(20) + f"{model_name}", bare=True)
        self.stdout.info("    Dataset : ".rjust(20) + f"{data_name}", bare=True)
        self.stdout.info(" Observable : ".rjust(20) + f"{obs_name}", bare=True)

        fit_args = [ROOT.RooFit.Range(range_name), ROOT.RooFit.PrintLevel(print_level),
                    ROOT.RooFit.Minos(minos), ROOT.RooFit.Hesse(hesse),
                    ROOT.RooFit.Save(), ROOT.RooFit.Strategy(strategy)]
        
        if asymptotic:
            fit_args.append(ROOT.RooFit.AsymptoticError(True))
        elif sumw2:
            fit_args.append(ROOT.RooFit.SumW2Error(True))

        status_label = {
            True  : 'SUCCESS',
            False : 'FAIL'
        }

        fit_results = []
        fit_time = 0.
        for i in range(1, max_fit + 1):
            with timer() as t:
                root_fit_result = self.pdf.fitTo(self.data, *fit_args)
            if not root_fit_result:
                self.result = None
                return None
            fit_result = RooFitResult(root_fit_result, use_asym_error=use_asym_error)
            fit_results.append(fit_result)
            fit_time += t.interval
            is_success = fit_result.is_fit_success()
            self.stdout.info(f" Fit iteration {i} : ".rjust(20) + f"{status_label[is_success]}", bare=True)
            if i >= min_fit:
                if is_success:
                    break
                elif (range_expand_rate is not None) and (range_name == "fitRange"):
                    new_vmin = observable.getRange("fitRange").first - range_expand_rate
                    new_vmax = observable.getRange("fitRange").second + range_expand_rate
                    self.stdout.info(f"Fit failed to converge, refitting with "
                                     f"expanded fit range [{new_vmin}, {new_vmax}]")
                    observable.setRange("fitRange", new_vmin, new_vmax)
        custom_range = f'fit_nll_{self.pdf.GetName()}_{self.data.GetName()}'
        if (range_name == "fitRange"):
            observable.setRange(custom_range, observable.getRange("fitRange").first,
                                observable.getRange("fitRange").second)
        else:
            for name in split_str(fit_range, ','):
                obs_range = observable.getRange(name)
                vmin, vmax = obs_range.first, obs_range.second
                observable.setRange(f'{custom_range}_{name}', vmin, vmax)
        # restore original observable range
        observable.setRange(tmp_range[0], tmp_range[1])
        if not len(fit_results):
            self.result = None
            return None
        final_fit_result = fit_results[-1]
        final_fit_result.set_time(fit_time)
        n_float_params = final_fit_result.parameters.size
        fit_stats = self.get_fit_stats(
            bin_range=eval_bin_range,
            fit_range=range_name,
            nbins=eval_nbins,
            n_float_params=n_float_params,
            data_error=data_error
        )
        self.print_fit_stats(fit_stats)
        final_fit_result.set_stats(fit_stats)
        if len(fit_results) > 1:
            final_fit_result._prefit_parameters = fit_results[0]._prefit_parameters
        self.result = final_fit_result
        return final_fit_result