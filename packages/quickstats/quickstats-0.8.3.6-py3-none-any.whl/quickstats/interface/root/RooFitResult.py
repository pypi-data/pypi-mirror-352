from typing import Optional, Dict, Any, Union, Tuple, List

import numpy as np

from quickstats import AbstractObject, cached_import
from quickstats.concepts import RealVariableSet, RealVariable
from quickstats.maths.numerics import square_matrix_to_dataframe
from quickstats.maths.interpolation import piecewise_interpolate
from quickstats.interface.root import TMatrixSym

def convert_parameters(source: "ROOT.RooArgList", name: str = "parameters", use_asym_error: bool = True) -> RealVariableSet:
    components = []
    for parameter in source:
        param_range = (parameter.getMin(), parameter.getMax())
        if use_asym_error:
            errors = (parameter.getErrorLo(), parameter.getErrorHi())
        else:
            errors = (parameter.getError(), parameter.getError())
        component = RealVariable(
            name=parameter.GetName(),
            value=parameter.getVal(),
            range=param_range,
            errors=errors,
        )
        components.append(component)
    parameters = RealVariableSet(
        name=name,
        components=components,
    )
    return parameters


class RooFitResult(AbstractObject):
    def __init__(
        self,
        source: Union["ROOT.RooFitResult", Dict[str, Any]],
        use_asym_error: bool = True,
        verbosity: Optional[Union[int, str]] = "INFO",
    ):
        super().__init__(verbosity=verbosity)
        self._time = None
        self._stats = None
        self.parse(source, use_asym_error=use_asym_error)

    def parse(self, source: Union["ROOT.RooFitResult", Dict[str, Any]], use_asym_error: bool = True):
        """
        Parse source data into the RooFitResult instance.

        Parameters
        ----------
        source : Union["ROOT.RooFitResult", Dict[str, Any]]
            Source data to parse. Can be a ROOT.RooFitResult object or a dictionary.
        use_asym_error: bool, default = True
            Whether to use asymmetric error for the parameters. Only applicable
            when `source` is an instance of RooFitResult.
        """
        if isinstance(source, dict):
            self._parse_dict(source)
        else:
            ROOT = cached_import("ROOT")
            if isinstance(source, ROOT.RooFitResult):
                self._parse_root(source, use_asym_error=use_asym_error)
            else:
                raise TypeError("`source` must be a dictionary or an instance of ROOT.RooFitResult")

    def _parse_dict(self, source: Dict[str, Any]):
        """
        Parse dictionary data into the RooFitResult instance.

        Parameters
        ----------
        source : Dict[str, Any]
            Dictionary containing the fit result data.
        """
        # Required fields
        try:
            self._status = source["status"]
            self._edm = source["edm"]
            self._min_nll = source["min_nll"]  # Use consistent key naming
            self._cov_qual = source["cov_qual"]
            self._correlation_matrix = np.array(source["correlation_matrix"])
            self._covariance_matrix = np.array(source["covariance_matrix"])
            self._postfit_parameters = RealVariableSet.from_dict(
                source["postfit_parameters"], name="float_final"
            )
            self._prefit_parameters = RealVariableSet.from_dict(
                source["prefit_parameters"], name="float_init"
            )
            self._constant_parameters = RealVariableSet.from_dict(
                source["constant_parameters"], name="constant"
            )
        except KeyError as e:
            raise ValueError(f"Missing required key in dictionary: {e}")

        # Optional fields
        self._time = source.get("time", None)
        self._stats = source.get("stats", None)

    def _parse_root(self, source: "ROOT.RooFitResult", use_asym_error: bool = True):
        """
        Parse ROOT.RooFitResult object into the RooFitResult instance.

        Parameters
        ----------
        source : ROOT.RooFitResult
            The ROOT.RooFitResult object to parse.
        """
        self._status = source.status()
        self._edm = source.edm()
        self._min_nll = source.minNll()
        self._cov_qual = source.covQual()
        self._correlation_matrix = TMatrixSym.to_numpy(source.correlationMatrix())
        self._covariance_matrix = TMatrixSym.to_numpy(source.covarianceMatrix())
        self._postfit_parameters = convert_parameters(source.floatParsFinal(), name="float_final", use_asym_error=use_asym_error)
        self._prefit_parameters = convert_parameters(source.floatParsInit(), name="float_init", use_asym_error=use_asym_error)
        self._constant_parameters = convert_parameters(source.constPars(), name="constant", use_asym_error=use_asym_error)

    @property
    def status(self) -> int:
        """Fit status"""
        return self._status

    @property
    def edm(self) -> float:
        """Estimated distance from minimum"""
        return self._edm

    @property
    def min_nll(self) -> float:
        """Minimum Nll"""
        return self._min_nll

    @property
    def cov_qual(self) -> int:
        """Convergence quality"""
        return self._cov_qual

    @property
    def time(self) -> Optional[float]:
        """Fit time"""
        return self._time

    @property
    def stats(self) -> Optional[Dict[str, Any]]:
        """Fit statistics"""
        return self._stats

    @property
    def correlation_matrix(self) -> np.ndarray:
        return self._correlation_matrix

    @property
    def covariance_matrix(self) -> np.ndarray:
        return self._covariance_matrix

    def cholesky_matrix(self) -> np.ndarray:
        """Computes the Cholesky decomposition of the covariance matrix."""
        return np.linalg.cholesky(self.covariance_matrix)

    @property
    def parameters(self) -> RealVariableSet:
        return self._postfit_parameters

    @property
    def prefit_parameters(self) -> RealVariableSet:
        return self._prefit_parameters

    @property
    def postfit_parameters(self) -> RealVariableSet:
        return self._postfit_parameters

    @property
    def constant_parameters(self) -> RealVariableSet:
        return self._constant_parameters

    def set_time(self, time: float) -> None:
        self._time = time

    def set_stats(self, stats: Dict[str, Any]) -> None:
        self._stats = stats

    def is_fit_success(self) -> bool:
        return (self.status == 0) and (self.cov_qual in [-1, 3])

    def get_correlation_matrix_dataframe(self) -> "pandas.DataFrame":
        return square_matrix_to_dataframe(self._correlation_matrix)

    def get_covariance_matrix_dataframe(self) -> "pandas.DataFrame":
        return square_matrix_to_dataframe(self._covariance_matrix)

    def get_parameter_index(self, name: str, strict: bool = False) -> Optional[int]:
        names = self.parameters.names
        if name not in names:
            if strict:
                raise ValueError(f'Parameter "{name}" is not a floating fit parameter')
            return None
        return names.index(name)

    def correlation(self, param_1: str, param_2: Optional[str] = None) -> float:
        index_1 = self.get_parameter_index(param_1, strict=True)
        index_2 = index_1 if param_2 is None else self.get_parameter_index(param_2, strict=True)
        return self.correlation_matrix[index_1, index_2]

    def covariance(self, param_1: str, param_2: Optional[str] = None) -> float:
        index_1 = self.get_parameter_index(param_1, strict=True)
        index_2 = index_1 if param_2 is None else self.get_parameter_index(param_2, strict=True)
        return self.covariance_matrix[index_1, index_2]

    def randomize_parameters(self, size: int = 1, seed: Optional[int] = None, code:Optional[int] = None, fmt: str = "array"):
        npar = self.parameters.size
        L = self.cholesky_matrix()
        if seed is not None:
            np.random.seed(seed)
        v = np.random.normal(size=(size, npar))
        R = v @ L.T
        if code is not None:
            V = np.zeros_like(R)
            for i, parameter in enumerate(self.parameters):
                nominal = parameter.value
                low = nominal + parameter.errorlo
                high = nominal + parameter.errorhi
                boundary = np.sqrt(self.covariance_matrix[i, i])
                R_transformed = piecewise_interpolate(R[:, i], nominal=nominal, low=low, high=high, boundary=boundary, code=code)
                V[:, i] = nominal + R_transformed
        else:
            V0 = np.array(list(self.parameters.values.values()))
            V = V0 + R
        if fmt == "array":
            return V
        elif fmt == "dict":
            names = self.parameters.names
            return {names[i]: V[:, i] for i in range(npar)}
        else:
            raise ValueError(f'Invalid format: {fmt} (choose between "array" and "dict")')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status,
            'edm': self.edm,
            'cov_qual': self.cov_qual,
            'min_nll': self.min_nll,
            'postfit_parameters': self.postfit_parameters.data,
            'prefit_parameters': self.prefit_parameters.data,
            'constant_parameters': self.constant_parameters.data,
            'correlation_matrix': self.correlation_matrix.tolist(),
            'covariance_matrix': self.covariance_matrix.tolist(),
            'time': self.time,
            'stats': self.stats
        }

    def get_summary_text(
        self,
        value_fmt:str="{:.2g}",
        show_params:bool=True,
        show_stats:bool=True,
        show_fit_error:bool=True,
        show_header:bool=True,
        stats_list:Optional[List[str]]=None
    ) -> str:      
        summary_text = ""
        indent = "    "
        if show_params:
            if show_header:
                summary_text += 'Parameters:\n'
            param_data = self.parameters.data
            for name, data in param_data.items():
                value = value_fmt.format(data["value"])
                if show_fit_error and (data['errors'] is not None):
                    errorlo, errorhi = data['errors']
                    if abs(errorlo) == abs(errorhi):
                        error_str = value_fmt.format(abs(errorhi))
                        summary_text += indent + f"{name} = ${value} \\pm$ {error_str}\n"
                    else:
                        errorlo_str = value_fmt.format(errorlo)
                        errorhi_str = value_fmt.format(errorhi)
                        if (errorhi > 0) and ('+' not in errorhi_str):
                            errorhi_str = f'+{errorhi_str}'
                        if (errorlo > 0) and ('+' not in errorlo_str):
                            errorlo_str = f'+{errorlo_str}'
                        summary_text += indent + f"{name} = ${value}_{{{errorlo_str}}}^{{{errorhi_str}}}$\n"
                else:
                    summary_text += indent + f"{name} = ${value}$\n"
            if not show_header:
                summary_text += '\n'
        if show_stats:
            if show_header:
                summary_text += 'Statistics:\n'
            if stats_list is None:
                stats_list = list(self.stats)
            for key in stats_list:
                if key not in self.stats:
                    raise RuntimeError(f"Invalid stats item: {key}")
                value = value_fmt.format(self.stats[key])
                summary_text += indent + f"{key} = ${value}$\n"
            summary_text += "\n"
        return summary_text