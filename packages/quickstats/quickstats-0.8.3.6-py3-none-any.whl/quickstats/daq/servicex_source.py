from typing import Union, List, Optional, Dict
import os
import uuid

from .remote_data_source import RemoteDataSource

from quickstats.utils.common_utils import combine_dict
from quickstats.maths.numerics import get_nbatch

class ServiceXSource(RemoteDataSource):
    
    DEFAULT_RESOLVE_OPTIONS = {
        "expand_local_dir" : True,
        "expand_remote_dir" : True,
        "reduce_local" : False,
        "check_local_exists" : True,
        "check_remote_exists" : False,
        "remove_duplicates" : False,
        "abspath" : True,
        "strict_naming" : False,
        "strict_format" : True,
        "strict_format_remote" : True,
        "raise_on_error" : False
    }

    def __init__(self, cachedir: Optional[str] = None,
                 local_cache: bool = False,
                 file_resolve_options: Optional[Dict] = None,
                 columns:Optional[List[str]]=None,
                 server:str="servicex-uc-af",
                 delivery:str="LocalCache",
                 verbosity: Union[int, str] = "INFO"):
        super().__init__(cachedir=cachedir,
                         local_cache=local_cache,
                         file_resolve_options=file_resolve_options,
                         verbosity=verbosity)
        self.columns = columns
        self.server = server
        self.delivery = delivery

    @staticmethod
    def _get_batched_files(filenames:List[str], batchsize:Optional[int]=None):
        nfiles = len(filenames)
        if batchsize is None:
            batchsize = nfiles
            nbatch = 1
        else:
            nbatch = get_nbatch(nfiles, batchsize)

        files = {}
        for i in range(nbatch):
            name = uuid.uuid1().hex
            sample_files = filenames[i * batchsize : (i + 1) * batchsize]
            files[name] = sample_files
        return files

    def deliver(self, batchsize:Optional[int]=None, retry:int=5,
                ignore_failure:bool=False) -> List[str]:
        resolve_options = self.file_resolve_options.copy()
        resolve_options['split_local_remote'] = True

        local_paths, remote_paths = self.resolve_paths(self.data_source,
                                                       **resolve_options)

        from quickstats.interface.servicex import get_template_spec, servicex_config, get_hash_path
        from servicex.servicex_client import deliver
        
        nfiles = len(remote_paths)
        files = self._get_batched_files(remote_paths, batchsize)
        kwargs = {
            "files": files,
            "columns": self.columns,
            "server": self.server,
            "delivery": self.delivery,
            "ignore_local_cache": not self.local_cache
        }
        
        cache_path_backup = servicex_config.cache_path
        servicex_config.set_cache_path(self.cachedir)

        delivered_files = []
        for i in range(retry):
            spec = get_template_spec(**kwargs)
            result = deliver(spec)
            delivered_files = [subfile for subfiles in result.values() for subfile in subfiles]
            if (len(delivered_files) == nfiles):
                break
            nmissing = nfiles - len(delivered_files)
            self.stdout.warning(f"Failed to deliver {nmissing} out of {nfiles} outputs.")
            if ignore_failure:
                break
            if i + 1 < retry:
                self.stdout.info(f"Retrying (Attempt {i+1} / {retry}).")
                kwargs["ignore_local_cache"] = False
                continue
            raise RuntimeError("Failed to deliver all outputs. Maximum retry reached.")
        servicex_config.set_cache_path(cache_path_backup)
        
        paths = local_paths + delivered_files
        return paths

    def clear_cache(self):
        from quickstats.interface.servicex import servicex_config
        servicex_config.clear_cache(self.cachedir)