from typing import Optional, Union, Dict
from contextlib import contextmanager

import numpy as np

from quickstats import AbstractObject
from quickstats.core.typing import ArrayLike
from quickstats.concepts import Binning, NamedRanges, RealVariable, Histogram1D

class DataSource(AbstractObject):
    """
    Base class for representation of a one-dimensional data input.
    """
    
    def __init__(
        self,
        observable: Union[str, RealVariable] = 'observable',
        weight_name: Optional[str] = None,
        verbosity:Optional[Union[int, str]]="INFO"
    ):
        """
        Parameters
        -----------
        observable : str
            Name of the observable or instance of RealVariable for creating datasets.
        weight : str
            Name of the weight or instance of RealVariable for creating datasets.
        verbosity : Union[int, str], optional
            The verbosity level. Default is "INFO".
        """
        super().__init__(verbosity=verbosity)
        self.observable = observable
        self.weight_name = weight_name

    @property
    def observable(self) -> RealVariable:
        return self._observable

    @observable.setter
    def observable(
        self,
        value: Union[str, RealVariable] = 'observable'
    ) -> None:
        if isinstance(value, RealVariable):
            self._observable = value
        elif isinstance(value, str):
            self._observable = RealVariable(name=value)
        else:
            raise ValueError(f'invalid format for observable: {value}')

    @property
    def observable_name(self) -> str:
        return self.observable.name

    @observable_name.setter
    def observable_name(self, value: str) -> None:
        self.observable.name = value

    @property
    def default_histogram_name(self) -> str:
        return f'hist_{self.observable.name}'

    @property
    def default_dataset_name(self) -> str:
        return f'dataset_{self.observable.name}'

    @property
    def default_binning(self) -> Optional[Binning]:
        return self.observable.binning

    @default_binning.setter
    def default_binning(self, value: Binning) -> None:
        bin_edges = value.bin_edges
        self.observable.domain = (bin_edges[0], bin_edges[1])
        self.observable.nbins = value.nbins

    def validate_arrays(self, data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if self.observable_name not in data:
            raise RuntimeError(
                f'Data arrays missing the observable column: {self.observable_name}'
            )
        if self.weight_name and (self.weight_name not in data):
            raise RuntimeError(
                f'Data arrays missing the weight column: {self.weight_name}'
            )
        return data

    def as_dataset(self, name:Optional[str]=None,
                   title:Optional[str]=None) -> "ROOT.RooDataSet":
        raise NotImplementedError

    def as_histogram(self, name:Optional[str]=None,
                     title:Optional[str]=None,
                     binning: Optional[Binning]=None) -> "ROOT.TH1":
        from quickstats.interface.root import TH1
        from quickstats.utils.root_utils import delete_object
        binning = binning or self.default_binning
        if binning is None:
            raise RuntimeError(
                'No binning information available for creating histogram'
            )
        arrays = self.as_arrays()
        data = arrays[self.observable_name]
        weights = arrays[self.weight_name] if self.weight_name else None
        return Histogram1D.create(
            data,
            weights=weights,
            bins=binning.nbins,
            bin_range=binning.bin_range
        )

    @contextmanager
    def context_histogram(self, name:Optional[str]=None,
                          title:Optional[str]=None,
                          binning: Optional[Binning]=None) -> "ROOT.TH1":
        histogram = self.as_histogram(name=name, title=title, binning=binning)
        try:
            yield histogram
        finally:
            histogram.Delete()
            
    def as_arrays(self) -> Dict[str, np.ndarray]:
        raise NotImplementedError