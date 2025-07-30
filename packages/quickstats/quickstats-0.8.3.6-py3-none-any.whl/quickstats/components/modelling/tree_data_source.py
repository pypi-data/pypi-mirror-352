from typing import Optional, Union, List, Dict

import numpy as np

from quickstats import cached_import
from quickstats.core.typing import ArrayLike
from quickstats.concepts import Binning, RealVariable
from quickstats.interface.root import RooRealVar
from .data_source import DataSource

class TreeDataSource(DataSource):
    """
    TTree representation of a one-dimensional data input
    """

    def __init__(
        self,
        tree: Union["ROOT.TTree", "ROOT.TChain"],
        observable: Union[str, RealVariable],
        weight_name: Optional[str] = None,
        selection: Optional[str] = None,
        verbosity:Optional[Union[int, str]]="INFO"
    ):
        """
        Parameter
        -----------
        tree : ROOT.TTree or ROOT.TChain
            Input TTree.
        observable_name : str
            Name of the observable for creating datasets. It must be
            a branch found in the tree.
        weight_name : str, optional
            Name of the weight for creating datasets. If specified,
            it must be a branch found in the tree.
        selection : str, optional
            Selection applied when extracting dataset.
        verbosity : Union[int, str], optional
            The verbosity level. Default is "INFO".
        """
        super().__init__(
            observable=observable,
            weight_name=weight_name,
            verbosity=verbosity
        )
        self.set_data(tree)
        self.selection = selection

    @classmethod
    def from_files(
        cls,
        filenames: Union[str, List[str], Dict[str, str]],
        observable: Union[str, RealVariable],
        weight_name: str = 'weight',
        default_treename: Optional[str] = None,
        **kwargs
    ):
        from quickstats.interface.root import TChain
        specs = TChain._get_specs(filenames, default_treename=default_treename)
        tree = TChain._from_specs(specs)
        return cls(tree, observable=observable, weight_name=weight_name, **kwargs)

    def set_data(self, tree:Union["ROOT.TTree", "ROOT.TChain"]) -> None:
        ROOT = cached_import("ROOT")
        from quickstats.interface.root import TChain, TTree
        if isinstance(tree, ROOT.TChain):
            data = TChain(tree)
        elif isinstance(tree, ROOT.TTree):
            data = TTree(tree)
        else:
            raise TypeError('`tree` must be an instance of ROOT.TTree.')
        columns = data.get_column_names()
        if self.observable_name not in columns:
            raise RuntimeError(f'Input tree does not contain a branch named "{self.observable_name}".')
        if self.weight_name and (self.weight_name not in columns):
            raise RuntimeError(f'Input tree does not contain a branch named "{self.weight_name}".')
        self.data = data

    def as_dataset(
        self,
        name:Optional[str]=None,
        title:Optional[str]=None
    ) -> "ROOT.RooDataSet":
        observable = RooRealVar(self.observable).to_root()
        name = name or self.default_dataset_name
        title = title or name
        dataset = self.data.get_dataset(
            observable=observable,
            weight_name=self.weight_name,
            selection=self.selection,
            name=name,
            title=title
        )
        return dataset

    #def as_histogram(self, name:Optional[str]=None,
    #                 title:Optional[str]=None,
    #                 binning: Optional[Binning]=None) -> "ROOT.TH1":
    #    from quickstats.utils.root_utils import delete_object
    #    binning = binning or self.default_binning
    #    name = name or self.default_histogram_name
    #    title = title or name
    #    delete_object(name)
    #    histogram = self.data.get_histo1d(observable=self.observable_name,
    #                                      weight=self.weight_name,
    #                                      bins=binning.nbins,
    #                                      bin_range=binning.bin_range,
    #                                      name=name,
    #                                      title=title)
    #    return histogram

    def as_arrays(self) -> Dict[str, np.ndarray]:
        ROOT = cached_import("ROOT")
        rdf = ROOT.RDataFrame(self.data.obj)
        columns = [self.observable_name]
        if self.weight_name is not None:
            columns.append(self.weight_name)
        if self.selection is not None:
            rdf = rdf.Filter(self.selection)
        arrays = rdf.AsNumpy(columns)
        return self.validate_arrays(arrays)