from typing import Optional, Union
import sys
if sys.version_info[0] > 2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

from quickstats import AbstractObject, timer
from XRootD.client import FileSystem as XRootDFileSystem
from XRootD.client.flags import StatInfoFlags
from  XRootD.client import glob_funcs

FILESYSTEMS = {}

__all__ = ["FileSystem", "get_filesystem"]

def split_uri(uri):
    parsed_uri = urlparse(uri)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    path = parsed_uri.path
    if path.startswith("//"):
        path = path[1:]
    return domain, path

class FileSystem(AbstractObject):

    def __init__(self, url:str,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.url = url
        self.filesystem = XRootDFileSystem(url)
        self.triggered = False
        self.sanity_check()
        
    def __getattr__(self, name:str):
        def method(*args, **kwargs):
            return self._run_query(name, *args, **kwargs)
        return method

    def _run_query(self, method:str, *args, **kwargs):
        suppress_error = kwargs.pop("suppress_error", False)
        if not hasattr(self.filesystem, method):
            raise ValueError(f'XRootD FileSystem does not contain the method "{method}".')
        if not self.triggered:
            self.stdout.info(f'Initializing XRootD query to the server {self.url}. '
                             f'Network traffic overhead might be expected.')
        with timer() as t:
            status, result = getattr(self.filesystem, method)(*args, **kwargs)
        # print the time taken for the first time
        if not self.triggered:
            self.stdout.info(f"Query completed in {t.interval:.2f}s.")
            self.triggered = True
        if not suppress_error:
            self._process_status(status, method)
        return status, result

    def _process_status(self, status, name:str):
        if status.error:
            self.stdout.warning(f'Query "{name}" responded with error status. Message: {status.message}')

    def sanity_check(self):
        if "root://" in self.url:
            from quickstats.interface.kerberos import list_service_principals
            service_principals = list_service_principals()
            if not any("CERN.CH@CERN.CH" in principal for principal in service_principals):
                self.stdout.warning("No kerberos ticket found for CERN.CH. "
                                    "XRootD might not work properly.")
                if service_principals:
                    self.stdout.warning("Available kerberos service principals:\n" +
                                        "\n".join(sercice_principals))
            else:
                self.stdout.info("Found valid kerberos ticket for CERN.CH.")

    def copy(self, source:str, target:str, force=False):
        return self._run_query('copy', source, target, force=force)
        
    def listdir(self, path:str, timeout=0, **kwargs):
        status, result = self._run_query('dirlist', path, timeout=timeout, **kwargs)
        if status.error:
            return []
        return [dir_.name for dir_ in result.dirlist]

    def stat(self, path:str, timeout=0, **kwargs):
        return self._run_query('stat', path, timeout=timeout, **kwargs)

    def size(self, path:str, timeout=0, **kwargs):
        status, result = self.stat(path, timeout=timeout, suppress_error=True)
        if status.error:
            return None
        return result.size
    
    def exists(self, path:str, timeout=0):
        status, result = self.stat(path, timeout=timeout, suppress_error=True)
        return not status.error

    def isdir(self, path:str, timeout=0, **kwargs):
        status, result = self.stat(path, timeout=timeout, suppress_error=True)
        return (not status.error) and (result.flags & StatInfoFlags.IS_DIR) != 0

    def isreadable(self, path:str, timeout=0, **kwargs):
        status, result = self.stat(path, timeout=timeout, suppress_error=True)
        return (not status.error) and (result.flags & StatInfoFlags.IS_READABLE) != 0

    def iswritable(self, path:str, timeout=0, **kwargs):
        status, result = self.stat(path, timeout=timeout, suppress_error=True)
        return (not status.error) and (result.flags & StatInfoFlags.IS_WRITABLE) != 0

    def glob(self, path:str, nourl:bool=True, **kwargs):
        url = self.url
        if not url.endswith('/'):
            url += '/'
        result =  glob_funcs.glob(url + path)
        if nourl:
            return [p.replace(self.url, "").replace("//", "/") for p in result]
        return result

    def ls(self, path:str, nourl:bool=True, **kwargs):
        if "*" in path:
            return self.glob(path, nourl=nourl, **kwargs)
        timeout = kwargs.get("timeout", 0)
        status, result = self.stat(path, timeout=timeout)
        if status.error:
            return []
        if result.flags & StatInfoFlags.IS_DIR:
            return self.listdir(path, **kwargs)
        return [path]
        
    def mv(self, source:str, dest:str, timeout=0, **kwargs):
        return self._run_query('mv', source, dest, timeout=timeout, **kwargs)

    def rm(self, path:str, timeout=0, **kwargs):
        return self._run_query('rm', path, timeout=timeout, **kwargs)

    def mkdir(self, path:str, timeout=0, **kwargs):
        return self._run_query('mkdir', path, timeout=timeout, **kwargs)

    def rmdir(self, path:str, timeout=0, **kwargs):
        return self._run_query('rmdir', path, timeout=timeout, **kwargs)
    
def get_filesystem(url:str):
    """
    Parameters: url (string) – The URL of the server to connect with
    """
    url = url.rstrip("/")
    if url in FILESYSTEMS:
        return FILESYSTEMS[url]
    filesystem = FileSystem(url)
    # caching the filesystem instance
    FILESYSTEMS[url] = filesystem
    return filesystem