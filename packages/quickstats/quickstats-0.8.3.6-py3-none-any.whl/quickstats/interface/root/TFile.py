from typing import Optional, Union, List, Dict
import os
import re
import glob

import numpy as np

from quickstats import semistaticmethod, cached_import
from quickstats.utils.path_utils import (resolve_paths, is_remote_path, remote_glob,
                                         remote_isdir, remote_listdir, listdir,
                                         local_path_exists, split_uri,
                                         remote_path_exists)
from quickstats.utils.root_utils import is_corrupt
from quickstats.utils.common_utils import in_notebook
from quickstats.utils.sys_utils import bytes_to_readable
from .TObject import TObject

class TFile(TObject):

    FILE_PATTERN = re.compile(r"^.+\.root(?:\.\d+)?$")

    def __init__(self, source:Union[str, "ROOT.TFile"],
                 **kwargs):
        super().__init__(source=source, **kwargs)

    def initialize(self, source:Union[str, "ROOT.TFile"]):
        self.obj = self._open(source)
        
    @staticmethod
    def is_corrupt(f:Union["ROOT.TFile", str]):
        return is_corrupt(f)

    @semistaticmethod
    def _get_all_treenames(self, source:Union["ROOT.TFile", str]):
        ROOT = cached_import("ROOT")
        if isinstance(source, str):
            source = ROOT.TFile.Open(source)
        keys = [key.GetName() for key in source.GetListOfKeys()]
        objs = [source.Get(key) for key in keys]
        trees = [obj for obj in objs if isinstance(obj, ROOT.TTree)]
        treenames = [tree.GetName() for tree in trees]
        return treenames

    @semistaticmethod
    def _get_main_treename(self, source:Union["ROOT.TFile", str]):
        ROOT = cached_import("ROOT")
        if isinstance(source, str):
            source = ROOT.TFile.Open(source)
        keys = [key.GetName() for key in source.GetListOfKeys()]
        objs = [source.Get(key) for key in keys]
        trees = [obj for obj in objs if isinstance(obj, ROOT.TTree)]
        if not trees:
            raise RuntimeError('No tree found in the root file')
        elif len(trees) == 1:
            return trees[0].GetName()
        main_trees = [tree for tree in trees if tree.GetEntriesFast() > 1]
        main_treenames = [tree.GetName() for tree in main_trees]
        if not main_trees:
            raise RuntimeError('No tree found with entries > 1')
        elif len(main_trees) > 1:
            raise RuntimeError('Found multiple trees with entries > 1 : {names}'.format(
                names=", ".join(main_treenames)))
        return main_treenames[0]           

    @semistaticmethod
    def _is_valid_filename(self, filename:str):
        return self.FILE_PATTERN.match(filename) is not None
    
    @semistaticmethod
    def _requires_protocol(self, filename:str):
        return "://" in filename

    @semistaticmethod
    def _filter_valid_filenames(self, filenames:List[str]):
        filenames = [filename for filename in filenames if self._is_valid_filename(filename)]
        return filenames

    @semistaticmethod
    def _get_cache_path(self, path:str, cachedir:str="/tmp"):
        host, filename = split_uri(path)
        filename = filename.lstrip('/.~')
        cache_path = os.path.join(cachedir, filename)
        return cache_path
    
    @semistaticmethod
    def _resolve_cached_remote_paths(self, paths:List[str],
                                     strict_format:Optional[bool]=True,
                                     cached_only:bool=False):
        ROOT = cached_import("ROOT")
        from quickstats.interface.xrootd import get_cachedir
        cachedir = get_cachedir()
        if cachedir is None:
            return list(paths)
        resolved_paths = []
        for path in paths:
            url = ROOT.TUrl(path)
            # skip local file
            if url.GetProtocol() == "file":
                resolved_paths.append(path)
                continue
            filename = url.GetFile().lstrip("/")
            cache_path = os.path.join(cachedir, filename)
            if os.path.exists(cache_path):
                if os.path.isdir(cache_path):
                    cache_paths = listdir(cache_path)
                    if strict_format:
                        cache_paths = self._filter_valid_filenames(cache_paths)
                    if not cache_paths:
                        if not cached_only:
                            resolved_paths.append(path)
                        continue
                    resolved_paths.extend(cache_paths)
                else:
                    resolved_paths.append(cache_path)
            elif not cached_only:
                resolved_paths.append(path)
        return resolved_paths
                
    @semistaticmethod
    def list_files(self, paths:Union[List[str], str],
                   strict_format:Optional[bool]=True,
                   resolve_cache:bool=False,
                   expand_remote_files:bool=True,
                   raise_on_error:bool=True):
        paths = resolve_paths(paths)
        filenames = []
        
        if resolve_cache:
            paths = self._resolve_cached_remote_paths(paths)
            
        # expand directories if necessary
        for path in paths:
            if is_remote_path(path):
                if local_path_exists(path):
                    host, path = split_uri(path)
                elif remote_path_exists(path):
                    if expand_remote_files and remote_isdir(path):
                        filenames.extend(remote_listdir(path))
                    else:
                        filenames.append(path)
                else:
                    self.stdout.warning(f'Remote file "{path}" does not exist')
            elif os.path.isdir(path):
                filenames.extend(listdir(path))
            elif os.path.exists(path):
                filenames.append(path)
            else:
                self.stdout.warning(f'Local file "{path}" does not exist')
        if strict_format:
            filenames = self._filter_valid_filenames(filenames)
        if not filenames:
            return []
        if resolve_cache:
            filenames = self._resolve_cached_remote_paths(filenames)
        ROOT = cached_import("ROOT")
        invalid_filenames, valid_filenames = [], []
        for filename in filenames:
            if is_remote_path(filename):
                # delay the check of remote root file to when they are open
                valid_filenames.append(filename)
                continue
            try:
                rfile = ROOT.TFile(filename)
                if self.is_corrupt(rfile):
                    invalid_filenames.append(filename)
                else:
                    valid_filenames.append(filename)
            except:
                invalid_filenames.append(filename)
        if invalid_filenames:
            fmt_str = "\n".join(invalid_filenames)
            if raise_on_error:
                raise RuntimeError(f'Found empty/currupted file(s):\n{fmt_str}')
            else:
                self.stdout.warning(f'Found empty/currupted file(s):\n{fmt_str}')
        return valid_filenames
    
    @staticmethod
    def _open(source:Union[str, "ROOT.TFile"]):
        # source is path to a root file
        if isinstance(source, str):
            ROOT = cached_import("ROOT")
            source = ROOT.TFile(source)
            
        if TFile.is_corrupt(source):
            raise RuntimeError(f'empty or currupted root file: "{source.GetName()}"')
            
        return source
        
    """
    def make_branches(self, branch_data):
        branches = {}
        return branches
    
    def fill_branches(self, treename:str, branch_data):
        if self.obj is None:
            raise RuntimeError("no active ROOT file instance defined")
        tree = self.obj.Get(treename)
        if not tree:
            raise RuntimeError(f"the ROOT file does not contain the tree named \"{treename}\"")
        n_entries = tree.GetEntriesFast()
        
        for i in range(n_entries):
            for branch in branches:
                
        tree.SetDirectory(self.obj)
        # save only the new version of the tree
        tree.GetCurrentFile().Write("", ROOT.TObject.kOverwrite)
    """
    
    def get_tree(self, name:str, strict:bool=True):
        tree = self.obj.Get(name)
        if not tree:
            if strict:
                raise RuntimeError(f'In TFile.Get: Tree "{name}" does not exist')
            return None
        return tree

    def get_tree_compression_summary(self, treename:Optional[str]=None):
        file = self.obj
        if treename is None:
            treename = self._deduce_treename(file)
        tree = file.Get(treename)
        total_bytes = tree.GetTotBytes()
        zip_bytes = tree.GetZipBytes()
        summary = {
            'total_bytes': total_bytes,
            'total_bytes_s': bytes_to_readable(total_bytes),
            'zip_bytes': zip_bytes,
            'zip_bytes_s': bytes_to_readable(zip_bytes),
            'comp_factor': total_bytes / zip_bytes
        }
        return summary

    def get_compression_summary(self, treenames:Optional[List[str]]=None):
        file = self.obj
        comp_setting = file.GetCompressionSettings()
        summary = {}
        summary["comp_setting"] = comp_setting
        summary["trees"] = {}
        if treenames is None:
            treenames = self._get_all_treenames(file)
        for treename in treenames:
            summary["trees"][treename] = self.get_tree_compression_summary(treename)
        return summary
        
    @semistaticmethod
    def copy_remote_files(self, paths:Union[str, List[str]],
                          cache:bool=True,
                          cachedir:str="/tmp",
                          parallel:bool=False,
                          **kwargs):
        if isinstance(paths, str):
            paths = [paths]
        remote_paths = []
        for path in paths:
            if not is_remote_path(path):
                self.stdout.warning(f"Not a remote file: {path}. Skipped.")
                continue
            if local_path_exists(path):
                self.stdout.warning(f"Remote path {path} can be accessed locally. Skipped.")
                continue
            remote_paths.append(path)
        from quickstats.interface.xrootd import switch_cachedir
        with switch_cachedir(cachedir):
            filenames = self.list_files(remote_paths, resolve_cache=cache,
                                        expand_remote_files=True)
        cached_files = [filename for filename in filenames if not is_remote_path(filename)]
        files_to_fetch = [filename for filename in filenames if is_remote_path(filename)]
        if cached_files:
            self.stdout.info(f'Cached remote file(s):\n' + '\n'.join(cached_files))
        src, dst = [], []
        for file in files_to_fetch:
            src.append(file)
            dst.append(self._get_cache_path(file, cachedir=cachedir))
        if not src:
            return None
        from quickstats.interface.xrootd import XRDHelper
        helper = XRDHelper(verbosity=self.stdout.verbosity)
        if parallel:
            helper.copy_files(src, dst, force=not cache, **kwargs)
            return None
        for src_i, dst_i in zip(src, dst):
            helper.copy_files([src_i], [dst_i], force=not cache, **kwargs)

    def get(self, key:str):
        return self.obj.Get(key)

    def close(self):
        self.obj.Close()
        self.obj = None