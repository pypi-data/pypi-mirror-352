from __future__ import annotations

from typing import Dict, Optional, Union, List, Tuple, Any
import copy

import numpy as np

from quickstats import cached_import
from quickstats.core.registries import get_registry, create_registry_metaclass
from quickstats.concepts import RealVariable, RealVariableSet, Histogram1D
from .data_source import DataSource

ModelParametersRegistry = get_registry('model_parameters')
ModelParametersRegistryMeta = create_registry_metaclass(ModelParametersRegistry)

ParametersType = Union[
    List[RealVariable],
    Tuple[RealVariable, ...],
    RealVariableSet,
    Dict[str, Any]
]

class ModelParameters(RealVariableSet, metaclass=ModelParametersRegistryMeta):
    """
    A base class for model parameters built on RealVariableSet.
    """
    __registry_key__ = "_base"

    DEFAULT_PARAM_DATA : Dict[str, Any] = None
    
    def __init__(
        self,
        components: Optional[ParametersType] = None,
        name: Optional[str] = None,
        verbosity: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize ModelParameters with default components or provided ones.

        Parameters
        ----------
        components : Optional[ParametersType]
            Components for the parameter set. Defaults to those obtained from `get_default`.
        name : Optional[str], optional
            Name of the model parameters. Defaults to the registry key.
        verbosity : Optional[str], optional
            Verbosity level for logging or diagnostics. Defaults to None.
        """
        self._cache_param_data : Dict[str, Any] = None
        name = name or self.__registry_key__
        super().__init__(
            name=name,
            verbosity=verbosity,
            **kwargs
        )
        self.set_parameters(components)

    def get_default_parameters(self) -> RealVariableSet:
        """
        Create a default model parameter set.

        Returns
        -------
        List[RealVariable]
            A RealVariableSet based on `DEFAULT_PARAM_DATA`.
        """
        if self.DEFAULT_PARAM_DATA is None:
            return RealVariableSet()
        components = [RealVariable(name=name, **kwargs) for name, kwargs in self.DEFAULT_PARAM_DATA.items()]
        return RealVariableSet(components=components)

    def set_parameters(
        self,
        components: Optional[ParametersType] = None,
        overwrite_cache: bool = True
    ) -> None:
        self._is_locked = False
        self.clear()
        default_parameters = self.get_default_parameters()
        if components is not None:
            if (len(default_parameters) > 0) and (len(default_parameters) != len(components)):
                raise ValueError(
                    f'Model "{self.name}" expects {len(default_parameters)} parameters, but got {len(components)}'
                )
            if len(default_parameters) == 0:
                aliases_list = [None] * len(components)
            else:
                aliases_list = [[parameter.name] for parameter in default_parameters]
            cloned_components = []
            if isinstance(components, dict):
                for (name, data), aliases in zip(components.items(), aliases_list):
                    if (aliases is not None) and (aliases[0] == name):
                        aliases = None
                    cloned_component = RealVariable(
                        name=name,
                        aliases=aliases,
                        value=data.get('value', None),
                        range=data.get('range', None),
                        description=data.get('description', None),
                        tags=data.get('tags', None)
                    )
                    cloned_components.append(cloned_component)
            elif isinstance(components, (list, tuple, RealVariableSet)):
                for component, aliases in zip(components, aliases_list):
                    if not isinstance(component, RealVariable):
                        raise TypeError(
                            f'Parameter component must be an instance of RealVariable, but got "{type(component)}"'
                        )
                    cloned_component = RealVariable(
                        name=component.name,
                        aliases=aliases,
                        value=component.value,
                        range=component.range,
                        description=component.description,
                        tags=list(component.tags)
                    )
                    cloned_components.append(cloned_component)
            else:
                raise TypeError(
                    f'`components` must be a RealVariableSet, dictionary, an iterable of RealVariable, but got "{type(components)}"'
                )
            parameters = RealVariableSet(components=cloned_components)
        else:
            parameters = default_parameters
        if overwrite_cache:
            self._cache_param_data = parameters.data
        self.append(parameters)
        self._is_locked = True

    def reset(self) -> None:
        if self._cache_param_data is None:
            self.stdout.warning('No cache parameter data available. Skipped.')
            return
        for name, data in self._cache_param_data.items():
            self[name].set_data(**data)

    def prefit(self, data: DataSource) -> None:
        """
        Perform a prefit operation to initialize parameter values from a data source.

        Parameters
        ----------
        data : DataSource
            The data source to use for the prefit operation.
        """
        pass

    def get_model_args(self, tags: Optional[List[str]] = None) -> List[RealVariable]:
        from quickstats.interface.root import RooRealVar
        if tags is None:
            components = self.components.values()
        else:
            components = self.select(tags=tags, to_list=True)
        return [RooRealVar(component).to_root() for component in components]

def extract_histogram_features(hist: Histogram1D) -> Dict[str, float]:
    """
    Extract relevant features from a histogram.

    Parameters
    ----------
    hist : "ROOT.TH1"
        The histogram to analyze.

    Returns
    -------
    Dict[str, float]
        A dictionary containing extracted features such as position of maximum,
        FWHM bounds, and effective sigma.
    """
    hist_max = hist.get_maximum()
    hist_bin_pos_max = hist.get_maximum_bin()
    bin_centers = hist.bin_centers
    hist_pos_max = bin_centers[hist_bin_pos_max]
    hist_pos_FWHM_low = bin_centers[hist.get_first_bin_above(0.5 * hist_max)]
    hist_pos_FWHM_high = bin_centers[hist.get_last_bin_above(0.5 * hist_max)]
    hist_sigma_effective = (hist_pos_FWHM_high - hist_pos_FWHM_low) / 2.355
    return {
        "pos_max": hist_pos_max,
        "FWHM_low": hist_pos_FWHM_low,
        "FWHM_high": hist_pos_FWHM_high,
        "sigma_effective": hist_sigma_effective
    }

class GaussianParameters(ModelParameters):
    __registry_key__ = 'Gaussian'
    __registry_aliases__ = ['Gauss', 'RooGaussian']

    DEFAULT_PARAM_DATA = {
        'mean': {
            'description': 'Mean of distribution'
        },
        'sigma': {
            'description': 'Standard deviation of distribution'
        }
    }
    
    def prefit(self, data_source: DataSource) -> None:
        hist = data_source.as_histogram()
        features = extract_histogram_features(hist)
        
        self['mean'].set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self['sigma'].set_data(
            value=features['sigma_effective'],
            range=(0., 5 * features['sigma_effective'])
        )


class DSCBParameters(ModelParameters):
    
    __registry_key__ = 'DSCB'
    __registry_aliases__ = ['RooTwoSidedCBShape', 'RooDSCB', 'RooDSCBShape']

    DEFAULT_PARAM_DATA = {
        'muCBNom': {
            'description': 'Mean of crystal ball'
        },
        'sigmaCBNom': {
            'description': 'Sigma of crystal ball'
        },
        'alphaCBLo': {
            'description': 'Location of transition to a power law on the left'
        },
        'nCBLo': {
            'description': 'Exponent of power-law tail on the left'
        },
        'alphaCBHi': {
            'description': 'Location of transition to a power law on the right'
        },
        'nCBHi': {
            'description': 'Exponent of power-law tail on the right'
        }
    }

    def prefit(self, data_source: DataSource) -> None:
        hist = data_source.as_histogram()
        features = extract_histogram_features(hist)
        
        self['muCBNom'].set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self['sigmaCBNom'].set_data(
            value=features['sigma_effective'],
            range=(0., 5 * features['sigma_effective'])
        )
        self['alphaCBLo'].set_data(value=1, range=(0., 5.))
        self['nCBLo'].set_data(value=10., range=(0., 200.))
        self['alphaCBHi'].set_data(value=1, range=(0., 5.))
        self['nCBHi'].set_data(value=10., range=(0., 200.))

class CrystalBallParameters(ModelParameters):
    
    __registry_key__ = 'RooCrystalBall'
    __registry_aliases__ = ['RooCrystalBall_DSCB']

    DEFAULT_PARAM_DATA = {
        'muNom': {
            'description': 'Mean of crystal ball'
        },
        'sigmaL': {
            'description': 'Width of the left side of the Gaussian component'
        },
        'sigmaR': {
            'description': 'Width of the right side of the Gaussian component'
        },
        'alphaL': {
            'description': 'Location of transition to a power law on the left'
        },
        'nL': {
            'description': 'Exponent of power-law tail on the left'
        },
        'alphaR': {
            'description': 'Location of transition to a power law on the right'
        },
        'nR': {
            'description': 'Exponent of power-law tail on the right'
        }
    }

    def prefit(self, data_source: DataSource) -> None:
        hist = data_source.as_histogram()
        features = extract_histogram_features(hist)

        self['muNom'].set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self['sigmaL'].set_data(
            value=features['sigma_effective'],
            range=(0., 5 * features['sigma_effective'])
        )
        self['sigmaR'].set_data(
            value=features['sigma_effective'],
            range=(0., 5 * features['sigma_effective'])
        )
        self['alphaL'].set_data(value=1, range=(0., 5.))
        self['nL'].set_data(value=10., range=(0., 200.))
        self['alphaR'].set_data(value=1, range=(0., 5.))
        self['nR'].set_data(value=10., range=(0., 200.))

class BukinParameters(ModelParameters):

    __registry_key__ = 'Bukin'

    __registry_aliases__ = ['RooBukinPdf']

    DEFAULT_PARAM_DATA = {
        'Xp': {
            'description': 'Peak position'
        },
        'sigp': {
            'description': 'Peak width as FWHM divided by 2*sqrt(2*log(2))=2.35'
        },
        'xi': {
            'description': 'Peak asymmetry'
        },
        'rho1': {
            'description': 'Left tail'
        },
        'rho2': {
            'description': 'Right tail'
        }
    }

    def prefit(self, data_source: DataSource) -> None:
        hist = data_source.as_histogram()
        features = extract_histogram_features(hist)

        self['Xp'].set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self['sigp'].set_data(
            value=features['sigma_effective'],
            range=(0.1, 5 * features['sigma_effective'])
        )
        self['xi'].set_data(
            value=0.0,
            range=(-1.0, 1.0)
        )
        self['rho1'].set_data(
            value=-0.1,
            range=(-1.0, 0.0)
        )
        self['rho2'].set_data(
            value=0.,
            range=(0., 1.0)
        )

class ExpGaussExpParameters(ModelParameters):

    __registry_key__ = 'ExpGaussExp'

    __registry_aliases__ = ['RooExpGaussExpShape']

    DEFAULT_PARAM_DATA = {
        'mean': {
            'description': 'Mean of EGE'
        },
        'sigma': {
            'description': 'Sigma of EGE'
        },
        'kLo': {
            'description': 'kLow of EGE'
        },
        'kHi': {
            'description': 'kHigh of EGE'
        }
    }

    def prefit(self, data_source: Optional[DataSource]=None) -> None:
        hist = data_source.as_histogram()
        features = extract_histogram_features(hist)

        self['mean'].set_data(
            value=features['pos_max'],
            range=(features['FWHM_low'], features['FWHM_high'])
        )
        self['sigma'].set_data(
            value=features['sigma_effective'],
            range=(0.1, 5 * features['sigma_effective'])
        )
        self['kLo'].set_data(
            value=2.5,
            range=(0.01, 10.0)
        )
        self['kHi'].set_data(
            value=2.4,
            range=(0.01, 10.0)
        )

def get_exponential_range(
    xmin: float,
    xmax: float,
    ymax: float,
    m: float = 10,
    n: float = 10
) -> Tuple[float, float]:
    k = np.log(ymax * n)
    if xmin >= 0:
        return (-m, k / xmax)
    elif xmax <= 0:
        return (k / xmin, m)
    else:                           
        return (k / xmin, k / xmax)

class ExponentialParameters(ModelParameters):

    __registry_key__ = 'Exponential'

    __registry_aliases__ = ['Exp', 'RooExponential']

    DEFAULT_PARAM_DATA = {
        'c': {
            'description': 'Slope of exponential'
        }
    }

    def prefit(self, data_source: DataSource) -> None:
        hist = data_source.as_histogram()
        xmin, xmax = hist.bin_range
        ymax = hist.get_maximum()
        xrange = get_exponential_range(xmin, xmax, ymax)
        self['c'].set_data(
            value=0,
            range=xrange
        )

class ExpPolyParameters(ModelParameters):

    __registry_key__ = 'ExpPoly'

    __registry_aliases__ = ['RooLegacyExpPoly']

    DEFAULT_PARAM_DATA = None

    @property
    def order(self) -> int:
        return self._order

    def __init__(
        self,
        order: Optional[int] = None,
        coefficients: Optional[ParametersType] = None,
        name: Optional[str] = None,
        verbosity: Optional[str] = None
    ):
        if (order is None) and (coefficients is None):
            raise ValueError(
                'Either `order` or `coefficients` must be specified'
            )
        if (order is not None) and (coefficients is not None):
            raise ValueError(
                'Can not specify both `order` and `coefficients`'
            )
        self._order = order or len(coefficients)
        
        super().__init__(
            components=coefficients,
            name=name,
            verbosity=verbosity
        )

    def get_default_parameters(self) -> RealVariableSet:
        """
        Create a default model parameter set.

        Returns
        -------
        List[RealVariable]
            A RealVariableSet based on `DEFAULT_PARAM_DATA`.
        """
        name_fmt = "c{deg}"
        description_fmt = "Coefficient {deg}"
        components = [
            RealVariable(
                name=name_fmt.format(deg=i+1),
                description=description_fmt.format(deg=i+1)
            ) for i in range(self.order)
        ]
        return RealVariableSet(components=components)

    def prefit(self, data_source: DataSource) -> None:
        hist = data_source.as_histogram()
        xmin, xmax = hist.bin_range
        ymax = hist.get_maximum()
        for i, parameter in enumerate(self.components.values()):
            xmin_i = min(np.power(xmin, i + 1), np.power(xmax, i + 1))
            xmax_i = max(np.power(xmin, i + 1), np.power(xmax, i + 1))
            xrange = get_exponential_range(xmin_i, xmax_i, ymax)
            parameter.set_data(
                value=0,
                range=xrange
            )

    def get_model_args(self) -> Tuple["ROOT.RooAbsArg", ...]:
        ROOT = cached_import('ROOT')
        coefficients = super().get_model_args()
        return (ROOT.RooArgList(*coefficients),)

class PowerParameters(ModelParameters):

    __registry_key__ = 'Power'

    __registry_aliases__ = ['PowerSum', 'RooPower', 'RooPowerSum']

    DEFAULT_PARAM_DATA = None

    def __init__(
        self,
        coefficients: ParametersType,
        exponents: ParametersType,
        name: Optional[str] = None,
        verbosity: Optional[str] = None
    ):
        parameters = self.parse_parameters(
            coefficients=coefficients,
            exponents=exponents
        )
        super().__init__(
            components=parameters,
            name=name,
            verbosity=verbosity
        )

    @property
    def coefficients(self) -> RealVariableSet:
        return RealVariableSet(
            name=f'{self.name}_coefficients',
            components=self.select(tags=['coefficient'], to_list=True)
        )

    @property
    def exponents(self) -> RealVariableSet:
        return RealVariableSet(
            name=f'{self.name}_exponents',
            components=self.select(tags=['exponent'], to_list=True)
        )

    def _clone(
        self,
        components,
        name: Optional[str] = None
    ) -> PowerParameters:
        raise NotImplementedError

    def parse_parameters(
        self,
        coefficients: ParametersType,
        exponents: ParametersType
    ) -> RealVariableSet:
        parameters = []
        for tag, components in [('coefficient', coefficients),
                                ('exponent', exponents)]:
            if isinstance(components, dict):
                for name, data in components.items():
                    tags = set(data.get('tags', []))
                    tags.add(tag)
                    cloned_component = RealVariable(
                        name=name,
                        value=data.get('value', None),
                        range=data.get('range', None),
                        description=data.get('description', None),
                        tags=tags
                    )
                    parameters.append(cloned_component)
            elif isinstance(components, (list, tuple, RealVariableSet)):
                for component, aliases in zip(components, aliases_list):
                    if not isinstance(component, RealVariable):
                        raise TypeError(
                            f'Parameter component must be an instance of RealVariable, but got "{type(component)}"'
                        )
                    tags = set(component.tags)
                    tags.add(tag)
                    cloned_component = RealVariable(
                        name=component.name,
                        value=component.value,
                        range=component.range,
                        description=component.description,
                        tags=tags
                    )
                    parameters.append(cloned_component)
            else:
                raise TypeError(
                    f'`components` must be a RealVariableSet, dictionary, an iterable of RealVariable, but got "{type(components)}"'
                )
        return parameters

    def get_model_args(self) -> Tuple["ROOT.RooAbsArg", ...]:
        ROOT = cached_import('ROOT')
        coefficients = super().get_model_args(['coefficient'])
        exponents = super().get_model_args(['exponent'])
        return (ROOT.RooArgList(*coefficients), ROOT.RooArgList(*exponents))

def get(
    source: Union[str, ModelParameters, ParametersType]
) -> ModelParameters:
    if isinstance(source, ModelParameters):
        return source
    if isinstance(source, str):
        cls = ModelParametersRegistry.get(source)
        if cls is None:
            raise ValueError(
                f'No predefined parameters available for the'
                f'functional form: "{source}"'
            )
        return cls()
    return ModelParameters(source)