from typing import Optional, Union, List, Dict
from inspect import getsource
import os

from tinydb import TinyDB
from servicex import ServiceXSpec, General, Sample
from servicex.minio_adapter import MinioAdapter

from .config import servicex_config

__all__ = ["get_template_query_str", "get_template_spec", "get_hash_path", "clear_cache", "fix_cache"]

def run_query(input_filename=None):
    import awkward as ak
    import uproot
    import fnmatch
    f = uproot.open({input_filename: None})
    treenames = [key for key in f.keys() if (f[key].classname == 'TTree') and (f[key].num_entries > 1)]
    if not treenames:
        raise RuntimeError('no tree found in the root file')
    elif len(treenames) > 1:
        raise RuntimeError(f'found multiple trees with entries > 1 : {", ".join(treenames)}')
    treename = treenames[0]
    tree = uproot.open({input_filename: treename})
    all_columns = [col.split("/")[-1] for col in tree.keys()]
    referenced_columns = _REFERENCE_COLUMNS_
    required_columns = []
    for column in all_columns:
        if any(fnmatch.fnmatch(column, ref_column) for ref_column in referenced_columns):
            required_columns.append(column)
    return tree.arrays(required_columns)
    
def get_template_query_str(columns:List[str]=None):
    if columns is None:
        columns = ["*"]
    columns = sorted(columns)
    query_str = getsource(run_query).replace("_REFERENCE_COLUMNS_", str(columns))
    return query_str

def get_template_spec(files:Dict[str, List[str]],
                      columns:Optional[List[str]]=None,
                      server:str="servicex-uc-af",
                      delivery:str="LocalCache",
                      ignore_local_cache:bool=False):
    general = General(ServiceX=server,
                      Codegen="python",
                      OutputFormat="root-file",
                      Delivery=delivery)
    query_str = get_template_query_str(columns)
    sample_kwargs = {
        "Function": query_str,
        "IgnoreLocalCache": ignore_local_cache
    }
    samples = []
    for name, sample_files in files.items():
        sample = Sample(Name=name,
                        XRootDFiles=sample_files,
                        **sample_kwargs)
        samples.append(sample)
    spec = ServiceXSpec(General=general,
                        Sample=samples)
    return spec

def get_hash_path(path:str):
    return MinioAdapter.hash_path(path)

def clear_cache():
    cache_db_path = servicex_config.get_cache_db_path()
    if cache_db_path is None:
        return None
    db = TinyDB(db_path)
    db.truncate()
    db.close()

def fix_cache():
    cache_db_path = servicex_config.get_cache_db_path()
    if cache_db_path is None:
        return None
    from quickstats.interface.tinydb.methods import remove_non_unique_field_values
    remove_non_unique_field_values(cache_db_path)