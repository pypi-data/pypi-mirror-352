import os
import sys
import glob

from typing import List, Union, Optional
from pathlib import Path

if sys.version_info[0] > 2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

from .string_utils import split_str

FILESYSTEM_TO = {}

def get_scheme(uri: str) -> Optional[str]:
    """
    Extracts and returns the scheme (protocol) part of a given URI.
    
    Parameters:
        uri (str): The URI from which to extract the scheme.
    
    Returns:
        Optional[str]: The scheme of the URI, or None if no scheme is found or input is invalid.
    """
    # Precompile the regex pattern to improve performance when the function is called multiple times
    pattern = re.compile(r"^([a-zA-Z][a-zA-Z\d+\-.]*):")  # Improved pattern based on RFC 3986
    match = pattern.match(uri)
    return match.group(1) if match else None

def has_scheme(uri: str) -> Optional[bool]:
    return get_scheme(uri) is not None

def split_uri(uri):
    parsed_uri = urlparse(uri)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    path = parsed_uri.path
    if path.startswith("//"):
        path = path[1:]
    # in case of multiple domains
    if ("://" in path ) and path.startswith("/"):
        path = path.lstrip("/")
    return domain, path

def is_remote_path(path:str):
    return "://" in path

def is_xrootd_path(path:str):
    return "root://" in path

def get_local_path(path:str):
    if not is_remote_path(path):
        return path
    host, path = split_uri(path)
    return get_local_path(path)

def remote_path_exists(path:str, timeout:int=0):
    from quickstats.interface.xrootd.path import exists
    return exists(path, timeout=timeout)

def remote_glob(path:str):
    from quickstats.interface.xrootd.path import glob as remote_glob
    return remote_glob(path)

def remote_isdir(dirname:str, timeout:int=0): 
    from quickstats.interface.xrootd.path import isdir
    return isdir(dirname, timeout=timeout)

def remote_listdir(dirname:str):
    from quickstats.interface.xrootd.path import glob as remote_glob
    return remote_glob(os.path.join(dirname, "*"))

def listdir(dirname:str):
    return glob.glob(os.path.join(dirname, "*"))

def local_path_exists(path:str):
    if os.path.exists(path):
        return True
    if is_xrootd_path(path):
        host, path = split_uri(path)
        return local_path_exists(path)
    return False
    
def resolve_paths(paths:Union[str, List[str]],
                  sep:str=","):
    if isinstance(paths, str):
        paths = split_str(paths, sep=sep, strip=True, remove_empty=True)
        return resolve_paths(paths, sep=sep)
    resolved_paths = []
    for path in paths:
        if "*" in path:
            if is_remote_path(path):
                from quickstats.interface.xrootd.path import glob
                glob_paths = glob(path)
            else:
                glob_paths = glob.glob(path)
            resolved_paths.extend(glob_paths)
        else:
            resolved_paths.append(path)
    return resolved_paths