from typing import Optional, Union, Dict

import numpy as np

from quickstats import cached_import
from quickstats.core.typing import ArrayLike
from quickstats.concepts import Binning, RealVariable
from .data_source import DataSource

class ArrayDataSource(DataSource):
    """
    Array representation of a one-dimensional data input
    """
    
    def __init__(
        self,
        data: np.ndarray,
        weights: Optional[np.ndarray] = None,
        observable: Union[str, RealVariable] = 'observable',
        weight_name: str = 'weight',
        verbosity:Optional[Union[int, str]]="INFO"
    ):
        """
        Parameters
        -----------
        data : np.ndarray
            Input data.
        weights : np.ndarray, optional
            Weights for the input data. Must have the same shape as `data`.
        binning : Binning, optional
            Default binning specification for creating histograms.
        observable_name : str, default = 'observable'
            Name of the observable for creating datasets.
        weight_name : str, default = 'weight'
            Name of the weight for creating datasets.
        verbosity : Union[int, str], optional
            The verbosity level. Default is "INFO".
        """
        self.set_data(data=data, weights=weights)
        super().__init__(observable=observable,
                         weight_name=weight_name,
                         verbosity=verbosity)

    def set_data(self, data: np.ndarray, weights: Optional[np.ndarray]=None) -> None:
        if not isinstance(data, np.ndarray):
            raise TypeError('`data` must be an instance of np.ndarray.')
        data = np.array(data)
        if weights is None:
            weights = np.ones(data.shape)
        else:
            weights = np.array(weights)
        if data.shape != weights.shape:
            raise ValueError('`weights` must have the same shape as `data`.')
        self.data, self.weights = data, weights

    def as_dataset(self, name:Optional[str]=None,
                   title:Optional[str]=None) -> "ROOT.RooDataSet":
        from quickstats.interface.root import RooRealVar, RooDataSet
        ROOT = cached_import('ROOT')
        arrays = self.as_arrays()
        variables = ROOT.RooArgSet()
        observable = RooRealVar(self.observable).to_root()
        variables.add(observable)
        if self.weight_name:
            weight_var = RooRealVar.create(self.weight_name, value=1).to_root()
            variables.add(weight_var)
        name = name or self.default_dataset_name
        title = title or name
        dataset = RooDataSet.from_numpy(arrays, variables,
                                        weight_name=self.weight_name,
                                        name=name, title=title)
        return dataset

    def as_arrays(self) -> Dict[str, np.ndarray]:
        arrays = {
            self.observable_name: self.data,
            self.weight_name: self.weights
        }
        return arrays