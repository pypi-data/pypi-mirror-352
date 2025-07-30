from typing import Optional, Union, List, Dict
import numpy as np

from quickstats import semistaticmethod, cached_import
from quickstats.core.typing import ArrayLike
from quickstats.utils.data_blinder import ArrayBlindConditionType
from .TObject import TObject
from .RooDataSet import RooDataSet
from .TH1 import TH1

class TTree(TObject):
    
    def __init__(self, tree: "ROOT.TTree", **kwargs):
        super().__init__(tree=tree, **kwargs)
        
    def initialize(self, tree: "ROOT.TTree"):
        ROOT = cached_import("ROOT")
        if not isinstance(source, ROOT.TTree):
            raise TypeError(f'`tree` must be an instance of ROOT.Tree')
        self.obj = tree

    def get_entries(self, selection:Optional[str]=None):
        if selection:
            return self.obj.GetEntries(selection)
        return self.obj.GetEntries()

    def get_dataset(self, observable: Union[str, "ROOT.RooRealVar"],
                    observable_branchname: Optional[str] = None,
                    weight_branchname: Optional[str] = None,
                    selection: Optional[str] = None,
                    weight_name: Optional[str] = None,
                    apply_ghost: bool = False,
                    blind_condition: Optional[ArrayBlindConditionType] = None,
                    name:Optional[str]=None,
                    title:Optional[str]=None):
        if (weight_name is None) and (weight_branchname is not None):
            raise ValueError('`weight_name` can not be None when `weight_branchname` is not None. Please '
                             'set `weight_name` to the branch name of the weight variable if the weight '
                             'name in the dataset is the same as the branch name.')
        ROOT = cached_import("ROOT")
        if isinstance(observable, str):
            observable = ROOT.RooRealVar(observable, observable, 0)
        elif not isinstance(observable, ROOT.RooRealVar):
            raise ValueError('`observable` must be either a str or a RooRealVar object')
        observable_branchname = observable_branchname or observable.GetName()
        weight_branchname = weight_branchname or weight_name

        columns = [observable_branchname]
        if weight_branchname is not None:
            columns.append(weight_branchname)

        rdf = ROOT.RDataFrame(self.obj)
        if selection:
            rdf = rdf.Filter(selection)
        arrays = rdf.AsNumpy(columns)
        
        # handles renaming
        observable_name = observable.GetName()
        if observable_branchname and (observable_name != observable_branchname):
            arrays[observable_name] = arrays.pop(observable_branchname)
        if weight_branchname and (weight_name != weight_branchname):
            arrays[weight_name] = arrays.pop(weight_branchname)
            
        # set all weights to one by default
        if not weight_name:
            weight_name = RooDataSet.DEFAULT_WEIGHT_NAME
            assert weight_name != observable_name
            arrays[weight_name] = np.ones(arrays[observable_name].shape[0])

        # try to resolve unspecified range
        if (observable.getMin() == -np.inf) and (observable.getMax() == np.inf):
            observable.setVal(arrays[observable_name][0])
            observable.setMin(np.min(arrays[observable_name]))
            observable.setMax(np.max(arrays[observable_name]))
            
        variables = ROOT.RooArgSet(observable)
        dataset = RooDataSet.from_numpy(arrays, variables,
                                        weight_name=weight_name,
                                        apply_ghost=apply_ghost,
                                        blind_condition=blind_condition,
                                        name=name,
                                        title=title)
        return dataset

    def get_histo1d(self, observable:str, weight:Optional[str]=None,
                    bins:ArrayLike=10,
                    bin_range:ArrayLike=None,
                    selection:Optional[str]=None,
                    name:Optional[str]=None,
                    title:Optional[str]=None):
        ROOT = cached_import("ROOT")
        rdf = ROOT.RDataFrame(self.obj)
        if selection is not None:
            rdf = rdf.Filter(selection)
        name = name or observable
        title = title or name
        histo_model = TH1.create_model(bins=bins, bin_range=bin_range,
                                       name=name, title=title)
        if weight is None:
            histo1d = rdf.Histo1D(histo_model, observable)
        else:
            histo1d = rdf.Histo1D(histo_model, observable, weight)
        return histo1d.GetValue()    

    def get_column_names(self):
        return [leaf.GetName() for leaf in self.obj.GetListOfLeaves()]

    # taken from https://root.cern/doc/master/classTChain.html#a98aec49da3a78d4298b7c40d5c1d79bb
    @semistaticmethod
    def parse_tree_filename(self, name:str):
        ROOT = cached_import("ROOT")
        url = ROOT.TUrl(name, True)
        if url.GetProtocol() != "file":
            filename = url.GetUrl()
        else:
            filename = url.GetFileAndOptions()
        query = None
        treename = None
        suffix = None
        fn = url.GetFile()
        # extract query
        options = url.GetOptions()
        if options and (len(options) > 0):
            query = f"?{options}"
        # extract treename
        anchor = url.GetAnchor()
        if anchor and (anchor[0] != '\0'):
            # support "?#tree_name" and "?query#tree_name"
            if (query or ("?#" in name)):
                if '=' in anchor:
                    query += '#'
                    query += anchor
                else:
                    treename = anchor
            else:
                # the anchor is part of the file name
                fn = url.GetFileAndOptions()
        suffix = url.GetFileAndOptions()
        # get options from suffix by removing the file name
        index = suffix.index(fn)
        if index != -1:
            suffix = suffix[:index] + suffix[index + len(fn):]
        # remove the options suffix from the original file name
        index = filename.index(suffix)
        if index != -1:
            filename = filename[:index] + filename[index + len(suffix):]
        
        # special case: [...]file.root/treename
        index = filename.rfind(".root")
        if index != -1:
            slash_index = filename.rfind('/')
            if (slash_index != -1) and (slash_index >= (index + len(".root"))):
                treename = filename[slash_index + 1:]
                filename = filename[:slash_index]
                suffix = f"/{treename}" + suffix
        results = {
            "filename": filename,
            "treename": treename,
            "query": query,
            "suffix": suffix
        }
        return results