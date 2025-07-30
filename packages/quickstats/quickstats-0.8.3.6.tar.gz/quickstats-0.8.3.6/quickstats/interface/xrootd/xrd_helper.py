import os
from typing import List, Optional, Union
from XRootD.client import CopyProcess

from quickstats import AbstractObject, semistaticmethod, timer

class XRDHelper(AbstractObject):

    def __init__(self, verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)

    @staticmethod
    def get_nbytes(paths:List[str]):
        pass        

    #https://xrootd.slac.stanford.edu/doc/python/xrootd-python-0.1.0/modules/client/copyprocess.html
    @semistaticmethod
    def copy_files(self, src:List[str], dst:List[str], force:bool=False, **kwargs):
        self.stdout.info(f'Copying remote file(s):\n' + '\n'.join(src))
        self.stdout.info(f'Destination(s):\n' + '\n'.join(dst))
        with timer() as t:
            copy_process = CopyProcess()
            for src_i, dst_i in zip(src, dst):
                copy_process.add_job(src_i, dst_i, force=force, **kwargs)
            copy_process.prepare()
            copy_process.run()
        self.stdout.info(f"Copy finished. Total time taken: {t.interval:.3f}s.")

    @semistaticmethod
    def copy_file_cli(self, src:str, dst:str, recursive:bool=False,
                      force:bool=False, allow_http:bool=False, pbar:bool=True,
                      retry:Optional[int]=None, silent:bool=False):
        options = []
        if allow_http:
            options.append("--allow-http")
        if force:
            options.append("--force")
        if not pbar:
            options.append("--nopbar")
        if recursive:
            options.append("--recursive")
        if retry is not None:
            options.append(f"--retry {retry}")
        if silent:
            options.append("--silent")
        options = " ".join(options)
        cmd = f"xrdcp {options} {src} {dst}"
        os.system(cmd)
            
    @semistaticmethod
    def copy_files_cli(self, src:List[str], dst:List[str], recursive:bool=False,
                       force:bool=False, allow_http:bool=False, pbar:bool=True,
                       retry:Optional[int]=None, silent:bool=False):
        self.stdout.info(f'Copying remote file(s):\n' + '\n'.join(src))
        self.stdout.info(f'Destination(s):\n' + '\n'.join(dst))
        with timer() as t:
            for src_i, dst_i in zip(src, dst):
                self.copy_file_cli(src_i, dst_i, recursive=recursive,
                                   force=force, allow_http=allow_http,
                                   pbar=pbar, retry=retry, silent=silent)
        self.stdout.info(f"Copy finished. Total time taken: {t.interval:.3f}s.")