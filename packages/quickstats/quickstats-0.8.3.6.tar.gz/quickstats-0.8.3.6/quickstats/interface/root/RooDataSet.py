from typing import Dict, Union, List, Optional, Tuple
import os

import numpy as np

from quickstats import semistaticmethod, AbstractObject, root_version, cached_import
from quickstats.core.typing import ArrayLike
from quickstats.concepts import Histogram1D
from quickstats.utils.string_utils import split_str
from quickstats.utils.data_blinder import (
    DataBlinder,
    ArrayBlindConditionType,
    DataBlindConditionType
)
from quickstats.interface.cppyy.vectorize import as_np_array
from quickstats.maths.histograms import (
    dataset_is_binned,
    fill_missing_bins,
    rebin_dataset,
    bin_edge_to_bin_center,
    poisson_interval,
    CONFIG
)
from .roofit_extension import (
    deduce_category_index_map,
    isolate_category_observables
)
from .RooRealVar import RooRealVar
from .RooVectorDataStore import RooVectorDataStore

# for ROOT 6.24
def _get_weight_var(dataset):
    if hasattr(dataset, 'weightVar'):
        return dataset.weightVar()
    return None

class RooDataSet(AbstractObject):

    DEFAULT_WEIGHT_NAME : str = "weight"
    DEFAULT_DATASET_NAME : str = "dataset"
    
    def __init__(
        self,
        dataset:"ROOT.RooDataSet",
        remove_ghost:bool=False,
        ghost_threshold:Optional[float]=None,
        ghost_weight:Optional[float]=None,
        verbosity:Optional[Union[int, str]]="INFO"
    ):
        super().__init__(verbosity=verbosity)
        self.ghost_threshold = ghost_threshold or CONFIG.ghost_threshold
        self.ghost_weight = ghost_weight or CONFIG.ghost_weight
        self.bin_precision = 8
        self.error_mode = 'poisson'
        self.parse(dataset, remove_ghost=remove_ghost)
        
    def parse(self, dataset:"ROOT.RooDataSet", remove_ghost:bool=False):
        category = self.get_dataset_category(dataset)
        if not category:
            raise RuntimeError('no category defined in the dataset')
        self.set_category_variable(category)
        observables = self.get_dataset_observables(dataset)
        self.set_observable_variables(observables)
        self.data = self.to_numpy(dataset, copy=True,
                                  rename_columns=False,
                                  category_label=False,
                                  remove_ghost=remove_ghost)
        self.name = dataset.GetName()
        self.title = dataset.GetTitle()
        self.set_weight_variable(_get_weight_var(dataset))
        
        obs_cat_pairing = self.pair_category_and_observable(dataset)
        category_map = {}
        for pairing in obs_cat_pairing:
            category_map[pairing['category_label']] = {
                'observable': pairing['observable'],
                'category_index': pairing['category_index']
            }
        self.category_map = category_map
            
    @semistaticmethod
    def to_numpy(self, dataset:"ROOT.RooDataSet", copy:bool=True,
                 rename_columns:bool=False, category_label:bool=False,
                 split_category:bool=False, sort:bool=True,
                 remove_ghost:bool=False):
        # use ROOT's built-in method if available
        if hasattr(dataset, "to_numpy"):
            data = dataset.to_numpy(copy=copy)
        # just copy the implementation from ROOT
        else:
            ROOT = cached_import("ROOT")

            data = {}
            if isinstance(dataset.store(), ROOT.RooVectorDataStore):
                arrays = RooVectorDataStore.to_numpy(dataset.store(), copy=copy)
                for name, array in arrays.items():
                    data[name] = array
            elif isinstance(dataset.store(), ROOT.RooTreeDataStore):
                # first create a VectorDataStore so we can read arrays
                store = dataset.store()
                variables = dataset.get()
                store_name = dataset.GetName()
                tmp_store = ROOT.RooVectorDataStore(store, variables, store_name)
                arrays = RooVectorDataStore.to_numpy(tmp_store, copy=copy)
                for name, array in arrays.items():
                    data[name] = array
            else:
                raise RuntimeError(
                    "Exporting RooDataSet to numpy arrays failed. The data store type "
                    + dataset.store().__class__.__name__
                    + " is not supported."
                )
                
        category = self.get_dataset_category(dataset)
        if category is not None:
            category_col = category.GetName()
        else:
            category_col = None
            
        weight_var = _get_weight_var(dataset)
        if weight_var:
            weight_col = weight_var.GetName()
        else:
            weight_col = None

        if category_label and (category is not None):
            index_values = data[category_col]
            category_map = {d.second:d.first for d in category}
            label_values = np.vectorize(category_map.get)(index_values)
        else:
            label_values = None
            
        if rename_columns:
            if weight_col is not None:
                data['weight'] = data.pop(weight_col)
                weight_col = 'weight'
            if category_col is not None:
                data['category_index'] = data.pop(category_col)
                category_col = 'category_index'
                
        if label_values is not None:
            data['category_label'] = label_values
            
        if remove_ghost and (weight_col is not None):
            mask = data[weight_col] > CONFIG.ghost_threshold
            for key in data:
                data[key] = data[key][mask]
            
        if split_category:
            if category is None:
                raise RuntimeError('cannot split dataset by category: no category '
                                   'defined in the dataset')
            cat_obs_info_list = self.pair_category_and_observable(dataset)
            cat_data = {}
            for cat_obs_info in cat_obs_info_list:
                cat_label = cat_obs_info['category_label']
                cat_index = cat_obs_info['category_index']
                observable = cat_obs_info['observable']
                mask = data[category_col] == cat_index
                obs_values = data[observable][mask]
                wt_values  = data[weight_col][mask]
                if sort:
                    sort_idx = np.argsort(obs_values)
                    obs_values = obs_values[sort_idx]
                    wt_values = wt_values[sort_idx]
                cat_data[cat_label] = {
                    observable: obs_values,
                    weight_col: wt_values
                }
            return cat_data
            
        return data
    
    @staticmethod
    def from_numpy(data: Dict[str, np.ndarray], variables: "ROOT.RooArgSet",
                   name: Optional[str] = None,
                   title: Optional[str] = None,
                   weight_name: Optional[str] = None,
                   apply_ghost: bool = False,
                   blind_condition: Optional[DataBlindConditionType] = None) -> "ROOT.RooDataSet":
        ROOT = cached_import("ROOT")

        # make arrays c-contiguous
        if not root_version > (6, 28, 0):
            tmp = {}
            for key, arr in data.items():
                tmp[key] = np.ascontiguousarray(arr)
            data = tmp

        if (apply_ghost or blind_condition):
            category, observables = isolate_category_observables(variables)
            observable_names = [observable.GetName() for observable in observables]
            if weight_name:
                observables = [v for v in observables if v.GetName() != weight_name]
            if (len(observables) > 1 ) and (category is None):
                raise RuntimeError('Missing category variable for multi-observable dataset.')
            if category is not None:
                category_name = category.GetName()
                category_index_map = deduce_category_index_map(data, category_name,
                                                               observable_names)
                default_value_map = {observable.GetName(): RooRealVar.get_default_value(observable) \
                                     for observable in observables}
            else:
                category_index_map = None
                default_value_map = None
                
            # make a copy
            data = {key: np.array(value) for key, value in data.items()}

            if apply_ghost:
                if weight_name is None:
                    weight_name = RooDataSet.DEFAULT_WEIGHT_NAME
                    assert weight_name not in observable_names
                    data[weight_name] = np.ones(data[observable_names[0]].shape)
                for observable in observables:
                    observable_name = observable.GetName()
                    binning = RooRealVar.get_binning(observable)
                    array = data[observable_name]
                    hist, bin_edges = np.histogram(array, bins=binning.bin_edges)
                    assert np.allclose(binning.bin_edges, bin_edges)
                    zero_indices = (hist == 0.)
                    bin_centers = binning.bin_centers[zero_indices]
                    weights = np.full(len(bin_centers), CONFIG.ghost_weight)
                    data[observable_name] = np.concatenate([data[observable_name],
                                                            bin_centers])
                    if weight_name:
                        data[weight_name] = np.concatenate([data[weight_name],
                                                            weights])
                    # fill in values for other observables as well
                    if category_index_map is not None:
                        category_index = category_index_map[observable_name]
                        category_values = np.full(len(bin_centers), category_index)
                        data[category_name] = np.concatenate([data[category_name], category_values])
                        other_observable_names = [name for name in observable_names if name != observable_name]
                        for other_observable_name in other_observable_names:
                            default_value = default_value_map[other_observable_name]
                            values = np.full(len(bin_centers), default_value)
                            data[other_observable_name] = np.concatenate([data[other_observable_name], values])
                            
            if blind_condition is not None:
                blinder = DataBlinder(blind_condition)
                obs_data = {observable_name: data[observable_name] for observable_name in observable_names}
                obs_mask = blinder.get_mask(obs_data)
                combined_mask = np.full(data[observable_names[0]].shape, True)
                if category_index_map is not None:
                    category_data = data[category_name]
                    for observable_name in observable_names:
                        category_index = category_index_map[observable_name]
                        category_mask = category_data == category_index
                        combined_mask = combined_mask & (~(obs_mask[observable_name] & category_mask))
                else:
                    for observable_name in observable_names:
                        combined_mask = combined_mask & (~obs_mask[observable_name])
                for key in data:
                    data[key] = data[key][combined_mask]
        # requires ROOT's built-in method
        if not hasattr(ROOT.RooDataSet, "from_numpy"):
            func = RooDataSet._from_numpy
        else:
            func = ROOT.RooDataSet.from_numpy
        dataset = func(data, variables,
                       name=name,
                       title=title,
                       weight_name=weight_name)
            
        return dataset

    # copied from https://github.com/root-project/root/blob/master/bindings/pyroot/pythonizations/python/ROOT/_pythonization/_roofit/_roodataset.py
    @staticmethod
    def _from_numpy(data, variables, name=None, title=None, weight_name=None):
        """Create a RooDataSet from a dictionary of numpy arrays.
        Args:
            data (dict): Dictionary with strings as keys and numpy arrays as
                         values, to be imported into the RooDataSet.
            variables (RooArgSet, or list/tuple of RooAbsArgs):
                Specification of the variables in the RooDataSet, will be
                forwarded to the RooDataSet constructor. Both real values and
                categories are supported.
            name (str): Name of the RooDataSet, `None` is equivalent to an
                        empty string.
            title (str): Title of the RooDataSet, `None` is equivalent to an
                         empty string.
            weight_name (str): Key of the array in `data` that will be used for
                               the dataset weights.

        Returns:
            RooDataSet
        """
        import ROOT
        import numpy as np
        import ctypes

        name = "" if name is None else name
        title = "" if title is None else title

        if weight_name is None:
            dataset = ROOT.RooDataSet(name, title, variables)
        else:
            if not variables.find(weight_name):
                variables = ROOT.RooArgSet(variables)
                weight_var = ROOT.RooRealVar(weight_name, weight_name, 1)
                variables.add(weight_var)
            dataset = ROOT.RooDataSet(name, title, variables, weight_name)

        def log_warning(s):
            """Log a string to the RooFit message log for the WARNING level on
            the DataHandling topic.
            """
            log = ROOT.RooMsgService.instance().log(dataset, ROOT.RooFit.WARNING, ROOT.RooFit.DataHandling)
            b = bytes(s, "utf-8")
            log.write(b, len(b))
            log.write("\n", 1)

        range_mask = np.ones_like(list(data.values())[0], dtype=bool)

        def in_range(arr, variable):
            # For categories, we need to check whether the elements of the
            # array are in the set of category state indices
            if hasattr(variable, 'isCategory'):
                is_category = variable.isCategory()
            else:
                is_category = isinstance(variable, ROOT.RooCategory)
            if is_category:
                return np.isin(arr, [state.second for state in variable])

            return (arr >= variable.getMin()) & (arr <= variable.getMax())

        # Get a mask that filters out all entries that are outside the variable definition range
        range_mask = np.logical_and.reduce([in_range(data[v.GetName()], v) for v in variables])
        # If all entries are in the range, we don't need a mask
        if range_mask.all():
            range_mask = None

        size = len(data[list(data.keys())[0]])
        variable_map = {variable.GetName(): variable for variable in variables}
        if weight_name is None:
            weight_name = '__weight'
            assert weight_name not in data
            data[weight_name] = np.ones(size)
        for i in range(size):
            for varname, variable in variable_map.items():
                variable.setVal(data[varname][i])
            if (range_mask is None) or (range_mask[i]):
                dataset.add(variables, data[weight_name][i])

        if range_mask is not None:
            n_out_of_range = len(range_mask) - range_mask.sum()
            log_warning("RooDataSet.from_numpy({0}) Ignored {1} out-of-range events".format(name, n_out_of_range))

        return dataset

    @semistaticmethod
    def to_pandas(self, dataset:"ROOT.RooDataSet", copy:bool=True,
                  rename_columns:bool=True, category_label:bool=True,
                  split_category:bool=False, sort:bool=True,
                  remove_ghost:bool=False):
        numpy_data = self.to_numpy(dataset, copy=copy,
                                   rename_columns=rename_columns,
                                   category_label=category_label,
                                   split_category=split_category,
                                   sort=sort,
                                   remove_ghost=remove_ghost)
        import pandas as pd
        if split_category:
            df_cat = {}
            for category, category_data in numpy_data.items():
                df_cat[category] = pd.DataFrame(category_data)
            return df_cat
        df = pd.DataFrame(numpy_data)
        return df
    
    to_dataframe = to_pandas
    
    @staticmethod
    def from_pandas(df, variables, name=None, title=None, weight_name=None):
        ROOT = cached_import("ROOT")
        # use ROOT's built-in method
        if hasattr(ROOT.RooDataSet, "from_pandas"):
            dataset = ROOT.RooDataSet.from_pandas(df, variables,
                                                  name=name,
                                                  title=title,
                                                  weight_name=weight_name)
        else:
            raise NotImplementedError
        return dataset
    
    @staticmethod
    def get_dataset_map(dataset_dict: Dict[str, "ROOT.RooDataSet"]):
        from quickstats.interface.cppyy.basic_methods import get_std_object_map
        dataset_map = get_std_object_map(dataset_dict, 'RooDataSet')
        return dataset_map
    
    @staticmethod
    def from_category_data(
        data,
        variables: "ROOT.RooArgSet",
        name: Optional[str]=None,
        title: Optional[str]=None,
        weight_name: Optional[str]=None,
        add_ghost:bool=False,
        ghost_weight:float=CONFIG.ghost_weight
    ):
        ROOT = cached_import("ROOT")
        
        if name is None:
            name = "dataset"
        if title is None:
            title = name

        def get_category_observable(columns:List[str], category:str):
            candidates = [column for column in columns if variables.find(column)]
            if weight_name is not None:
                candidates = [column for column in columns if column != weight_name]
            if len(candidates) != 1:
                raise RuntimeError(f'failed to deduce observable name for the category "{category}"')
            return variables.find(candidates[0])
        
        dataset_map = {}
        for category, cat_data in data.items():
            cat_variables = ROOT.RooArgSet()
            columns = list(cat_data.keys())
            cat_observable = get_category_observable(columns, category)
            cat_variables.add(cat_observable)
            if weight_name is not None:
                weight_var = ROOT.RooRealVar(weight_name, weight_name, 1)
                cat_variables.add(weight_var)
            cat_name = f"{name}_{category}"
            cat_title = f"{title}_{category}"
            cat_dataset = RooDataSet.from_numpy(cat_data, cat_variables,
                                                name=cat_name, title=cat_title,
                                                weight_name=weight_name)
            if add_ghost:
                RooDataSet.add_ghost_weights(cat_dataset,
                                             ghost_weight=ghost_weight)
            dataset_map[category] = cat_dataset

        # not needed by newer version of ROOT
        c_dataset_map = RooDataSet.get_dataset_map(dataset_map)
        cat_var = [v for v in variables if v.ClassName() == "RooCategory"]
        _variables = ROOT.RooArgSet(variables)
        if not cat_var:
            cat_var = ROOT.RooCategory('category', 'category')
            for category in data:
                cat_var.defineType(category)
        else:
            cat_var = cat_var[0]
            _variables.remove(cat_var)

        if weight_name is not None:
            weight_var = _variables.find(weight_name)
            if not weight_var:
                weight_var = ROOT.RooRealVar(weight_name, weight_name, 1)
                _variables.add(weight_var)
            dataset = ROOT.RooDataSet(name, title, _variables,
                                      ROOT.RooFit.Index(cat_var),
                                      ROOT.RooFit.Import(dataset_map),
                                      ROOT.RooFit.WeightVar(weight_var))
        else:
            dataset = ROOT.RooDataSet(name, title, _variables,
                                      ROOT.RooFit.Index(cat_var),
                                      ROOT.RooFit.Import(dataset_map))
        return dataset
    
    @staticmethod
    def from_RooDataHist(source:"ROOT.RooDataHist", pdf:"ROOT.RooAbsPdf",
                         name:Optional[str]=None):
        ROOT = cached_import("ROOT")
        if name is None:
            name = source.GetName()
        parameters = source.get()
        category = None
        for parameter in parameters:
            if parameter.ClassName() == "RooCategory":
                category = parameter
                break
      # case multi-category data
        if category is not None:
            dataset_map = {}
            data_cat = source.split(category, True)
            n_cat = len(category)
            observables = ROOT.RooArgSet()
            for i in range(n_cat):
                category.setBin(i)
                cat_name = category.getLabel()
                pdf_i = pdf.getPdf(cat_name)
                data_i = data_cat.FindObject(cat_name)                
                obs_i = pdf_i.getObservables(data_i).first()
                _obs_i = data_i.get().find(obs_i.GetName())
                w_i = ROOT.RooRealVar(f"weight_{i}", f"weight_{i}", 1)
                dataset_i = ROOT.RooDataSet(f"dataset_{i}", f"dataset_{i}",
                                            ROOT.RooArgSet(obs_i, w_i),
                                            ROOT.RooFit.WeightVar(w_i))
                ROOT.RFUtils.CopyData(data_i, dataset_i, _obs_i, obs_i, w_i)
                dataset_map[cat_name] = dataset_i
                observables.add(obs_i)
            w = ROOT.RooRealVar("weight", "weight", 1)
            observables.add(w)
            cpp_dataset_map = RooDataSet.get_dataset_map(dataset_map)
            dataset = ROOT.RooDataSet(name, name, observables,
                                      ROOT.RooFit.Index(category),
                                      ROOT.RooFit.Import(cpp_dataset_map),
                                      ROOT.RooFit.WeightVar(w))
        # case single-category data
        else:
            obs = pdf.getObservables(source).first()
            _obs = source.get().find(obs.GetName())
            w = ROOT.RooRealVar("weight", "weight", 1)
            dataset = ROOT.RooDataSet(name, name, ROOT.RooArgSet(obs, w),
                                      ROOT.RooFit.WeightVar(w))
            ROOT.RFUtils.CopyData(source, dataset, _obs, obs, w)
        return dataset

    @staticmethod
    def _get_cat_and_obs(variables:"ROOT.RooArgSet"):
        cat_variable = None
        observables = {}
        for v in variables:
            class_name = v.ClassName()
            if class_name == "RooCategory":
                if cat_variable is not None:
                    raise RuntimeError("found multiple RooCategory instances")
                cat_variable = v
            else:
                var_name = v.GetName()
                observables[var_name] = v
        if cat_variable is None:
            raise RuntimeError("missing RooCategory instance from variables")
        return cat_variable, observables
    
    @staticmethod
    def get_dataset_observables(dataset:"ROOT.RooDataSet", fmt:str="argset"):
        """
        Extract the observables from the dataset.
        """
        ROOT = cached_import("ROOT")
        observables = ROOT.RFUtils.GetDatasetObservables(dataset)
        if fmt == "list":
            return [obs for obs in observables]
        elif fmt == "argset":
            return observables
        else:
            raise ValueError(f'unsupported output format: {fmt}')
    
    @staticmethod
    def get_dataset_category(dataset:"ROOT.RooDataSet"):
        """
        Extract the category variable from the dataset.
        """
        ROOT = cached_import("ROOT")
        category = ROOT.RFUtils.GetDatasetCategory(dataset)
        if not category:
            return None
        return category
    
    @semistaticmethod
    def pair_category_and_observable(self, dataset):
        category = self.get_dataset_category(dataset)
        if category is None:
            return None
        observables = self.get_dataset_observables(dataset)
        observables = [obs.GetName() for obs in observables]
        numpy_data = self.to_numpy(dataset, copy=False,
                                   rename_columns=True,
                                   category_label=False)
        result = []
        for cat_data in category:
            cat_label = cat_data.first
            cat_index = cat_data.second
            mask = numpy_data['category_index'] == cat_index
            obs_with_changing_values = []
            for observable in observables:
                obs_values = numpy_data[observable][mask]
                if len(np.unique(obs_values)) > 1:
                    obs_with_changing_values.append(observable)
            if len(obs_with_changing_values) != 1:
                self.stdout.warning(f'Failed to deduce observable for the category: {cat_label} {obs_with_changing_values}')
                continue
            paired_data = {
                'observable': obs_with_changing_values[0],
                'category_index': cat_index,
                'category_label': cat_label
            }
            result.append(paired_data)
        return result

    @semistaticmethod
    def create_binned_category_dataset(self, data:Dict[str, "numpy.ndarray"],
                                       pdf:"ROOT.RooAbsPdf",
                                       variables:"ROOT.RooArgSet",
                                       weight_name:str="weightVar",
                                       name:str=None, title:str=None):
        ROOT = cached_import("ROOT")
        if name is None:
            name = ""
        if title is None:
            title = ""        
        cat_variable, observables = self._get_cat_and_obs(variables)
        n_cat = cat_variable.size()
        cat_names = []
        cat_obs_names = []
        for i in range(n_cat):
            cat_variable.setIndex(i)
            cat_name = cat_variable.getLabel()
            cat_names.append(cat_name)
            pdf_cat = pdf.getPdf(cat_name)
            obs = pdf_cat.getObservables(variables)
            cat_obs = obs.first()
            cat_obs_names.append(cat_obs.GetName())
        if set(cat_obs_names) != set(observables):
            raise RuntimeError("the given variables are insistent with the category observables")
        if not set(cat_names).issubset(set(data)):
            missing = list(set(cat_names) - set(data))
            raise RuntimeError("missing data for the following categories: {}".format(",".join(missing)))
        dataset = ROOT.RooDataSet(name, title, variables, weight_name)
        for i, (cat_name, obs_name) in enumerate(zip(cat_names, cat_obs_names)):
            observable = observables[obs_name]
            data_i = data[cat_name]
            cat_variable.setIndex(i)
            nbins = observable.getBins()
            nbins_data = len(data_i)
            if nbins_data != nbins:
                raise RuntimeError(f"the observable has `{nbins}` bins but data has `{nbins_data}`")
            for j in range(nbins_data):
                observable.setBin(j)
                dataset.add(variables, data_i[j])
        return dataset
    
    @staticmethod
    def fill_from_TH1(dataset:"ROOT.RooDataSet", hist:"ROOT.TH1",
                      skip_out_of_range:bool=True,
                      blind_range:Optional[List[float]]=None,
                      min_bin_value:float=0,
                      weight_scale:float=1):
        ROOT = cached_import("ROOT")
        parameters = dataset.get()
        if parameters.size() > 1:
            raise RuntimeError("multiple observables are not allowed")
        x = parameters.first()
        weight_var = _get_weight_var(dataset)
        # blinding will be taken care of
        xmin = x.getMin()
        xmax = x.getMax()
        nbins = hist.GetNbinsX()
        for i in range(1, nbins + 1):
            bin_center = hist.GetBinCenter(i)
            # skip bins that are out of range
            if skip_out_of_range and ((bin_center > xmax) or (bin_center < xmin)):
                continue
            # skip bins in the blind range
            if (blind_range and (bin_center > blind_range[0]) and (bin_center < blind_range[1])):
                continue
            x.setVal(bin_center)
            bin_content = hist.GetBinContent(i)
            weight = bin_content * weight_scale
            # if the weight is negligible, consider it as zero
            if (weight < min_bin_value):
                continue
            if weight_var:
                weight_var.setVal(weight)
                dataset.add(ROOT.RooArgSet(x, weight_var), weight)
            else:
                dataset.add(ROOT.RooArgSet(x), weight)
    
    @staticmethod
    def get_x_and_weight(dataset:"ROOT.RooDataSet"):
        parameters = dataset.get()
        if parameters.size() > 1:
            raise RuntimeError("multiple observables are not allowed")
        x = parameters.first()
        weight_var = _get_weight_var(dataset)
        return x, weight_var
    
    @staticmethod
    def to_TH1(dataset:"ROOT.RooDataSet", name:str,
               blind_range:Optional[List[float]]=None,
               weight_scale:float=1):
        ROOT = cached_import("ROOT")
        x, weight_var = RooDataSet.get_x_and_weight(dataset)
        nbins = x.getBins()
        x_min = x.getMin()
        x_max = x.getMax()
        hist = ROOT.TH1D(name, name, nbins, x_min, x_max)
        hist.Sumw2()
        for i in range(dataset.numEntries()):
            dataset.get(i)
            x_val = x.getVal()
            obs.setVal(x_val)
            weight = dataset.weight() * weight_scale
            # ignore data in the blind range
            if (blind_range and (x_val > blind_range[0]) and (x_val < blind_range[1])):
                continue
            hist.Fill(x_val, weight)
        return hist
    
    @staticmethod
    def add_ghost_weights(
        dataset:"ROOT.RooDataSet",
        blind_range:Optional[List[float]]=None,
        ghost_weight:float=CONFIG.ghost_weight
    ):
        ROOT = cached_import("ROOT")
        x, weight_var = RooDataSet.get_x_and_weight(dataset)
        xmin, xmax = x.getMin(), x.getMax()
        nbins = x.getBins()
        bin_width = (xmax - xmin) / nbins
        data = RooDataSet.to_numpy(dataset, rename_columns=True)
        x_data = data[x.GetName()]
        weight_data = data["weight"]
        hist, bin_edges = np.histogram(x_data, bins=nbins, range=(xmin, xmax), weights=weight_data)
        from quickstats.maths.statistics import bin_edge_to_bin_center
        bin_centers = bin_edge_to_bin_center(bin_edges)
        # to be optimized
        for bin_val, bin_center in zip(hist, bin_centers):
            if (bin_val != 0):
                continue
            if (blind_range and (bin_center > blind_range[0]) and (bin_center < blind_range[1])):
                continue
            x.setVal(bin_center)
            if weight_var is not None:
                weight_var.setVal(ghost_weight)
                dataset.add(ROOT.RooArgSet(x, weight_var), ghost_weight)
            else:
                dataset.add(ROOT.RooArgSet(x), ghost_weight)
         
    @semistaticmethod
    def compare_category_data(self, ds1:"ROOT.RooDataSet", ds2:"ROOT.RooDataSet", rtol=1e-8):
        ds1_data = self.to_numpy(ds1, split_category=True)
        ds2_data = self.to_numpy(ds1, split_category=True)
        ds1_has_cat = self.get_dataset_category(ds1) is not None
        ds2_has_cat = self.get_dataset_category(ds2) is not None
        if (not ds1_has_cat) or  (not ds2_has_cat):
            raise RuntimeError('all input datasets must have category index')
        df1_cats = list(ds1_data.keys())
        df2_cats = list(ds2_data.keys())
        common_cats = list(set(df1_cats).intersection(df2_cats))
        unique_cats_left = list(set(df1_cats) - set(common_cats))
        unique_cats_right = list(set(df2_cats) - set(common_cats))
        def get_sorted_obs_and_weight(data):
            columns = list(data.keys())
            try:
                obs_col = [i for i in columns if i != 'weight'][0]
            except Exception:
                raise RuntimeError('unable to deduce observable column from data')
            obs_values = data[obs_col]
            weight_values = data['weight']
            indices = np.argsort(obs_values)
            return obs_values[indices], weight_values[indices]
        result = {
            'identical': [],
            'modified': [],
            'unique_left': unique_cats_left,
            'unique_right': unique_cats_right
        }
        for category in common_cats:
            obs_values_1, weight_values_1 = get_sorted_obs_and_weight(ds1_data[category])
            obs_values_2, weight_values_2 = get_sorted_obs_and_weight(ds2_data[category])
            if (np.allclose(obs_values_1, obs_values_2, rtol=rtol) and 
                np.allclose(weight_values_1, weight_values_2, rtol=rtol)):
                result['identical'].append(category)
            else:
                result['modified'].append(category)
        return result
    
    @semistaticmethod
    def dataset_equal(self, ds1:"ROOT.RooDataSet", ds2:"ROOT.RooDataSet", rtol=1e-8):
        result = self.compare_category_data(ds1, ds2)
        return (len(result['modified']) == 0) and (len(result['unique_left']) == 0) and (len(result['unique_right']) == 0)
        
    def set_observable_variables(self, observables):
        _observables = []
        from .RooRealVar import RooRealVar
        for observable in observables:
            _observables.append(RooRealVar(observable))
        self.observables = _observables
        
    def set_category_variable(self, category):
        from .RooCategory import RooCategory
        self.category = RooCategory(category)
        
    def set_weight_variable(self, weight):
        if weight:
            from .RooRealVar import RooRealVar
            self.weight = RooRealVar(weight)
        else:
            self.weight = None
    
    def clip_to_range(self, ranges:Optional[Union[Tuple[float], Dict[str, Tuple[float]]]]=None,
                      inplace:bool=True):
        index_map = {}
        
        for category in self.category_map:
            category_index = self.category_map[category]['category_index']
            observable = self.category_map[category]['observable']
            if observable not in index_map:
                index_map[observable] = []
            index_map[observable].append(category_index)
            
        if ranges is None:
            ranges = {observable.name: observable.range for observable in self.observables}
        elif not isinstance(ranges, dict):
            ranges = {observable.name: ranges for observable in self.observables}
        
        range_mask = np.ones_like(list(self.data.values())[0], dtype=bool)

        def in_range(arr, variable):
            return (arr >= ranges[variable][0]) & (arr <= ranges[variable][1])
        
        def in_cat(arr, variable):
            return np.isin(arr, index_map[variable])
        
        cat_name = self.category.name
        range_mask = np.logical_and.reduce([(in_range(self.data[obs], obs) | \
                                            ~in_cat(self.data[cat_name], obs)) \
                                            for obs in ranges])
        
        if range_mask.all():
            if inplace:
                return None
            else:
                return self.data.copy()
        result = {column: self.data[column][range_mask] for column in self.data}
        if inplace:
            self.data = result
            return None
        else:
            return result
    
    def scale_category_weights(self, scale_factors:Union[float, Dict[str, float]]):
        if not isinstance(scale_factors, dict):
            scale_factors = {category: scale_factors for category in self.category_map}
        category_name = self.category.name
        weight_name = self.weight.name
        for category, scale_factor in scale_factors.items():
            if category not in self.category_map:
                raise ValueError(f'dataset has no category "{category}"')
            category_index = self.category_map[category]['category_index']
            mask = self.data[category_name] == category_index
            self.data[weight_name][mask] *= scale_factor
    
    def get_category_data(self, category:str, sort:bool=True,
                          remove_ghost:bool=False):
        category_name = self.category.name
        weight_name = self.weight.name
        category_index = self.category_map[category]['category_index']
        observable_name = self.category_map[category]['observable']
        mask = self.data[category_name] == category_index
        obs_values = self.data[observable_name][mask]
        wt_values = self.data[weight_name][mask]
        if sort:
            sort_idx = np.argsort(obs_values)
            obs_values = obs_values[sort_idx]
            wt_values = wt_values[sort_idx]
        if remove_ghost:
            mask = wt_values > self.ghost_threshold
            obs_values = obs_values[mask]
            wt_values = wt_values[mask]
        category_data = {
            observable_name: obs_values,
            weight_name: wt_values
        }
        return category_data
    
    def get_category_histogram(self, category:str, histname:str='hist',
                               histtitle:Optional[str]=None,
                               nbins:Optional[int]=None,
                               bin_range:Optional[Tuple[float]]=None,
                               weight_scale:Optional[float]=None,
                               include_error:bool=True,
                               remove_ghost:bool=False):
        distribution = self.get_category_distribution(category, nbins=nbins,
                                                      bin_range=bin_range,
                                                      weight_scale=weight_scale,
                                                      include_error=False,
                                                      remove_ghost=remove_ghost)
        if include_error:
            bin_error, _ = self.get_weight_error(distribution['y'], error_mode='sumw2')
        else:
            bin_error = None
        from quickstats.interface.root import TH1
        from quickstats.maths.statistics import bin_center_to_bin_edge
        bin_edges = bin_center_to_bin_edge(distribution['x'])
        hist = TH1.from_numpy_histogram(distribution['y'],
                                        bin_edges=bin_edges,
                                        bin_error=bin_error)
        roohist = hist.to_ROOT(histname, histtitle)
        return roohist
        
    
    def get_category_distribution(
        self,
        category:str,
        nbins:Optional[int]=None,
        bin_range:Optional[Tuple[float]]=None,
        weight_scale:Optional[float]=None,
        include_error:bool=True,
        remove_ghost:bool=False
    ):
        data = self.get_category_data(category, sort=True)
        observable_name = self.category_map[category]['observable']
        weight_name = self.weight.name
        x, y = data[observable_name], data[weight_name]
        observable = [obs for obs in self.observables if obs.name == observable_name]
        assert len(observable) == 1
        observable = observable[0]
        default_nbins = observable.nbins
        if nbins is None:
            nbins = default_nbins
        if bin_range is None:
            bin_range = observable.range
        else:
            #remove bins outside custom range
            range_mask = (x >= bin_range[0]) & (x <= bin_range[1])
            x, y = x[range_mask], y[range_mask]
        binned_dataset = dataset_is_binned(x, y, xlow=bin_range[0],
                                           xhigh=bin_range[1],
                                           nbins=default_nbins,
                                           ghost_threshold=self.ghost_threshold,
                                           bin_precision=self.bin_precision)
        # binned dataset with blinded range
        if binned_dataset and (len(x) != default_nbins):
            x, y = fill_missing_bins(x, y, xlow=bin_range[0],
                                     xhigh=bin_range[1],
                                     nbins=default_nbins,
                                     value=0.,
                                     bin_precision=self.bin_precision)
        # rebin binned dataset
        if binned_dataset and (nbins != default_nbins):
            h = Histogram1D.create(x, y, bins=default_nbins, evaluate_error=False, ghost_weight=self.ghost_weight)
            h_rebinned = h.rebin(nbins, keep_ghost=not remove_ghost)
            x, y = h_rebinned.bin_centers, h_rebinned.bin_content
            self.stdout.warning(f"Rebinned dataset ({self.name}, category = {category}) "
                                f"from nbins = {default_nbins} to nbins = {nbins}")
        if not binned_dataset:
            non_ghost_mask = (y > self.ghost_threshold)
            if (not remove_ghost) or non_ghost_mask.all():
                x_non_ghost = x
                y_non_ghost = y
            else:
                x_non_ghost = x[non_ghost_mask]
                y_non_ghost = y[non_ghost_mask]
            hist, bin_edges = np.histogram(x_non_ghost, bins=nbins,
                                           range=(bin_range[0], bin_range[1]),
                                           density=False, weights=y_non_ghost)
            bin_centers = bin_edge_to_bin_center(bin_edges)
            x = bin_centers
            y = hist

        if include_error:
            # it will not be accurate for already binned dataset since the sumw2
            # information is not stored in RooDataset
            yerrlo, yerrhi = self.get_weight_error(y, self.error_mode)
        else:
            yerrlo, yerrhi = None, None
            
        if weight_scale is not None:
            y *= weight_scale
            if (yerrlo is not None) and (yerrhi is not None):
                yerrlo *= weight_scale
                yerrhi *= weight_scale
        result = {
            "x": x,
            "y": y
        }
        if (yerrlo is not None) and (yerrhi is not None):
            result["yerrlo"] = yerrlo
            result["yerrhi"] = yerrhi
        return result
    
    def create_binned_dataset(self, binnings:Optional[Union[Dict[str, int], int]]=None) -> "RooDataSet":
        raise NotImplementedError

    @staticmethod
    def _get_merged_distribution(distributions:Dict[str, Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        x, y, yerrlo, yerrhi = None, None, None, None
        for category, distribution in distributions.items():
            if x is None:
                x = distribution['x']
                y = distribution['y']
            elif not np.array_equal(x, distribution['x']):
                raise RuntimeError('can not merge category distributions with different binnings')
            else:
                y += distribution['y']
            if ('yerrlo' in distribution) and ('yerrhi' in distribution):
                if (yerrlo is None) and (yerrhi is None):
                    yerrlo = distribution['yerrlo'] ** 2
                    yerrhi = distribution['yerrhi'] ** 2
                else:
                    yerrlo += distribution['yerrlo'] ** 2
                    yerrhi += distribution['yerrhi'] ** 2
        result = {
            'x': x,
            'y': y
        }
        if (yerrlo is not None) and (yerrhi is not None):
            # check if distribution is unbinned
            if all(y_i.is_integer() for y_i in y) and (not np.array_equal(yerrlo, yerrhi)):
                yerrlo, yerrhi = RooDataSet.get_weight_error(y, "poisson")
            else:
                yerrlo, yerrhi = RooDataSet.get_weight_error(y, "sumw2")
            result["yerrlo"] = yerrlo
            result["yerrhi"] = yerrhi
        return result

    def get_category_distributions(self, categories:Optional[List[str]]=None,
                                   nbins:Optional[Union[Dict[str, int], int]]=None,
                                   bin_range:Optional[Union[Dict[str, Tuple[float]], Tuple[float]]]=None,
                                   include_error:bool=True,
                                   weight_scales:Optional[Union[float, Dict[str, float]]]=None,
                                   remove_ghost:bool=False,
                                   merge:bool=False) -> Dict[str, np.ndarray]:
        if categories is None:
            categories = list(self.category_map)
        if weight_scales is None:
            weight_scales = {}
        if not isinstance(weight_scales, dict):
            weight_scales = {category: weight_scales for category in categories}
        if not isinstance(nbins, dict):
            nbins = {category: nbins for category in categories}
        if not isinstance(bin_range, dict):
            bin_range = {category: bin_range for category in categories}
        distributions = {}
        for category in categories:
            weight_scale = weight_scales.get(category, None)
            nbins_cat = nbins.get(category, None)
            bin_range_cat = bin_range.get(category, None)
            distribution = self.get_category_distribution(category=category,
                                                          nbins=nbins_cat,
                                                          bin_range=bin_range_cat,
                                                          weight_scale=weight_scale,
                                                          include_error=include_error,
                                                          remove_ghost=remove_ghost)
            distributions[category] = distribution
        if merge:
            return self._get_merged_distribution(distributions)
        return distributions
    
    @semistaticmethod
    def get_weight_error(self, weight:np.ndarray, error_mode:str='sumw2'):
        if error_mode == "poisson":
            return poisson_interval(weight)
        elif error_mode == "sumw2":
            weight_error = np.sqrt(weight)
            return weight_error, weight_error
        else:
            raise RuntimeError(f'Unknown error mode: {error_mode}')
    
    def new(self) -> "ROOT.RooDataSet":
        ROOT = cached_import("ROOT")
        variables = ROOT.RooArgSet()
        for observable in self.observables:
            variables.add(observable.new())
        variables.add(self.category.new())
        if self.weight is not None:
            weight_var = self.weight.new()
            variables.add(weight_var)
            weight_name = weight_var.GetName()
        else:
            weight_name = None
        dataset = ROOT.RooDataSet.from_numpy(self.data, variables,
                                             name=self.name,
                                             title=self.title,
                                             weight_name=weight_name)
        return dataset

    @semistaticmethod
    def get_default_weight_var(self) -> "ROOT.RooRealVar":
        ROOT = cached_import("ROOT")
        return ROOT.RooRealVar(self.DEFAULT_WEIGHT_NAME,
                               self.DEFAULT_WEIGHT_NAME,
                               1.)

    @semistaticmethod
    def _resolve_name_title(self,
                            name: Optional[str] = None,
                            title: Optional[str] = None) -> Tuple[str, str]:
        name = name or self.DEFAULT_DATASET_NAME
        title = title or name
        return name, title

    @semistaticmethod
    def from_counting(self, count: float,
                      observable: "ROOT.RooRealVar",
                      weight_name: Optional[str] = None,
                      apply_ghost: bool = False,
                      blind_condition: Optional[ArrayBlindConditionType] = None,
                      name: Optional[str] = None,
                      title: Optional[str] = None) -> "ROOT.RooDataSet":
        ROOT = cached_import("ROOT")
        obs_min, obs_max = observable.getMin(), observable.getMax()
        if (obs_min == -np.inf) or (obs_max == -np.inf):
            raise ValueError('Observable range must be bounded to create a counting dataset.')
        bin_center = (obs_min + obs_max) / 2.
        if apply_ghost and (count == 0.):
            count = CONFIG.ghost_weight
        observable_name = observable.GetName()
        if weight_name is None:
            weight_name = self.DEFAULT_WEIGHT_NAME
            assert observable_name != weight_name
        variables = ROOT.RooArgSet(observable)
        if weight_name not in variables:
            weight_var = ROOT.RooRealVar(weight_name, weight_name, 1)
            variables.add(weight_var)        
        data = {
            observable_name : np.array([bin_center]),
            weight_name : np.array([count])
        }
        name, title = self._resolve_name_title(name, title)
        dataset = self.from_numpy(data,
                                  variables=variables,
                                  weight_name=weight_name,
                                  apply_ghost=apply_ghost,
                                  blind_condition=blind_condition,
                                  name=name,
                                  title=title)
        return dataset
    
    @semistaticmethod
    def from_txt(self, filename: str,
                 observable: "ROOT.RooRealVar",
                 weight_name: Optional[str] = None,
                 apply_ghost: bool = False,
                 blind_condition: Optional[ArrayBlindConditionType] = None,
                 name: Optional[str] = None,
                 title: Optional[str] = None) -> "ROOT.RooDataSet":
        ROOT = cached_import("ROOT")
        try:
            arrays = np.loadtxt(filename)
        except FileNotFoundError:
            raise FileNotFoundError(f'File "{filename}" not found.')
        except Exception:
            raise RuntimeError(f'Failed to read data from text file "{filename}".')
        observable_name = observable.GetName()
        if weight_name is None:
            weight_name = self.DEFAULT_WEIGHT_NAME
            assert observable_name != weight_name
        # unweighted data
        if arrays.ndim == 1:
            data = {
                observable_name: arrays,
                weight_name: np.ones(arrays.shape[0])
            }
        # weighted data
        elif (arrays.ndim == 2) and (arrays.shape[1] == 2):
            data = {
                observable_name: arrays[:, 0],
                weight_name: arrays[:, 1]
            }
        else:
            raise RuntimeError(f'Input arrays must have shape (N,) for unweighted data, '
                               f'or (N, 2) for weighted data, but got {arrays.shape}.')
        variables = ROOT.RooArgSet(observable)
        if weight_name not in variables:
            weight_var = ROOT.RooRealVar(weight_name, weight_name, 1)
            variables.add(weight_var)
        name, title = self._resolve_name_title(name, title)
        dataset = self.from_numpy(data,
                                  variables=variables,
                                  weight_name=weight_name,
                                  apply_ghost=apply_ghost,
                                  blind_condition=blind_condition,
                                  name=name,
                                  title=title)
        """
        dataset = ROOT.RooDataSet(dataset_name, dataset_name,
                                  ROOT.RooArgSet(observable, weight_var),
                                  ROOT.RooFit.WeightVar(weight_var))
        if (data.ndim == 1):
            ROOT.RFUtils.FillDataSetValues(dataset, observable, data.data,
                                           data.shape[0])
        elif (data.ndim == 2) and (data.shape[1] == 2):
            ROOT.RFUtils.FillWeightedDataSetValues(dataset, observable,
                                                   data.flatten().data,
                                                   data.shape[0],
                                                   weight_var)
        else:
            raise RuntimeError('invalid file format')
        """
        return dataset
            
    @semistaticmethod
    def from_ntuples(self, filenames: Union[str, List[str]],
                     observable: "ROOT.RooRealVar",
                     treename: Optional[str] = None, 
                     observable_branchname: Optional[str] = None,
                     weight_branchname: Optional[str] = None,
                     selection: Optional[str] = None,
                     weight_name: Optional[str] = None,
                     apply_ghost: bool = False,
                     blind_condition: Optional[ArrayBlindConditionType] = None,
                     name: Optional[str] = None,
                     title: Optional[str] = None) -> "ROOT.RooDataSet":
        from quickstats.interface.root import TChain
        if isinstance(filenames, str):
            filenames = split_str(filenames, sep=',', remove_empty=True)
        chain = TChain(filenames, default_treename=treename)
        observable_name = observable.GetName()
        if weight_name is None:
            weight_name = self.DEFAULT_WEIGHT_NAME
            assert observable_name != weight_name
        dataset = chain.get_dataset(observable=observable,
                                    observable_branchname=observable_branchname,
                                    weight_branchname=weight_branchname,
                                    selection=selection,
                                    weight_name=weight_name,
                                    apply_ghost=apply_ghost,
                                    blind_condition=blind_condition,
                                    name=name,
                                    title=title)
        """
        for filename in filenames:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"file does not exist: {filename}")
            status = chain.AddFile(filename, -1)
            if not status:
                raise RuntimeError(f'cannot find tree "{treename}" in file "{filename}"')
        if cut:
            chain = chain.CopyTree(cut)
        branch = chain.FindBranch(branchname)
        if not branch:
            raise RuntimeError(f'cannot find branch "{branchname}" in tree "{treename}"')
        x = ROOT.RooRealVar(branchname, branchname, observable.getMin(), observable.getMax())
        if weight_branchname is not None:
            weight_branch = chain.FindBranch(weight_branchname)
            if not weight_branch:
                raise RuntimeError(f'cannot find branch "{weight_branchname}" in tree "{treename}"')
            w = ROOT.RooRealVar(weight_branchname, weight_branchname, 1)
            dataset = ROOT.RooDataSet(dataset_name, dataset_name,
                                      ROOT.RooArgSet(x, w),
                                      ROOT.RooFit.Import(chain),
                                      ROOT.RooFit.WeightVar(w))
            if weight_var is not None:
                dataset.weightVar().SetName(weight_var.GetName())
        else:
            dataset = ROOT.RooDataSet(dataset_name, dataset_name,
                                      ROOT.RooArgSet(x),
                                      ROOT.RooFit.Import(chain))
        dataset.get().first().SetName(observable.GetName())
        """
        return dataset

    @semistaticmethod
    def from_histogram(self, histogram: "ROOT.TH1",
                       observable: "ROOT.RooRealVar",
                       weight_name: Optional[str] = None,
                       apply_ghost: bool = False,
                       blind_condition: Optional[ArrayBlindConditionType] = None,
                       name: Optional[str] = None,
                       title: Optional[str] = None) -> "ROOT.RooDataSet":
        ROOT = cached_import("ROOT")
        from quickstats.interface.root import TH1
        py_histogram = TH1(histogram)
        x = py_histogram.bin_center
        y = py_histogram.bin_content
        xmin, xmax = observable.getMin(), observable.getMax()
        mask = ((x >= xmin) & (x <= xmax)) & (y >= 0.)
        x, y = x[mask], y[mask]
        observable_name = observable.GetName()
        if weight_name is None:
            weight_name = self.DEFAULT_WEIGHT_NAME
            assert observable_name != weight_name
        variables = ROOT.RooArgSet(observable)
        if weight_name not in variables:
            weight_var = ROOT.RooRealVar(weight_name, weight_name, 1)
            variables.add(weight_var)        
        data = {
            observable_name: x,
            weight_name: y
        }
        name, title = self._resolve_name_title(name, title)
        dataset = self.from_numpy(data,
                                  variables=variables,
                                  weight_name=weight_name,
                                  apply_ghost=apply_ghost,
                                  blind_condition=blind_condition,
                                  name=name,
                                  title=title)
        return dataset

    @semistaticmethod
    def scale_dataset(
        self,
        dataset: "ROOT.RooDataSet",
        scale_factor: float = 1.0,
        ignore_ghost: bool = True,
        name: Optional[str] = None,
        title: Optional[str] = None
    ) -> "ROOT.RooDataSet":
        variables = dataset.get()
        weight_var = _get_weight_var(dataset)
        data = self.to_numpy(dataset)
        if not weight_var:
            weight_name = self.DEFAULT_WEIGHT_NAME
            assert weight_name not in data
            data[weight_name] = np.ones(np.shape(data[list(data)[0]]))
        else:
            weight_name = weight_var.GetName()
        if ignore_ghost:
            mask = data[weight_name] > CONFIG.ghost_threshold
            data[weight_name][mask] *= scale_factor
        else:
            data[weight_name] *= scale_factor
        name = name or dataset.GetName()
        title = title or dataset.GetTitle()
        scaled_dataset = self.from_numpy(data,
                                         variables=variables,
                                         weight_name=weight_name,
                                         name=dataset.GetName(),
                                         title=dataset.GetTitle())
        return scaled_dataset

    @semistaticmethod
    def bin_dataset(self, dataset: "ROOT.RooDataSet",
                    name: Optional[str] = None,
                    title: Optional[str] = None):
        variables = dataset.get()
        category = self.get_dataset_category(dataset)
        observables = self.get_dataset_observables(dataset)
        if len(observables) == 0:
            raise RuntimeError('No observable found in the dataset')
        data = self.to_numpy(dataset)
        weight_var = _get_weight_var(dataset)
        if weight_var:
            weight_name = weight_var.GetName()
        else:
            weight_var = self.get_default_weight_var()
            variables.add(weight_var)
            weight_name = weight_var.GetName()
            assert weight_name not in data
            data[weight_name] = np.ones(len(data[obseravbles[0].GetName()]))
        binning_map = {}
        nbins_total = 0
        for observable in observables:
            binning = RooRealVar.get_binning(observable)
            binning_map[observable.GetName()] = binning
            nbins_total += binning.nbins
        binned_data = {}
        if category is not None:
            observable_names = [observable.GetName() for observable in observables]
            category_name = category.GetName()
            category_data = data[category_name]
            category_index_map = deduce_category_index_map(data, category_name, observable_names)
            category_indices = []
            index_start = 0
            binned_data[weight_name] = np.zeros(nbins_total)
            for observable in observables:
                observable_name = observable.GetName()
                default_value = RooRealVar.get_default_value(observable)
                observable_binning = binning_map[observable_name]
                nbins = observable_binning.nbins
                category_index = category_index_map[observable_name]
                category_mask = category_data == category_index
                observable_data = data[observable_name][category_mask]
                weight_data = data[weight_name][category_mask]
                hist, bin_edges = np.histogram(observable_data, bins=observable_binning.bin_edges,
                                               weights=weight_data)
                assert np.allclose(bin_edges, observable_binning.bin_edges)
                binned_data[observable_name] = np.full(nbins_total, default_value)
                binned_data[observable.GetName()][index_start : index_start + nbins] = observable_binning.bin_centers
                binned_data[weight_name][index_start : index_start + nbins] = hist
                category_indices.extend([category_index] * nbins)
                index_start =  index_start + nbins
            binned_data[category_name] = np.array(category_indices)
        else:
            if len(observables) != 1:
                raise RuntimeError(f'Dataset with multiple observables but no category is not supported.')
            observable_name = observables[0].GetName()
            observable_data = data[observable_name]
            observable_binning = binning_map[observable_name]
            weight_data = data[weight_name]
            hist, bin_edges = np.histogram(observable_data, bins=observable_binning.bin_edges,
                                           weights=weight_data)
            binned_data[observable_name] = observable_binning.bin_centers
            binned_data[weight_name] = hist
            assert np.allclose(bin_edges, observable_binning.bin_edges)
        name = name or dataset.GetName()
        title = title or dataset.GetTitle()
        binned_dataset = self.from_numpy(binned_data, variables,
                                         weight_name=weight_name,
                                         name=name,
                                         title=title)
        return binned_dataset            
    
    def filter_categories(self, categories:List[str]):
        cat_indices = []
        excluded_categories = []
        excluded_obs  = []
        for category in categories:
            if category not in self.category_map:
                raise ValueError(f'dataset does not contain the category "{category}"')
            cat_index = self.category_map[category]['category_index']
            cat_indices.append(cat_index)
        for category in self.category_map:
            if category not in categories:
                excluded_categories.append(category)
                obs_label = self.category_map[category]['observable']
                excluded_obs.append(obs_label)
        cat_column = self.category.name
        mask = np.isin(self.data[cat_column], cat_indices)
        # clean up observable and category information
        for key in self.data:
            self.data[key] = self.data[key][mask]
        self.observables = [obs for obs in self.observables if obs.name not in excluded_obs]       
        for category in excluded_categories:
            self.category_map.pop(category)
        self.category.category_labels = list(categories)
        # reset category index
        index_map = {}
        for new_index, category in enumerate(categories):
            old_index = self.category_map[category]['category_index']
            index_map[old_index] = new_index
            self.category_map[category]['category_index'] = new_index
        self.data[cat_column] = np.vectorize(index_map.get)(self.data[cat_column])

    @semistaticmethod
    def split_dataset(self, dataset: "ROOT.RooDataSet") -> List["ROOT.RooDataSet"]:
        ROOT = cached_import('ROOT')
        variables = dataset.get()
        category = self.get_dataset_category(dataset)
        observables = self.get_dataset_observables(dataset)
        data = self.to_numpy(dataset)
        weight_var = _get_weight_var(dataset)
        if weight_var:
            weight_name = weight_var.GetName()
        else:
            weight_name = None
        result = []
        if category is None:
            variables = ROOT.RooArgSet(*observables)
            dataset_i = self.from_numpy(data,
                                        variables=variables,
                                        weight_name=weight_name,
                                        name=dataset.GetName(),
                                        title=dataset.GetTitle())
            result.append(dataset_i)
        else:
            category_name = category.GetName()
            observable_names = [observable.GetName() for observable in observables]
            category_data = data[category_name]
            category_index_map = deduce_category_index_map(data, category_name, observable_names)
            for observable in observables:
                split_data = {}
                observable_name = observable.GetName()
                category_index = category_index_map[observable_name]
                category_mask = category_data == category_index
                split_data[observable_name] = data[observable_name][category_mask]
                if weight_name is not None:
                    split_data[weight_name] = data[weight_name][category_mask]
                variables = ROOT.RooArgSet(observable)
                category.setIndex(category_index)
                category_label = category.getLabel()
                name = f'{dataset.GetName()}_{category_label}'
                title = f'{dataset.GetTitle()}_{category_label}'
                dataset_i = self.from_numpy(split_data,
                                            variables=variables,
                                            weight_name=weight_name,
                                            name=name,
                                            title=title)
                result.append(dataset_i)
        return result        
            
    def generate_toy_dataset(self, n_toys:int=1,
                             seed:Optional[int]=None,
                             event_seed:Optional[Dict]=None,
                             add_ghost:bool=True,
                             name_fmt:str="{name}_toy_{index}",
                             title_fmt:str="{title}_toy_{index}"):
        from quickstats.maths.statistics_jitted import random_poisson_elementwise_seed
        ROOT = cached_import("ROOT")
        cat_data = {}
        weight_name = self.weight.name
        for category in self.category_map:
            cat_data[category] = self.get_category_data(category,
                                                        remove_ghost=True,
                                                        sort=True)
            unbinned = (cat_data[category][weight_name] == 1).all()
            if not unbinned:
                raise RuntimeError('cannot generate toy dataset from binned data')
        variables = ROOT.RooArgSet()
        for observable in self.observables:
            variables.add(observable.new())
        variables.add(self.category.new())
        
        if seed is not None:
            np.random.seed(seed)
        
        for i in range(n_toys):
            toy_data = {}
            for category in self.category_map:
                toy_data[category] = {}
                obs_name = self.category_map[category]['observable']
                obs_values = cat_data[category][obs_name]
                if event_seed is not None:
                    if category not in event_seed:
                        raise ValueError(f'no event seed defined for the category: {category}')
                    cat_event_seed = np.array(event_seed[category])
                    if cat_event_seed.shape != obs_values.shape:
                        raise ValueError('number of event seeds in a category must match '
                                         'the number of events in the category dataset')
                    cat_event_seed = cat_event_seed + i
                    pois_weights = random_poisson_elementwise_seed(cat_event_seed, 1).flatten()
                else:
                    pois_weights = np.random.poisson(size=cat_data[category][weight_name].shape)
                toy_data[category][obs_name] = np.repeat(obs_values, pois_weights)
                toy_data[category][weight_name] = np.ones(toy_data[category][obs_name].shape)
            name  = name_fmt.format(name=self.name, index=(i+1))
            if title_fmt is None:
                title = name
            else:
                title = title_fmt.format(title=self.title, index=(i+1))
            toy_dataset_i = self.from_category_data(toy_data, variables,
                                                    name=name, title=title,
                                                    weight_name=weight_name,
                                                    add_ghost=add_ghost,
                                                    ghost_weight=self.ghost_weight)
            yield toy_dataset_i