from typing import Optional, Dict, List, Union, Sequence
import os
import glob
import time

import numpy as np

import quickstats
from quickstats import cached_import
from .common_utils import get_cpu_count

root_type_str_maps = {
    'Char_t'    : 'char',
    'Bool_t'    : 'bool',
    'Float_t'   : 'float',
    'Double_t'  : 'double',
    'Int_t'     : 'int',
    'Long_t'    : 'long',
    'Long64_t'  : 'long long',
    'UInt_t'    : 'unsigned int',
    'ULong_t'   : 'unsigned long',
    'ULong64_t' : 'unsigned long long'
}

def rtype2ctype(rtypes:List[str]):
    ctypes = []
    for rtype in rtypes:
        #rtype = rtype.replace("ROOT::VecOps::RVec", "vector")
        ctype = root_type_str_maps.get(rtype, rtype)
        ctypes.append(ctype)
    return ctypes

def templated_rdf_snapshot(rdf:"ROOT.RDataFrame", columns:List[str]=None):
    if columns is None:
        columns = [str(i) for i in rdf.GetColumnNames()]
    rtypes = [rdf.GetColumnType(c) for c in columns]
    ctypes = tuple(rtype2ctype(rtypes))
    snapshot = rdf.Snapshot.__getitem__(ctypes)
    return snapshot

def is_corrupt(f:Union["ROOT.TFile", str]):
    ROOT = cached_import("ROOT")
    if isinstance(f, str):
        ROOT.RooMsgService.instance().setSilentMode(True)
        f = ROOT.TFile.Open(f)
        ROOT.RooMsgService.instance().setSilentMode(False)
    if f.IsZombie():
        return True
    if f.TestBit(ROOT.TFile.kRecovered):
        return True
    if f.GetNkeys() == 0:
        return True
    return False

def opt_flags() -> str:
    ROOT = cached_import("ROOT")
    return ROOT.gSystem.GetFlagsOpt()

def compile_macro(name:str, opt:str="kfOc"):
    ROOT = cached_import("ROOT")
    macros_dir = os.path.join(quickstats.macro_path, name)
    macros_path = os.path.join(macros_dir, name + '.cxx')
    print('INFO: Compiling macro "{}"...'.format(name))
    if not os.path.exists(macros_path):
        print('ERROR: Cannot locate macro files from {}. ROOT macros will not be compiled.'.format(macros_dir))
        return -1
    status = ROOT.gSystem.CompileMacro(macros_path, opt)
    #status = ROOT.gROOT.LoadMacro('{}++'.format(macros_path))
    return status

def load_library(name:str):
    import cppyy
    if name in dir(cppyy.gbl):
        return None
    macros_dir = os.path.join(quickstats.macro_path, name)
    macros_path = os.path.join(macros_dir, name + '_cxx')
    if os.path.exists(macros_path + '.so'):
        try:
            cppyy.load_library(macros_path)
            return None
        except RuntimeError:
            return load_macro(name)
    return load_macro(name)
        
def load_macro(name:str):
    import cppyy
    if name in dir(cppyy.gbl):
        return None
    ROOT = cached_import("ROOT")
    auto_load = ROOT.gInterpreter.AutoLoad(name)
    # already loaded by quickstats / third-party
    if auto_load == 1:
        return None
    class_loaded = hasattr(ROOT, name)
    if class_loaded:
        return None
    macros_dir = os.path.join(quickstats.macro_path, name)
    macros_path = os.path.join(macros_dir, name + '_cxx')
    if not os.path.exists(macros_path + '.so'):
        status_compile = compile_macro(name)
    status_load = ROOT.gSystem.Load(macros_path)
    if (status_load != 0) and (status_load != 1):
        raise RuntimeError(f"Shared library for the macro {name} is incompatible with the current pyROOT version. "
                           "Please recompile by using the command line \"quickstats compile\". "
                           "(use quickstats.compile_macros() instead inside a jupyter kernel)")
    return status_load

def get_macro_dir(name:str):
    return os.path.join(quickstats.macro_path, name)

def get_macro_TClass(name:str):
    ROOT = cached_import("ROOT")
    if not getattr(ROOT, name):
        raise RuntimeError(f"class {name} is not loaded into ROOT yet")    
    cls = ROOT.TClass.GetClass(name)
    macro_dir = get_macro_dir(name)
    macro_decl_file = os.path.join(f"{macro_dir}/{name}.h")
    macro_impl_file = os.path.join(f"{macro_dir}/{name}.cxx")
    if not os.path.exists(macro_decl_file):
        raise FileNotFoundError(f"decl file {macro_decl_file} for the macro \"{name}\" not found")
    if not os.path.exists(macro_impl_file):
        raise FileNotFoundError(f"impl file {macro_impl_file} for the macro \"{name}\" not found")        
    cls.SetDeclFile(macro_decl_file, 0)
    cls.SetImplFileName(macro_impl_file)
    return cls

def print_resource_used(start):
    ROOT = cached_import("ROOT")
    proc_info = ROOT.ProcInfo_t()
    flag = ROOT.gSystem.GetProcInfo(proc_info)
    if flag < 0:
        return None
    cpu_time = proc_info.fCpuUser + proc_info.fCpuSys
    wall_time = time.time()-start
    print('Resources Used: cpu_time={:.3f}s, mem={}kb, vmem={}kb, wall_time={:.3f}s'.format(
          cpu_time, proc_info.fMemResident, proc_info.fMemVirtual, wall_time))
    return None

def process_uproot_array(source):
    result = np.array(source)
    if (result.dtype == np.dtype('O')) and (isinstance(result[0], bytes)):
        result = result.astype(str)
    return result

def get_data_size(data):
    if isinstance(data, (tuple, list, np.ndarray)):
        return len(data)
    else:
        return 1
    
def root_to_dict(filename:str, simplify:bool=True):
    ROOT = cached_import("ROOT")
    f = ROOT.TFile(filename)
    if is_corrupt(f):
        raise RuntimeError(f"corrupted ROOT file: {filename}")
    treenames = [t.GetName() for t in f.GetListOfKeys()]
    result = {}
    for treename in treenames:
        tree = f.Get(treename)
        rdf = ROOT.RDataFrame(tree)
        data = rdf.AsNumpy()
        for branch in data:
            # convert std::string to python string
            if rdf.GetColumnType(branch) == "string":
                data[branch] = np.char.mod('%s', data[branch])
            # unwrap array if size is 1
            if simplify and (data[branch].shape[0] == 1):
                data[branch] = data[branch][0]
        result[treename] = data
    return result    

def uproot_to_dict(file):
    result = {}
    for tree in file.values():
        #tree_name = tree.name.decode('utf-8')
        tree_name = tree.name
        result[tree_name] = {}
        for branch in tree.values():
            #branch_name = branch.name.decode('utf-8')
            branch_name = branch.name
            arr = process_uproot_array(branch.array())
            value = arr[0] if len(arr) == 1 else arr
            result[tree_name][branch_name] = value    
    return result
    
def get_leaf_type_str(data):
    from six import string_types
    
    type_str = None
    data_type = None

    if isinstance(data, (tuple, list, np.ndarray)):
        data_type = type(data[0])
        if data_type in string_types:
            return None
    elif isinstance(data, string_types):
        return None
    else:
        data_type = type(data)
        
    if data_type in [float, np.float64]:
        type_str = 'D'
    elif data_type in [int, np.int64]:
        type_str = 'L'
    elif data_type in [np.int32]:
        type_str = 'I'
    elif data_type in [np.uint32]:
        type_str = 'i'        
    elif data_type in [bool, np.bool_]:
        type_str = 'O'        
    elif data_type in [np.float32]:
        type_str = 'F'
    elif data_type in [np.int8]:
        type_str = 'B'
    elif data_type in [np.uint8]:
        type_str = 'b'
    else:
        raise ValueError('cannot infer leaf type for {}'.format(data_type))
    return type_str

def fill_branch(tree, values_dict):
    ROOT = cached_import("ROOT")
    buffer = {}
    leaf_types = {}
    data_sizes = list(set([get_data_size(v) for k,v in values_dict.items()]))
    if len(data_sizes) > 1:
        raise ValueError('cannot fill tree with values of inconsistent entry sizes')
    data_size = data_sizes[0]
    if data_size == 1:
        for k, v in values_dict.items():
            leaf_type_str = get_leaf_type_str(v)
            leaf_types[k] = leaf_type_str
            if leaf_type_str is not None:
                buffer[k] = np.array([v], dtype=type(v))
                tree.Branch(k, buffer[k], '{}/{}'.format(k, leaf_type_str))
            else:
                buffer[k] = ROOT.std.string(v)
                tree.Branch(k, buffer[k])
        tree.Fill()
    else:
        for k, v in values_dict.items():
            leaf_type_str = get_leaf_type_str(v)
            leaf_types[k] = leaf_type_str
            if leaf_type_str is not None:
                buffer[k] = np.array([v[0]], dtype=type(v[0]))
                tree.Branch(k, buffer[k], '{}/{}'.format(k, leaf_type_str))
            else:
                buffer[k] = ROOT.std.string(v[0])
                tree.Branch(k, buffer[k])
        for i in range(data_size):
            for k, v in values_dict.items():
                if leaf_types[k] is not None:
                    buffer[k][0] = v[i]
                else:
                    buffer[k].replace(0, ROOT.std.string.npos, v[i])
            tree.Fill()
            
def close_all_root_files():
    ROOT = cached_import("ROOT")
    ROOT.gROOT.CloseFiles()

def close_all_root_files2():
    ROOT = cached_import("ROOT")
    opened_files = ROOT.gROOT.GetListOfFiles()
    for f in opened_files:
        f.Close()

def delete_object(name:str):
    ROOT = cached_import("ROOT")
    obj = ROOT.gROOT.FindObject(name) 
    if obj:
        obj.Delete()
        
def create_declaration(expression:str, name:Optional[str]=None):
    if name is None:
        hash_str = str(hash(expression)).replace("-", "n")
        name_guard = f"__quickstats_declare_{hash_str}__"
    else:
        name_guard = f"__quickstats_declare_{name}__"
    guarded_declaration = f"#ifndef {name_guard}\n"
    guarded_declaration += f"#define {name_guard}\n"
    guarded_declaration += f"\n{expression}\n\n#endif\n"
    return guarded_declaration

def declare_expression(expression:str, name:Optional[str]=None,
                       distributed:bool=False):
    ROOT = cached_import("ROOT")
    declaration = create_declaration(expression, name)
    status = ROOT.gInterpreter.Declare(declaration)
    if distributed:
        def wrapper():
            ROOT.gInterpreter.Declare(declaration)
        try:
            ROOT.RDF.Experimental.Distributed.initialize(wrapper)
        except:
            quickstats.stdout.warning("Failed to initialize distributed code declarations. Ignored.")
    return status

def get_tree_names(f:"ROOT.TFile"):
    ROOT = cached_import("ROOT")
    tree_names = []
    for i in f.GetListOfKeys():
        obj = f.Get(i.GetName())
        if isinstance(obj, ROOT.TTree):
            tree_names.append(obj.GetName())
    return tree_names

def merge_root_files(source_files:Union[str, List[str]], target_file:str, treename:str=None,
                     multithread:bool=True, keep_order:bool=False, use_template:bool=True,
                     ignore_missing_columns:bool=True, verbosity:str="INFO"):
    ROOT = cached_import("ROOT")
    from quickstats import Logger
    stdout = Logger(verbosity)
    
    if isinstance(source_files, str):
        source_files = [source_files]
    rfiles = []
    for source_file in source_files:
        files = glob.glob(source_file)
        if not files:
            raise FileNotFoundError(f"file \"{source_file}\" does not exist")
        rfiles += files
    # now all rfiles are guaranteed to exist
    for i, rfile in enumerate(rfiles):
        stdout.info(f"Source {i+1}: {rfile}", bare=True)
        if is_corrupt(rfile):
            raise RuntimeError(f"the root file \"{rfile}\" is corrupted")
    if not rfiles:
        raise RuntimeError("no source files found")
    if treename is None:
        f = ROOT.TFile(rfiles[0])
        treenames = get_tree_names(f)
        if len(treenames) > 1:
            raise RuntimeError("unable to deduce tree name from source files: "
                               "multiple trees are present")
        treename = treenames[0]
        stdout.info("No tree name specified for merging. Will use "
                    f"the auto-detected tree name \"{treename}\".")
        
    # configure multi-threading setting
    multithread_orig_state = ROOT.IsImplicitMTEnabled()
    if multithread and (not multithread_orig_state) and (not keep_order):
        ROOT.EnableImplicitMT()
    if keep_order and multithread_orig_state:
        ROOT.DisableImplicitMT()
    
    if ignore_missing_columns:
        column_map = {}
        all_columns = set()
        for rfile in rfiles:
            rdf = ROOT.RDataFrame(treename, rfile)
            columns = set([str(i) for i in rdf.GetColumnNames()])
            all_columns.update(columns)
            column_map[rfile] = columns
        for rfile, columns in column_map.items():
            if columns != all_columns:
                missing_columns = list(all_columns - columns)
                stdout.warning(f"The root file \"{rfile}\" is missing the following column(s): "
                               f"{','.join(missing_columns)}. The missing column(s) will not be saved.")
        columns_to_keep = list(set.intersection(*column_map.values()))
        rdf = ROOT.RDataFrame(treename, rfiles)
        stdout.info(f"Target path: {target_file}", bare=True)
        if use_template:
            snapshot = templated_rdf_snapshot(rdf, columns_to_keep)
        else:
            snapshot = rdf.Snapshot
        snapshot(treename, target_file, columns_to_keep)
    else:
        rdf = ROOT.RDataFrame(treename, rfiles)
        stdout.info(f"Target path: {target_file}", bare=True)
        if use_template:
            snapshot = templated_rdf_snapshot(rdf, columns_to_keep)
        else:
            snapshot = rdf.Snapshot
        snapshot(treename, target_file)
   
    # restore multi-threading setting
    if multithread_orig_state != ROOT.IsImplicitMTEnabled():
        if multithread_orig_state:
            ROOT.DisableImplicitMT()
        else:
            ROOT.EnableImplicitMT()
            
def list_root_files(paths:Union[List[str], str], strict_format:Optional[str]=None):
    from quickstats.interface.root import TFile
    return TFile.list_files(paths, strict_format=strict_format)

def close_read_cache(rfile:"ROOT.TFile"):
    read_cache = rfile.GetCacheRead()
    if read_cache:
        read_cache.Close()
        
def set_cachedir(cachedir:str="", forcecache:bool=True):
    ROOT = cached_import("ROOT")
    if not cachedir:
        cachedir = ""
        forcecache = False
    ROOT.TFile.SetCacheFileDir(cachedir, True, forcecache)
    
def get_cachedir():
    ROOT = cached_import("ROOT")
    cachedir = ROOT.TFile.GetCacheFileDir()
    if (not cachedir) or (cachedir == "/"):
        return None
    return cachedir

def set_multithread(num_threads:Union[int, bool]=None):
    ROOT = cached_import("ROOT")
    if num_threads:
        if num_threads > 1:
            ROOT.EnableImplicitMT(num_threads)
        else:
            ROOT.EnableImplicitMT()
            num_threads = get_cpu_count()
    else:
        num_threads = None
        if ROOT.IsImplicitMTEnabled():
            ROOT.DisableImplicitMT()
    return num_threads

def get_tree_perf_stats(tree):
    ROOT = cached_import("ROOT")
    # https://eguiraud.web.cern.ch/eguiraud/decks/root_io_perf_tooling/#/6
    ps = ROOT.TTreePerfStats("ioperf", tree)
    for i in range(tree.GetEntriesFast()):
        tree.GetEntry(i)
    ps.Print() # or ps.GetXXX(), or ps.Draw()

def print_tree_clusters(tree):
    tree.Print("clusters")

def set_task_per_worker_hint(m:int):
    ROOT = cached_import("ROOT")
    ROOT.TTreeProcessorMT.SetTasksPerWorkerHint(m)

def get_task_per_worker_hint():
    ROOT = cached_import("ROOT")
    return ROOT.TTreeProcessorMT.GetTasksPerWorkerHint()

def get_opt_flag():
    ROOT = cached_import("ROOT")
    return ROOT.gSystem.GetFlagsOpt()

def get_misc_summary():
    ROOT = cached_import("ROOT")
    summary = {
        'opt_flag': get_opt_flag(),
        'multithread': ROOT.IsImplicitMTEnabled(),
        'task_per_worker_hint': get_task_per_worker_hint(),
        'cachedir': get_cachedir()
    }
    return summary