from typing import Union, List, Optional, Dict
import os
import re
import glob
import tempfile
from itertools import filterfalse, compress
from pathlib import Path

from quickstats import AbstractObject
from quickstats.utils.common_utils import remove_duplicates as remove_duplicate_paths
from quickstats.utils.common_utils import list_diff, combine_dict
from quickstats.utils.path_utils import (
    is_remote_path, split_uri, get_local_path,
    local_path_exists, remote_path_exists,
    listdir, remote_isdir, remote_listdir,
    remote_glob
)

ROOT_FILE_PATTERN = re.compile(r"^.+\.root(?:\.\d+)?$")

DEFAULT_CACHE_DIR = "/tmp/${USER}"

def is_valid_root_filename(filename:str):
    return ROOT_FILE_PATTERN.match(filename) is not None

class RemoteDataSource(AbstractObject):

    DEFAULT_RESOLVE_OPTIONS = {}

    def __init__(self, cachedir: Optional[str] = None,
                 local_cache: bool = False,
                 file_resolve_options: Optional[Dict] = None,
                 verbosity: Union[int, str] = "INFO"):
        super().__init__(verbosity=verbosity)
        self.cachedir = cachedir
        self.local_cache = local_cache
        self.file_resolve_options = combine_dict(self.DEFAULT_RESOLVE_OPTIONS,
                                                 file_resolve_options)
        self.data_source = []
        
    @property
    def cachedir(self) -> str:
        return self._cachedir

    @cachedir.setter
    def cachedir(self, value: Optional[str]):
        self._cachedir = self.resolve_cachedir(value)

    @staticmethod
    def resolve_cachedir(dirname: Optional[str] = None) -> str:
        """Resolve and create the cache directory."""
        if not dirname:
            dirname = DEFAULT_CACHE_DIR
    
        path = os.path.expandvars(os.path.expanduser(dirname))
        p = Path(path)
    
        if len(p.parts) > 1 and p.parts[1] == "tmp":
            p = Path(tempfile.gettempdir()) / Path(*p.parts[2:])

        p.mkdir(parents=True, exist_ok=True)
        return p.as_posix()

    def get_cache_path(self, path:str):
        return None

    def local_cache_exists(self, path:str):
        cache_path = self.get_cache_path(path)
        return cache_path and os.path.exists(cache_path)

    def resolve_paths(self, paths:Union[str, List[str]],
                      expand_local_dir:bool=False,
                      expand_remote_dir:bool=False,
                      reduce_local:bool=True,
                      reduce_cache:bool=True,
                      check_local_exists:bool=True,
                      check_remote_exists:bool=False,
                      remove_duplicates:bool=True,
                      abspath:bool=True,
                      strict_naming:bool=True,
                      strict_format:bool=True,
                      strict_format_remote:bool=False,
                      raise_on_error:bool=True,
                      split_local_remote:bool=False):
        paths = [paths] if isinstance(paths, str) else paths
        if remove_duplicates:
            paths = remove_duplicate_paths(paths)        
        local_paths = []
        remote_paths = []

        for path in paths:
            if is_remote_path(path):
                # need to resolve wildcards
                if "*" in path:
                    subpaths = remote_glob(path)
                else:
                    subpaths = [path]
                for subpath in subpaths:
                    if reduce_local and local_path_exists(subpath):
                        local_paths.append(get_local_path(subpath))
                    elif reduce_cache and self.local_cache_exists(subpath):
                        local_paths.append(self.get_cache_path(subpath))
                    else:
                        remote_paths.append(subpath)
            elif "*" in path:
                local_paths.extend(glob.glob(path))
            else:
                local_paths.append(path)

        if check_local_exists:
            valid_paths = list(filter(os.path.exists, local_paths))
            missing_paths = list_diff(local_paths, valid_paths)
            if missing_paths:
                self.stdout.warning("Local path does not exist:\n" + "\n".join(missing_paths))
            local_paths = valid_paths
  
        if check_remote_exists:
            valid_paths = list(filter(remote_path_exists, remote_paths))
            missing_paths = list_diff(remote_paths, valid_paths)
            if missing_paths:
                self.stdout.warning("Remote path does not exist:\n" + "\n".join(missing_paths))
            remote_paths = valid_paths
      
        if expand_local_dir:
            expanded_local_paths = []
            for path in local_paths:
                if os.path.isdir(path):
                    expanded_local_paths.extend(listdir(path))
                else:
                    expanded_local_paths.append(path)
            local_paths = expanded_local_paths

        if expand_remote_dir:
            expanded_remote_paths = []
            for path in remote_paths:
                if remote_isdir(path):
                    expanded_remote_paths.extend(remote_listdir(path))
                else:
                    expanded_remote_paths.append(path)
            remote_paths = expanded_remote_paths

        if remove_duplicates:
            local_paths = remove_duplicate_paths(local_paths)
            remote_paths = remove_duplicate_paths(remote_paths)

        if strict_naming:
            valid_local_paths = list(filter(is_valid_root_filename, local_paths))
            valid_remote_paths = list(filter(is_valid_root_filename, remote_paths))
            invalid_paths = list_diff(local_paths, valid_local_paths) + list_diff(remote_paths, valid_remote_paths)
            if invalid_paths:
                self.stdout.warning("Invalid naming of root files:\n" + "\n".join(invalid_paths))

        if strict_format and local_paths:
            from quickstats.utils.root_utils import is_corrupt
            # only check local files
            corrupted_files = list(filter(is_corrupt, local_paths))
            if corrupted_files:
                msg = 'Found empty/currupted file(s):\n' + '\n'.join(corrupted_files)
                if raise_on_error:
                    raise RuntimeError(msg)
                else:
                    self.stdout.error(msg)
                local_paths = list_diff(local_paths, corrupted_files)
                
        if strict_format_remote and remote_paths:
            from quickstats.interface.root.helper import switch_error_ignore_level
            from quickstats.utils.common_utils import execute_multi_tasks
            from quickstats.utils.root_utils import is_corrupt
            with switch_error_ignore_level():
                results = execute_multi_tasks(is_corrupt, remote_paths, parallel=-1)
                corrupted_files = list(compress(remote_paths, results))
            if corrupted_files:
                msg = 'Found empty/currupted file(s):\n' + '\n'.join(corrupted_files)
                if raise_on_error:
                    raise RuntimeError(msg)
                else:
                    self.stdout.error(msg)
                remote_paths = list_diff(remote_paths, corrupted_files)

        if abspath:
            local_paths = [os.path.abspath(path) for path in local_paths]

        return (local_paths, remote_paths) if split_local_remote else local_paths + remote_paths

    def get_resolved_paths(self, paths:Union[str, List[str]]):
        return self.resolve_paths(paths, **self.file_resolve_options)

    def add_files(self, paths:Union[str, List[str]]):
        paths = [paths] if isinstance(paths, str) else paths
        self.data_source.extend(paths)    

    def clear(self):
        self.data_source = []