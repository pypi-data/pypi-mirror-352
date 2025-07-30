from typing import Optional, List, Dict, Union
import os
import copy
import glob
import json
import time

import numpy as np

from .builtin_methods import BUILTIN_METHODS
from .actions import *
from .roo_process_config import RooProcessConfig

from quickstats import timer, AbstractObject, GeneralEnum, module_exists, semistaticmethod, cached_import
from quickstats.interface.root import TFile, RDataFrame, RDataFrameBackend
from quickstats.interface.xrootd import get_cachedir, set_cachedir, switch_cachedir
from quickstats.utils.root_utils import declare_expression, close_all_root_files, set_multithread
from quickstats.utils.path_utils import is_remote_path
from quickstats.utils.common_utils import get_cpu_count, combine_dict
from quickstats.utils.string_utils import split_str
from quickstats.daq import DEFAULT_CACHE_DIR, XRootDSource, ServiceXSource

class RDFVerbosity(GeneralEnum):
    UNSET   = (0, 'kUnset')
    FATAL   = (1, 'kFatal')
    ERROR   = (2, 'kError')
    WARNING = (3, 'kWarning')
    INFO    = (4, 'kInfo')
    DEBUG   = (5, 'kDebug')

    def __new__(cls, value:int, key:str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.key = key
        return obj

class DataDeliveryService(GeneralEnum):
    XROOTD   = (0, "XRootD")
    SERVICEX = (1, "ServiceX")
    
    def __new__(cls, value:int, key:str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.key = key
        return obj

DEFAULT_DATA_DELIVERY_OPTIONS = {
    DataDeliveryService.XROOTD: {
        "cachedir": DEFAULT_CACHE_DIR,
        "local_cache": False,
        "localize": False
    },
    DataDeliveryService.SERVICEX: {
        "cachedir": DEFAULT_CACHE_DIR,
        "local_cache": True,
        "deliver_options": {
            "batchsize" : None,
            "retry" : 5,
            "ignore_failure": True
        }
    }    
}

DATASOURCE_MAP = {
    DataDeliveryService.XROOTD: XRootDSource,
    DataDeliveryService.SERVICEX: ServiceXSource
}

class RooProcessor(AbstractObject):

    @property
    def distributed(self):
        return self.backend != RDataFrameBackend.DEFAULT
        
    def __init__(self, config_source:Optional[Union[RooProcessConfig, str]]=None,
                 flags:Optional[List[str]]=None,
                 multithread:int=True,
                 cache:bool=False,
                 backend:Optional[Union[str, RDataFrameBackend]]=None,
                 backend_options:Optional[Dict]=None,
                 data_service:Optional[Union[str, DataDeliveryService]]=None,
                 data_service_options:Optional[Dict]=None,
                 use_template:bool=False,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.cache = cache
        self.action_tree = None
        if flags is not None:
            self.flags = list(flags)
        else:
            self.flags = []
        self._file_chains = {}
        self.rdf_frames = {}
        self.rdf = None
        self.global_variables = {}
        self.external_variables = {}
        self.default_treename = None
        self.use_template = use_template
        self.rdf_verbosity = None
        self.result_metadata = None
        self.set_profile_options()
        self.set_backend(backend, backend_options)
        self.set_data_service(data_service, data_service_options)
        self.load_buildin_functions()

        self.set_multithread(multithread)
        
        if config_source is not None:
            self.load_config(config_source)

    def set_backend(self, backend:Optional[Union[str, RDataFrameBackend]]=None,
                    options:Optional[Dict]=None):
        if backend is None:
            self.backend = RDataFrameBackend.DEFAULT
        else:
            self.backend = RDataFrameBackend.parse(backend)
        # TODO: add default options
        self.backend_options = combine_dict(options)

    def set_data_service(self, service:Optional[Union[str, DataDeliveryService]]=None,
                         options:Optional[Dict]=None):
        # auto-detect by default
        if service is None:
            if module_exists("servicex"):
                service = "servicex"
            else:
                service = "xrootd"
        service = DataDeliveryService.parse(service)
        self.stdout.info(f"Using data delivery service: {service.key}")
        self.data_service = service
        default_options = DEFAULT_DATA_DELIVERY_OPTIONS[service]
        self.data_service_options = combine_dict(default_options, options)    

    def set_multithread(self, num_threads:Optional[int]=None):
        if num_threads is None:
            num_threads = self.multithread
        num_threads = set_multithread(num_threads)
        if num_threads is None:
            self.stdout.info("Disabled multithreading.")
        else:
            self.stdout.info(f"Enabled multithreading with {num_threads} threads.")
        self.multithread = num_threads
            
    def set_cache(self, cache:bool=True):
        self.cache = cache

    def set_profile_options(self, throughput:bool=False):
        profile_options = {
            "throughput": throughput
        }
        self.profile_options = profile_options
            
    def load_buildin_functions(self):
        # bug of redefining module from ROOT
        try:
            ROOT = cached_import("ROOT")
            Internal = ROOT.Internal
        except:
            Internal = None
        distributed = self.distributed
        for name, definition in BUILTIN_METHODS.items():
            declare_expression(definition, name, distributed=distributed)
        if Internal is not None:
            if Internal != ROOT.Internal:
                ROOT.Internal = Internal
    
    def load_config(self, config_source:Union[RooProcessConfig, str]):
        if isinstance(config_source, RooProcessConfig):
            config = config_source
        else:
            config = RooProcessConfig.open(config_source)
        self.config = config
        action_tree = config.get_action_tree()
        action_tree.construct_actions(rdf_backend=self.backend)
        if not action_tree.root_node.has_child:
            raise RuntimeError("no actions found in the process card")
        first_action = action_tree.root_node.first_child.action
        if isinstance(first_action, RooProcTreeName):
            self.default_treename = first_action._params['treename']
        else:
            self.default_treename = None
        self.action_tree = action_tree
        
    def set_global_variables(self, **kwargs):
        self.global_variables.update(kwargs)
        
    def clear_global_variables(self):
        self.global_variables = {}
    
    def add_flags(self, flags:List[str]):
        self.flags += list(flags)
        
    def set_flags(self, flags:List[str]):
        self.flags = list(flags)        
        
    def cleanup(self, deepclean:bool=True):
        close_all_root_files()
        if deepclean:
            self.rdf_frames = {}
            self.rdf = None
            
    def shallow_cleanup(self):
        self.cleanup(deepclean=False)
    
    def run_action(self, action:RooProcBaseAction):
        if not self.rdf:
            raise RuntimeError("RDataFrame instance not initialized")
        if isinstance(action, RooProcRDFAction):
            self.rdf = action.execute(self.rdf, self.global_variables)
        elif isinstance(action, RooProcHelperAction):
            action.execute(self, self.global_variables)
        elif isinstance(action, RooProcHybridAction):
            self.rdf, _ = action.execute(self.rdf, self, self.global_variables)
        elif isinstance(action, RooProcNestedAction):
            return_code = action.execute(self, self.global_variables)
            return return_code
        else:
            raise RuntimeError("unknown action type")
        return RooProcReturnCode.NORMAL
            
    def run_all_actions(self, consider_child:bool=True):
        if not self.action_tree:
            raise RuntimeError("action tree not initialized")
        node = self.action_tree.get_next(consider_child=consider_child)
        if node is not None:
            source = node.try_get_data("source", None)
            self.stdout.debug(f'Executing node "{node.name}" defined at line {node.data["start_line_number"]}'
                             f' (source {source})')
            action = node.action
            return_code = self.run_action(action)
            if return_code == RooProcReturnCode.NORMAL:
                self.run_all_actions()
            elif return_code == RooProcReturnCode.SKIP_CHILD:
                self.run_all_actions(consider_child=False)
            else:
                raise RuntimeError("unknown return code")
        else:
            self.stdout.debug('All node executed')
            
    def sanity_check(self):
        if not self.action_tree:
            raise RuntimeError("action tree not initialized")        
        if not self.action_tree.root_node.has_child:
            self.stdout.warning("No actions to be performed.")
            return None
            
    def get_source_files(self, filenames:Union[List[str], str]):
        data_source_cls = DATASOURCE_MAP[self.data_service]
        data_service_options = self.data_service_options.copy()
        if self.data_service == DataDeliveryService.SERVICEX:
            data_service_options["columns"] = self.get_referenced_columns()
        deliver_options = data_service_options.pop("deliver_options", {})
        data_source = data_source_cls(**data_service_options)
        data_source.add_files(filenames)
        filenames = data_source.deliver(**deliver_options)
        if self.data_service == DataDeliveryService.SERVICEX:
            # TO FIX
            self.default_treename = "servicex"
        return filenames

    @staticmethod
    def _resolve_filechains(filenames:Union[List[str], str]):
        if isinstance(filenames, str):
            filenames = [filenames]
        filechains = {}
        for filename in filenames:
            filenames_chain = split_str(filename, sep=';', strip=True)
            for i, filename_chain in enumerate(filenames_chain):
                filechains.setdefault(i, [])
                filechains[i].append(filename_chain)
        return filechains

    def get_source_filechains(self, filechains:Dict[str, List[str]]):
        source_filechains = {}
        nchains = len(filechains)
        for chain_index, filenames in filechains.items():
            source_filenames = self.get_source_files(filenames)
            source_filechains[chain_index] = source_filenames
            if (not source_filenames):
                # not matching files
                if chain_index == 0:
                    return source_filechains
                raise RuntimeError(f'No friend files matching the expressions: {filenames}')
            if (nchains > 1) and (len(source_filenames) > 1):
                raise RuntimeError('Multiple input files with friends is not supported')
        return source_filechains
        
    def load_rdf(self,
                 filenames:Union[List[str], str],
                 treename:Optional[str]=None):
        filechains = self._resolve_filechains(filenames)
        filechains = self.get_source_filechains(filechains)
        if not filechains[0]:
            self.stdout.info('No files to be processed. Skipping.')
            return None
        
        if treename is None:
            treename = self.default_treename
        if treename is None:
            treename = TFile._get_main_treename(filechains[0][0])
            self.stdout.info(f"Using deduced treename: {treename}")

        if len(filechains) == 1:
            filenames = filechains[0]
        else:
            filenames = list(zip(*filechains.values()))

        self._filenames = filenames
        if (len(filechains) == 1) and (len(filenames) == 1):
            self.stdout.info(f'Processing file "{filenames[0]}".')
        else:
            def get_filename_repr(filename:str):
                return "(" + ", ".join(filename) + ")" if isinstance(filename, tuple) else f'"{filename}"'
            self.stdout.info("Processing files")
            for filename in filenames:
                self.stdout.info(f"  {get_filename_repr(filename)}", bare=True)
                
        rdf = RDataFrame.from_files(*filechains.values(), treename=treename,
                                    backend=self.backend,
                                    backend_options=self.backend_options,
                                    multithread_safe=self.multithread)
        self.rdf = rdf
        return self
    
    def run(self, filenames:Optional[Union[List[str], str]]=None):
        self.sanity_check()
        with timer() as t:
            if filenames is not None:
                self.load_rdf(filenames)
            self.action_tree.reset()
            self.run_all_actions()
            self.shallow_cleanup()
        self.stdout.info(f"Task finished. Total time taken: {t.interval:.3f} s.")
        result_metadata = {
            "files": copy.deepcopy(self._filenames),
            "real_time": t.real_time_elapsed,
            "cpu_time": t.cpu_time_elapsed
        }
        self.result_metadata = result_metadata
        return self

    def get_rdf(self, frame:Optional[str]=None):
        rdf = self.rdf if frame is None else self.rdf_frames.get(frame, None)
        if rdf is None:
            raise RuntimeError('RDataFrame instance not initialized')
        return rdf

    def get_referenced_columns(self):
        action_tree = self.action_tree
        return action_tree.get_referenced_columns(self.global_variables)

    def resolve_columns(self, frame:Optional[str]=None,
                        columns:Optional[List[str]]=None,
                        exclude:Optional[List[str]]=None,
                        mode:str="ALL"):
        rdf = self.get_rdf(frame)
        selected_columns, _ = RDataFrame._resolve_columns(rdf=rdf,
                                                          columns=columns,
                                                          exclude=exclude,
                                                          mode=mode)
        return selected_columns
        
    def awkward_array(self, frame:Optional[str]=None,
                      columns:Optional[List[str]]=None):
        rdf = self.get_rdf(frame)
        selected_columns = self.resolve_columns(frame, columns=columns)
        return RDataFrame._awkward_array(rdf, columns=selected_columns)

    def display(self, frame:Optional[str]=None,
                columns:Union[str, List[str]]="",
                n_rows:int=5, n_max_collection_elements:int=10,
                lazy:bool=False):
        rdf = self.get_rdf(frame)
        result = self.rdf.Display(columns, n_rows, n_max_collection_elements)
        if not lazy:
            result.Print()
            return None
        return result

    def save_graph(self, frame:Optional[str]=None,
                   filename:Optional[str]=None):
        ROOT = cached_import("ROOT")
        rdf = self.get_rdf(frame)
        if filename:
            ROOT.RDF.SaveGraph(rdf, filename)
        else:
            ROOT.RDF.SaveGraph(rdf)

    def set_rdf_verbosity(self, verbosity:str='INFO'):
        ROOT = cached_import("ROOT")
        if isinstance(verbosity, str):
            verbosity = RDFVerbosity.parse(verbosity)
            loglevel = getattr(ROOT.Experimental.ELogLevel, verbosity.key)
        else:
            loglevel = verbosity
        verb = ROOT.Experimental.RLogScopedVerbosity(ROOT.Detail.RDF.RDFLogChannel(), loglevel)
        self.rdf_verbosity = verb