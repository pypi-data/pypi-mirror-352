from .filesystem import split_uri, get_filesystem

def _call_path_method(method:str, path:str, **kwargs):
    domain, path = split_uri(path)
    filesystem = get_filesystem(domain)
    if not hasattr(filesystem, method):
        raise ValueError(f'not implemented method: {method}')
    return getattr(filesystem, method)(path, **kwargs)

def listdir(path:str, **kwargs):
    return _call_path_method('listdir', path, **kwargs)

def mkdir(path:str, **kwargs):
    return _call_path_method('mkdir', path, **kwargs)

def ls(path:str, nourl:bool=False, **kwargs):
    return _call_path_method('ls', path, nourl=nourl, **kwargs)

def rmdir(path:str, **kwargs):
    return _call_path_method('rmdir', path, **kwargs)

def rm(path:str, **kwargs):
    return _call_path_method('rm', path, **kwargs)

def isdir(path:str, **kwargs):
    return _call_path_method('isdir', path, **kwargs)

def exists(path:str, **kwargs):
    return _call_path_method('exists', path, **kwargs)

def glob(path:str, nourl:bool=False, **kwargs):
    return _call_path_method('glob', path, nourl=nourl, **kwargs)

def stat(path:str, **kwargs):
    return _call_path_method('stat', path, **kwargs)