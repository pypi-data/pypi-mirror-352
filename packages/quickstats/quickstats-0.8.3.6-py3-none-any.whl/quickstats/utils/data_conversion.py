from typing import Union, Optional, Dict, List, Sequence
import os
import re
import glob
import uuid

import numpy as np

import quickstats
from quickstats import DescriptiveEnum, module_exists, cached_import

root_datatypes = ["bool", "Bool_t", "Byte_t", "char", "char*", "Char_t", 
                  "double", "Double32_t", "Double_t", "float",
                  "Float16_t", "Float_t", "int", "Int_t", 
                  "long", "long long", "Long_t", "Long64_t",
                  "short", "Short_t", "Size_t", "UChar_t",
                  "UInt_t", "ULong64_t", "ULong_t",
                  "unsigned", "unsigned char", "unsigned int",
                  "unsigned long", "unsigned long long",
                  "unsigned short", "UShort_t", "ROOT::VecOps::RVec<Char_t>"]

uproot_datatypes = ["bool", "double", "float", "int", "int8_t", "int64_t", "char*", "int32_t", "uint64_t", "uint32_t"]

class ConversionMode(DescriptiveEnum):
    ALL = (0, "Convert all variable types")
    REMOVE_NON_STANDARD_TYPE = (1, "Remove variables of non-standard type (i.e. other than bool, int, float, str, etc.)")
    REMOVE_NON_ARRAY_TYPE = (2, "Remove variables of non-standard type or not convertible to array of standard type")

def get_default_library(custom_columns:bool=False):
    if custom_columns:
        return "root"
    try:
        import uproot
        has_uproot = True
        from packaging import version
        uproot_version = uproot.__version__
        if version.parse(uproot_version) < version.parse("4.2.0"):
            print("WARNING: uproot version too old (<4.2.0), will switch to using ROOT instead")
            has_uproot = False
    except ImportError:
        has_uproot = False
    if has_uproot:
        return "uproot"
    return "root"

def downcast_dataframe(df):
    import pandas as pd
    fcols = df.select_dtypes('float').columns
    icols = df.select_dtypes('integer').columns

    df[fcols] = df[fcols].apply(pd.to_numeric, downcast='float')
    df[icols] = df[icols].apply(pd.to_numeric, downcast='integer')

def array2root(array_data:Dict[str, np.ndarray], filename:str, treename:str,
               library:str="auto", multithread:bool=True):
    if library.lower() == "auto":
        library = get_default_library()
    if library == "root":
        from quickstats.interface.root.helper import RMultithreadEnv
        from quickstats.interface.cppyy.vectorize import np_type_str_maps
        with RMultithreadEnv(multithread):
            columns = list(array_data.keys())
            snapshot_templates = []
            for column in columns:
                template_type = np_type_str_maps.get(array_data[column].dtype, None)
                if template_type is None:
                    raise ValueError(f"unsupported array type \"{array_data[column].dtype}\""
                                     f" from the column \"{column}\"")
                if template_type == "bool":
                    template_type = "int"
                    array_data[column] = array_data[column].astype("int32")
                snapshot_templates.append(template_type)
            snapshot_templates = tuple(snapshot_templates)
            ROOT = cached_import("ROOT")
            if quickstats.root_version >= (6, 28, 0):
                df = ROOT.RDF.FromNumpy(array_data)
            else:
                df = ROOT.RDF.MakeNumpyDataFrame(array_data)
            df.Snapshot.__getitem__(snapshot_templates)(treename, filename, columns)
    elif library == "uproot":
        import uproot
        from packaging import version
        uproot_version = uproot.__version__
        if version.parse(uproot_version) < version.parse("4.2.0"):
            raise RuntimeError("uproot version too old (requires 4.2.0+)")
        file = uproot.recreate(filename)
        file[treename] = array_data
        file.close()
    else:
        raise RuntimeError(f'unknown library "{library}" for root data conversion')            
        
numpy2root = array2root

def dataframe2numpy(df:"pandas.DataFrame", columns:Optional[List[str]]=None):
    if columns is not None:
        arrays = dict(zip(columns, df[columns].to_numpy().T))
    else:
        arrays = dict(zip(df.columns.values, df.to_numpy().T))
    for column in arrays:
        arrays[column] = arrays[column].astype(df[column].dtype)
    return arrays 

def numpy2dataframe(array_data:Dict[str, np.ndarray]):
    array_shallow_copy = {**array_data}
    for key, array in array_data.items():
        if (array.ndim > 1) and (array.dtype != object):
            array_shallow_copy[key] = list(array)
    import pandas as pd
    df = pd.DataFrame(array_shallow_copy)
    return df

array2dataframe = numpy2dataframe

def dataframe2root(df:"pandas.DataFrame", filename:str, treename:str,
                   columns:Optional[List[str]]=None,
                   library:str="auto", multithread:bool=True):
    array_data = dataframe2numpy(df, columns)
    array2root(array_data, filename, treename, library=library,
               multithread=multithread)
    
def uproot_get_standard_columns(uproot_tree):
    typenames = uproot_tree.typenames()
    columns = list(typenames.keys())
    column_types = list(typenames.values())
    return np.array(columns)[np.where(np.isin(column_types, uproot_datatypes))]

def get_rdf_column_type(rdf, column_name:str):
    if hasattr(rdf, "GetColumnType"):
        GetColumnType = rdf.GetColumnType
    # case distributed dataframe
    else:
        GetColumnType = rdf._headnode._localdf.GetColumnType
    try:
        column_type = GetColumnType(column_name)
    except Exception:
        column_type = ""
    return column_type

def reduce_vector_types(column_types:List[str]):
    reduced_column_types = []
    vec_expr1 = re.compile(r"ROOT::VecOps::RVec<([ \w]+)>")
    vec_expr2 = re.compile(r"vector<([ \w]+)>")
    def match(pattern, string):
        result = pattern.match(string)
        if result:
            return result.group(1)
        return string
    for column_type in column_types:
        if column_type.startswith("ROOT::VecOps::RVec"):
            reduced_column_types.append(match(vec_expr1, column_type))
        elif column_type.startswith("vector"):
            reduced_column_types.append(match(vec_expr2, column_type))
        else:
            reduced_column_types.append(column_type)
    reduced_column_types = np.array(reduced_column_types)
    return reduced_column_types


def make_iter_result(results, downcast:bool=False):
    if downcast:
        for result in results:
            downcast_dataframe(result)
            yield result
    for result in results:
        yield result
        
def iterate_uproot(files:List[str], columns:Optional[Union[str, List[str], Dict]]=None,
                   filter_typename=None, step_size:Union[str, int]='100 MB',
                   cut:Optional[str]=None, iterate:bool=False, library:str='numpy',
                   downcast:bool=True):
    import uproot
    assert library in ['numpy', 'pandas']
    if columns is None:
        expressions = None
        aliases = None
    elif isinstance(columns, str):
        expressions = columns
        aliases = None
    elif isinstance(columns, Sequence):
        expressions = list(columns)
        aliases = None
    elif isinstance(columns, dict):
        expressions = list(columns)
        aliases = {k:v for k, v in columns.items() if k != v}
    else:
        raise TypeError('columns must be a string, list of strings or a dictionary')
    results = uproot.iterate(files, expressions=expressions,
                             filter_typename=filter_typename,
                             step_size=step_size,
                             aliases=aliases,
                             cut=cut, library=library)
    if not iterate:
        if library == 'numpy':
            result = {}
            for batch in results:
                for column in batch:
                    if column not in result:
                        result[column] = batch[column]
                    else:
                        result[column] = np.concatenate([result[column], batch[column]])
            return result
        else:
            import pandas as pd
            result = None
            for batch in results:
                if downcast:
                    downcast_dataframe(batch)
                if result is None:
                    result = batch
                else:
                    result = pd.concat([result, batch])
            return result
    else:
        if (library == 'pandas') and (downcast):
            return make_iter_result(results, downcast=True)
        return make_iter_result(results, downcast=False)

def get_columns(filename:str, treename:str):
    if module_exists('uproot'):
        try:
            import uproot
            return list(uproot.open(filename)[treename].keys())
        except:
            pass
    return None
    
def rdf2numpy(rdf, columns:Union[Dict[str, str], List[str]]=None,
              cut:Optional[str]=None, convert_vectors:bool=True,
              mode:Union[str, int, ConversionMode]=1,
              all_columns:Optional[List[str]]=None):
    if all_columns is None:
        all_columns = [str(name) for name in rdf.GetColumnNames()]
    if cut is not None:
        rdf = rdf.Filter(cut)     
    rename_columns = {}
    if columns is None:
        column_names = list(all_columns)
        columns = {}
        for name in column_names:
            if "." in name:
                name_fix = name.replace(".", "_")
                if name_fix not in column_names:
                    columns[name_fix] = name
                else:
                    raise RuntimeError(f'failed to rename column {name} to {name_fix}: column already exists')
            
            else:
                columns[name] = name
    if isinstance(columns, dict):
        save_columns = []
        for column_name, definition in columns.items():
            if column_name == definition:
                save_columns.append(column_name)
                continue
            if column_name in all_columns:
                new_column_name = f"var_{uuid.uuid4().hex}"
                rename_columns[new_column_name] = column_name
                column_name = new_column_name
            if definition in all_columns:
                rdf = rdf.Alias(column_name, definition)
            else:
                rdf = rdf.Define(column_name, definition)
            all_columns.append(column_name)
            save_columns.append(column_name)
    else:
        save_columns = list(columns)
    conversion_mode = ConversionMode.parse(mode)

    if conversion_mode in [ConversionMode.REMOVE_NON_STANDARD_TYPE,
                           ConversionMode.REMOVE_NON_ARRAY_TYPE]:
        column_types = np.array([get_rdf_column_type(rdf, column_name) for column_name in save_columns])
        if conversion_mode == ConversionMode.REMOVE_NON_ARRAY_TYPE:
            column_types = reduce_vector_types(column_types)
        save_columns = list(np.array(save_columns)[np.where(np.isin(column_types, root_datatypes))])
        rename_columns = {k:v for k,v in rename_columns.items() if k in save_columns}
    vector_columns = []
    if convert_vectors:
        vector_columns_tmp = []
        for column_name in save_columns:
            column_type = get_rdf_column_type(rdf, column_name)
            if column_type.count("ROOT::VecOps::RVec") == 1:
                vector_columns_tmp.append(column_name)
        if len(vector_columns_tmp) > 0:
            import quickstats
            quickstats.load_processor_methods()
            for column_name in vector_columns_tmp:
                new_column_name = f"var_{uuid.uuid4().hex}"
                if column_name in save_columns:
                    save_columns = [new_column_name if name == column_name else name for name in save_columns]
                # mapped twice
                if column_name in rename_columns:
                    rename_columns[new_column_name] = rename_columns.pop(column_name)
                else:
                    rename_columns[new_column_name] = column_name
                try:
                    rdf = rdf.Define(new_column_name, f"RVec2Vec({column_name})")
                except Exception:
                    tmp_column_name = f"var_{uuid.uuid4().hex}"
                    rdf = rdf.Alias(tmp_column_name, column_name)
                    rdf = rdf.Define(new_column_name, f"RVec2Vec({tmp_column_name})")
                vector_columns.append(new_column_name)
    available_columns = [str(name) for name in rdf.GetColumnNames()]
    missing_columns = np.setdiff1d(save_columns, available_columns)
    if len(missing_columns) > 0:
        raise RuntimeError(f'missing column(s): {", ".join(missing_columns)}')
    result = None
    #if module_exist('awkward'):
    #    import awkward as ak
    #    if hasattr(ak, 'from_rdataframe'):
    #        result = ak.to_numpy(ak.from_rdataframe(rdf, columns=save_columns))
    if result is None:
        result = rdf.AsNumpy(save_columns)
    for vector_column in vector_columns:
        # not the most efficient way, but easiest
        numpy_array = np.array([np.array(v.data()) for v in result[vector_column]], dtype=object)
        # in case it't array of regular size
        if len(numpy_array) and (numpy_array[0].dtype == object):
            result[vector_column] = np.array([np.array(v.data()) for v in result[vector_column]])
        else:
            result[vector_column] = numpy_array
    for old_column, new_column in rename_columns.items():
        result[new_column] = result.pop(old_column)
    # reorder the columns to match the order given by the user
    if columns is not None:
        result = {column: result[column] for column in columns if column in result}
    return result
    
def root2numpy(filename:Union[str, List[str]], treename:str,
               columns:Union[Dict[str, str], List[str]]=None,
               cut:Optional[str]=None, convert_vectors:bool=True,
               mode:Union[str, int, ConversionMode]=1,
               step_size:Union[str, int]='100 MB', iterate:bool=False,
               library:str="auto", multithread:bool=True):
    if isinstance(filename, str) and os.path.isdir(filename):
        filename = glob.glob(os.path.join(filename, "*.root"))
    conversion_mode = ConversionMode.parse(mode)
    if conversion_mode == ConversionMode.REMOVE_NON_ARRAY_TYPE:
        library = "root"
    if library.lower() == "auto":
        library = get_default_library(custom_columns=isinstance(columns,dict))
    if library.lower() == "root":
        from quickstats.interface.root.helper import RMultithreadEnv
        with RMultithreadEnv(multithread):
            ROOT = cached_import("ROOT")
            rdf = ROOT.RDataFrame(treename, filename)
            all_columns = get_columns(filename, treename=treename)
            return rdf2numpy(rdf, columns=columns, cut=cut,
                             convert_vectors=convert_vectors,
                             mode=mode,
                             all_columns=all_columns)
    elif library.lower() == "uproot":
        import uproot
        if not isinstance(filename, list):
            filename = [filename]
        # iterate over multiple files
        files = {f:treename for f in filename}
        if conversion_mode == ConversionMode.REMOVE_NON_STANDARD_TYPE:
            filter_typename = list(uproot_datatypes)
        else:
            filter_typename = None
        result = iterate_uproot(files, columns=columns,
                                filter_typename=filter_typename,
                                step_size=step_size,
                                cut=cut, library='numpy',
                                iterate=iterate,
                                downcast=False)
        return result
    else:
        raise RuntimeError(f'unknown library "{library}" for root data conversion')

root2array = root2numpy
        
def root2dataframe(filename:Union[str, List[str]], treename:str,
                   columns:Union[Dict[str, str], List[str]]=None,
                   cut:Optional[str]=None,
                   mode:Union[str, int, ConversionMode]=1,
                   downcast:bool=True, iterate:bool=False,
                   step_size:Union[str, int]='100 MB',
                   library:str="auto", multithread:bool=True):
    conversion_mode = ConversionMode.parse(mode)
    if conversion_mode == ConversionMode.REMOVE_NON_ARRAY_TYPE:
        library = "root"    
    if library.lower() == "auto":
        library = get_default_library(custom_columns=isinstance(columns,dict))
    if library.lower() == "root":
        numpy_data = root2numpy(filename, treename, columns=columns, cut=cut,
                                convert_vectors=True,
                                mode=mode,
                                library=library,
                                multithread=multithread)
        result = numpy2dataframe(numpy_data)
        if downcast:
            downcast_dataframe(result)
    elif library.lower() == "uproot":
        import uproot
        if not isinstance(filename, list):
            filename = [filename]
        import pandas as pd
        # iterate over multiple files
        files = {f:treename for f in filename}
        if conversion_mode == ConversionMode.REMOVE_NON_STANDARD_TYPE:
            filter_typename = list(uproot_datatypes)
        else:
            filter_typename = None
        result = iterate_uproot(files, columns=columns,
                                filter_typename=filter_typename,
                                step_size=step_size,
                                cut=cut, library='pandas',
                                iterate=iterate,
                                downcast=False)
    return result

def root2rdataset(filename:Union[str, List[str], "quickstats.PathManager"], treename:str,
                  observable:Union[str, dict, "ROOT.RooRealVar",
                                   "quickstats.interface.root.RooRealVar"],
                  weight_name:Optional[str]=None,
                  dataset_name:str="obsData"):
    from quickstats.components.modelling import TreeDataSource
    source = TreeDataSource(treename, filename, observable, weight_name)
    dataset = source.construct_dataset(dataset_name)
    return dataset

def rdataset2numpy(dataset:"ROOT.RooDataSet"):
    from quickstats.interface.root import RooDataSet
    return RooDataSet.to_numpy(dataset)

def rdataset2dataframe(dataset:"ROOT.RooDataSet"):
    from quickstats.interface.root import RooDataSet
    return RooDataSet.to_pandas(dataset)

def rdataset2hist(dataset:"ROOT.RooDataSet"):
    pass

def root2hist(filename:Union[str, List[str]], treename:str,
              column:str, bins:int=10, range:List[float]=None, weight_column:Optional[str]=None):
    pass