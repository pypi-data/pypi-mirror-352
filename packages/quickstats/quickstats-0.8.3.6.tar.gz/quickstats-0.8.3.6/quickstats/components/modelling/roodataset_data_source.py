from typing import Optional, Union, List, Dict

import numpy as np

from quickstats import cached_import
from quickstats.core.typing import ArrayLike
from quickstats.concepts import Binning, RealVariable
from .data_source import DataSource

class RooDataSetDataSource(DataSource):
    """
    RooDataSet representation of a one-dimensional data input
    """

    def __init__(
        self, dataset: "ROOT.RooDataSet",
        observable: Union[str, RealVariable],
        weight_name: Optional[str] = None,
        verbosity:Optional[Union[int, str]]="INFO"
    ):
        """
        Parameters
        -----------
        dataset : ROOT.RooDataSet
            Input dataset.
        verbosity : Union[int, str], optional
            The verbosity level. Default is "INFO".
        """
        super().__init__(observable=observable, weight_name=weight_name, verbosity=verbosity)
        self.set_data(dataset)

    def set_data(self, dataset: "ROOT.RooDatSet") -> None:
        ROOT = cached_import("ROOT")
        if not isinstance(dataset, ROOT.RooDataSet):
            raise TypeErrror(f'`dataset` must be an instance of ROOT.RooDataSet')
        if dataset.numEntries() == 0:
            raise RuntimeError(f'Dataset "{dataset.GetName()}" is empty')
        observables = dataset.get()
        if len(observables) > 1:
            raise RuntimeError(f'Dataset "{dataset.GetName()}" has more than one observable')
        observable = observables.first()
        observable_name = observable.GetName()
        if observable_name != self.observable_name:
            self.stdout.warning(
                f'There is a mismatch in the observable name'
                f'between the data source ({observable_name})'
                f'and the internal value ({self.observable_name}). '
                f'The internal value will be modified accordingly.'
            )
            self.observable_name = observable_name
        # weightVar only available after ROOT 6.26+]
        if hasattr(dataset, 'weightVar') and dataset.weightVar():
            weight_name = dataset.weightVar().GetName()
        else:
            weight_name = None
        if weight_name and (weight_name != self.weight_name):
            self.stdout.warning(
                f'There is a mismatch in the weight name'
                f'between the data source ({weight_name})'
                f'and the internal value ({self.weight_name}). '
                f'The internal value will be modified accordingly.'
            )
            self.weight_name = weight_name
        self.data = dataset

    def as_dataset(self, name:Optional[str]=None,
                   title:Optional[str]=None) -> "ROOT.RooDataSet":
        return self.data

    def as_arrays(self) -> np.ndarray:
        arrays = self.data.to_numpy()
        if self.weight_name and (self.weight_name not in arrays):
            arrays[self.weight_name] = np.ones(self.data.numEntries())
        return self.validate_arrays(arrays)