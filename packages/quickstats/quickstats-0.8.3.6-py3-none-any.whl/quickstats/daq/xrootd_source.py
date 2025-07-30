from typing import Union, List, Optional, Dict
import os

from .remote_data_source import RemoteDataSource

from quickstats.utils.path_utils import split_uri, is_remote_path
from quickstats.utils.common_utils import combine_dict, remove_duplicates

class XRootDSource(RemoteDataSource):

    DEFAULT_RESOLVE_OPTIONS = {
        "expand_local_dir" : True,
        "expand_remote_dir" : True,
        "reduce_local" : True,
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
                 localize: bool = False,
                 verbosity: Union[int, str] = "INFO"):
        super().__init__(cachedir=cachedir,
                         local_cache=local_cache,
                         file_resolve_options=file_resolve_options,
                         verbosity=verbosity)
        self.localize = localize

    def get_cache_path(self, path:str):
        if not is_remote_path(path):
            raise ValueError(f'not a remote path: {path}')
        host, filename = split_uri(path)
        filename = filename.lstrip('/.~')
        return os.path.join(self.cachedir, filename)

    def deliver(self, parallel:bool=False, **options) -> List[str]:
        resolve_options = self.file_resolve_options.copy()
        resolve_options['reduce_cache'] = self.local_cache
        resolve_options['split_local_remote'] = True
        local_paths, remote_paths = self.resolve_paths(self.data_source,
                                                       **resolve_options)
        if not self.localize:
            return local_paths + remote_paths
        from quickstats.interface.xrootd import XRDHelper
        helper = XRDHelper(verbosity=self.stdout.verbosity)
        src = remote_paths
        dst = list(map(self.get_cache_path, remote_paths))
        unique_src = remove_duplicates(src)
        unique_dst = remove_duplicates(dst)
        # make local copy
        if parallel:
            helper.copy_files(unique_src, unique_dst, force=not self.local_cache, **options)
        else:
            for src_i, dst_i in zip(unique_src, unique_dst):
                helper.copy_files([src_i], [dst_i], force=not self.local_cache, **options)
        paths = local_paths + dst
        return paths