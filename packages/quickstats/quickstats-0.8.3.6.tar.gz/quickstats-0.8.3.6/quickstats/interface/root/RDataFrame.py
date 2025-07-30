import json
from typing import Optional, Union, List, Dict
from tempfile import NamedTemporaryFile

import numpy as np

import quickstats
from quickstats import semistaticmethod, DescriptiveEnum, cached_import
from .TObject import TObject
from .TChain import TChain
from .TFile import TFile

class RDataFrameBackend(DescriptiveEnum):
    DEFAULT = (0, "Default backend")
    SPARK = (1, "Spark backend")
    DASK = (2, "Dask backend")

class RDataFrame(TObject):

    @property
    def rdf(self):
        return self.obj
    
    def __init__(self, *args, verbosity:Optional[Union[int, str]]="INFO", **kwargs):
        super().__init__(verbosity=verbosity, **kwargs)
        ROOT = cached_import("ROOT")
        if not args:
            self.obj = None
        elif (len(args) == 1) and isinstance(args[0], ROOT.RDataFrame):
            self.obj = args[0]
        else:
            self.obj = ROOT.RDataFrame(*args)
       
    @semistaticmethod
    def create_spec(self, source:Union[Dict, List[str], str],
                    global_range:Optional[List]=None,
                    sample_metadata:Optional[Dict]=None,
                    select_samples:Optional[List[str]]=None,
                    default_sample:str="sample",
                    default_treename:Optional[str]=None):
        if isinstance(source, dict):
            spec = source.copy()
        else:
            spec = {"samples": {default_sample: {"trees": [], "files": []}}}
            if isinstance(source, str):
                source = [source]
            for source_i in source:
                info = TChain.parse_tree_filename(source_i)
                filename, treename = info['filename'], info['treename']
                if treename is None:
                    treename = default_treename
                spec['samples'][default_sample]['trees'].append(treename) 
                spec['samples'][default_sample]['files'].append(filename)
        if sample_metadata is None:
            sample_metadata = {}
        if select_samples is not None:
            spec['samples'] = {sample:sample_spec for sample, sample_spec in spec['samples'].items() \
                               if sample in select_samples}
        for sample, sample_spec in spec['samples'].items():
            if 'trees' not in sample_spec:
                sample_spec['trees'] = [default_treename] * len(sample_spec['files'])
            else:
                sample_spec['trees'] = [treename if treename is not None else default_treename \
                                        for treename in sample_spec['trees']]
            if any(treename is None for treename in sample_spec['trees']):
                raise ValueError("found file with unspecified treename")
            if sample in sample_metadata:
                sample_spec['metadata'] = sample_metadata[sample]
        if (global_range is not None):
            spec["samples"]["range"] = global_range
        return spec

    @semistaticmethod
    def _get_spec_files_and_trees(self, spec:Dict):
        files = []
        trees = []
        for sample, sample_spec in spec['samples'].items():
            files.extend(sample_spec['files'])
            trees.extend(sample_spec['trees'])
        return files, trees
    
    @semistaticmethod
    def _requires_unsafe_tchain(self, files):
        from quickstats.utils.root_utils import get_cachedir
        return  (any(TFile._requires_protocol(file) for file in files) and \
                 (get_cachedir() is not None))

    @semistaticmethod
    def get_chain_from_spec(self, spec:Dict, multithread_safe:bool=True):
        ROOT = cached_import("ROOT")
        files, trees = self._get_spec_files_and_trees(spec)
        from quickstats.utils.root_utils import get_cachedir
        # this is just to fix a bug where RDataFrame custom TChain
        # does not support remote file caching
        # https://github.com/root-project/root/issues/15028
        if ((not multithread_safe) and self._requires_unsafe_tchain(files)):
            chain = ROOT.TChain()
        else:
            try:
                chain = ROOT.Internal.TreeUtils.MakeChainForMT()
            except:
                chain = ROOT.TChain("", "", ROOT.TChain.kWithoutGlobalRegistration)
                chain.ResetBit(ROOT.TObject.kMustCleanup)
        for (file, tree) in zip(files, trees):
            chain.AddFile(file, ROOT.TTree.kMaxEntries, tree)
        # NB: Might leak memory!
        ROOT.SetOwnership(chain, False)
        return chain

    @semistaticmethod
    def _parse_backend(self, backend:Optional[str]=None):
        if not backend:
            backend = RDataFrameBackend.DEFAULT
        else:
            backend = RDataFrameBackend.parse(backend)
        return backend
    
    @semistaticmethod
    def _get_kernel(self, backend:Optional[str]=None):
        ROOT = cached_import("ROOT")
        backend = self._parse_backend(backend)
        if backend == RDataFrameBackend.DEFAULT:
            return ROOT.RDataFrame
        elif backend == RDataFrameBackend.SPARK:
            return ROOT.RDF.Experimental.Distributed.Spark.RDataFrame
        elif backend == RDataFrameBackend.DASK:
            return ROOT.RDF.Experimental.Distributed.Dask.RDataFrame
        
    @semistaticmethod
    def get_dataset_spec(self, spec:Dict):
        ROOT = cached_import("ROOT")
        ds_spec = ROOT.RDF.Experimental.RDatasetSpec()
        for sample, sample_spec in spec['samples'].items():
            treenames = sample_spec['trees']
            filenames = sample_spec['files']
            if 'metadata' in sample_spec:
                metadata = ROOT.RDF.Experimental.RMetaData()
                for key, value in sample_spec['metadata'].items():
                    metadata.Add(key, value)
                sample = ROOT.RDF.Experimental.RSample(sample, treenames, filenames, metadata)
            else:
                sample = ROOT.RDF.Experimental.RSample(sample, treenames, filenames)
            ds_spec.AddSample(sample)
        if "range" in spec['samples']:
            global_range = spec['samples']['range']
            ds_spec.WithGlobalRange(tuple(global_range))
        return ds_spec

    @semistaticmethod
    def _awkward_array(self, rdf, columns:Optional[List[str]]=None, **kwargs):
        if columns is None:
            columns = list(rdf.GetColumnNames())
        import awkward as ak
        array = ak.from_rdataframe(rdf, columns=columns, **kwargs)
        return array

    def awkward_array(self, columns:Optional[List[str]]=None, **kwargs):
        rdf = self.rdf
        if rdf is None:
            RuntimeError('RDataFrame instance not initialized')
        return self._awkward_array(rdf, columns=columns, **kwargs)

    @semistaticmethod
    def from_files(self, *filenames_chain,
                   treename:Optional[str]=None,
                   columns:Optional[List[str]]=None,
                   backend:str=None,
                   backend_options:Optional[Dict]=None,
                   multithread_safe=True):
        """
        Create RDataFrame instance from a list of input files.

        It considers the generic case of files with different treenames. 
        """
        if not filenames_chain:
            raise ValueError('No files specified')
        backend = self._parse_backend(backend)
        has_friends = len(filenames_chain) > 1
        specs = []
        for filenames in filenames_chain:
            spec = self.create_spec(filenames, default_treename=treename)
            specs.append(spec)
        
        files, trees = self._get_spec_files_and_trees(spec)

        if (not has_friends) and (backend == RDataFrameBackend.DEFAULT) and \
            (quickstats.root_version >= (6, 28, 0)):
            spec = specs[0]
            files, trees = self._get_spec_files_and_trees(spec)
            if (not self._requires_unsafe_tchain(files)):
                dataset_spec = self.get_dataset_spec(spec)
                return self.from_dataset_spec(dataset_spec, backend=backend,
                                              backend_options=backend_options)
        kernel = self._get_kernel(backend)
        if not has_friends:
            # do not require TChain
            if len(set(trees)) == 1:
                args = (trees[0], files)
            else:
                chain = self.get_chain_from_spec(spec, multithread_safe=multithread_safe)
                args = (chain,)
        else:
            main_chain = None
            for spec in specs:
                chain = self.get_chain_from_spec(spec, multithread_safe=multithread_safe)
                if main_chain is None:
                    main_chain = chain
                main_chain.AddFriend(chain)
            args = (main_chain,)
        if columns is not None:
            args += (columns,)
        if backend_options is None:
            backend_options = {}
        return kernel(*args, **backend_options)

    @semistaticmethod
    def from_dataset_spec(self, dataset_spec, backend:str=None,
                          backend_options:Optional[Dict]=None):
        backend = self._parse_backend(backend)
        if backend != RDataFrameBackend.DEFAULT:
            self.stdout.warning("Creating RDataFrame from DatasetSpec is not supported " +\
                               f"with the {backend.name} backend. Fall back to default " +\
                                "backend")
            backend = RDataFrameBackend.DEFAULT
        if backend_options is None:
            backend_options = {}
        kernel = self._get_kernel(backend)
        return kernel(dataset_spec, **backend_options)

    @staticmethod
    def _resolve_columns(rdf,
                         columns:Optional[List[str]]=None,
                         exclude:Optional[List[str]]=None,
                         mode:str="ALL"):
        from quickstats.utils.common_utils import filter_by_wildcards, remove_duplicates
        from quickstats.utils.data_conversion import (root_datatypes, get_rdf_column_type,
                                                      ConversionMode, reduce_vector_types)
        all_columns = list([str(col) for col in rdf.GetColumnNames()])
        
        if columns is None:
            columns = list(all_columns)
        if exclude is None:
            exclude = []
        
        selected_columns = filter_by_wildcards(all_columns, columns)
        selected_columns = filter_by_wildcards(selected_columns, exclude, exclusion=True)
        selected_columns = remove_duplicates(selected_columns)
    
        mode = ConversionMode.parse(mode)
        if mode in [ConversionMode.REMOVE_NON_STANDARD_TYPE,
                    ConversionMode.REMOVE_NON_ARRAY_TYPE]:
            column_types = np.array([get_rdf_column_type(rdf, col) for col in selected_columns])
            if mode == ConversionMode.REMOVE_NON_ARRAY_TYPE:
                column_types = reduce_vector_types(column_types)
            new_columns = list(np.array(selected_columns)[np.where(np.isin(column_types, root_datatypes))])
            removed_columns = np.setdiff1d(selected_columns, new_columns)
            selected_columns = new_columns
        else:
            removed_columns = []
        return selected_columns, removed_columns

    def resolve_columns(self,
                        columns:Optional[List[str]]=None,
                        exclude:Optional[List[str]]=None,
                        mode:str="ALL"):
        return self._resolve_columns(self.rdf, columns=columns, exclude=exclude, mode=mode)