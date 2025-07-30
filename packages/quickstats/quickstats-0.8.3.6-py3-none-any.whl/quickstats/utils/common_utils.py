import os
import sys
import copy
import fnmatch
import time
import json
import yaml
import inspect
import datetime
import functools
import collections.abc
from collections import Counter
from typing import Optional, Union, Dict, List, Tuple, Callable, Any

import numpy as np

from quickstats.core.typing import Iterable

class disable_cout:    
    def __enter__(self):
        import cppyy
        cppyy.gbl.std.cout.setstate(cppyy.gbl.std.ios_base.failbit)
        return self

    def __exit__(self, *args):
        import cppyy
        cppyy.gbl.std.cout.clear()

def timely_info(green_text, normal_text, adjust=40):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '\033[92m[INFO]\033[0m', '\033[92m{}\033[0m'.format(green_text).rjust(40, ' '), normal_text)

def get_cpu_count():
    return os.cpu_count()

def execute_multi_tasks(
    func: Callable[..., Any], 
    *iterables: Iterable[Any],
    parallel: int, 
    executor: str = 'process'
) -> Any:
    """
    Execute tasks in parallel using the specified executor.

    Parameters
    ----------
    func : Callable[..., Any]
        The function to be executed for each task. It should accept arguments corresponding to the elements
        of the provided iterables.
    *iterables : Iterable[Any]
        One or more iterables that provide the arguments for `func`. The function is applied element-wise across these iterables.
    parallel : int
        The number of parallel tasks to run. If `parallel` is positive, it sets the number of parallel workers.
        If `parallel` is negative, the number of workers will be set to the number of CPUs on the system (`os.cpu_count()`).
        If `parallel` is `0`, tasks are run sequentially, i.e., no parallel workers are used.
    executor : str, optional
        The type of executor to use, either 'process' or 'thread'. The default is 'process', which uses multiprocessing.
        If 'thread' is specified, threading will be used instead.

    Returns
    -------
    Any
        The result of applying `func` in parallel (or sequentially) to the provided iterables. The return type depends on the implementation.

    Examples
    --------
    >>> def add(a, b):
    ...     return a + b
    >>> result = execute_multi_tasks(add, [1, 2, 3], [4, 5, 6], parallel=2)
    >>> print(result)
    [5, 7, 9]
    """

    if parallel == 0:
        # Run tasks sequentially
        result = [func(*args) for args in zip(*iterables)]
        return result
    else:
        # Determine the number of workers
        if parallel < 0:
            parallel = get_cpu_count()

        # Select the appropriate executor (process or thread)
        if executor == 'process':
            from concurrent.futures import ProcessPoolExecutor as Executor
        elif executor == 'thread':
            from concurrent.futures import ThreadPoolExecutor as Executor
        else:
            raise ValueError(f'Invalid executor: {executor} (choose between "process" and "thread")')

        # Run tasks in parallel using the chosen executor
        with Executor(max_workers=parallel) as exec:
            results = list(exec.map(func, *iterables))
        
        return results

def stdout_print(msg):
    sys.__stdout__.write(msg + '\n')
    
def redirect_stdout(logfile_path):
    from quickstats import cached_import
    ROOT = cached_import("ROOT")
    sys.stdout = open(logfile_path, 'w')
    ROOT.gSystem.RedirectOutput(logfile_path)

def restore_stdout():
    from quickstats import cached_import
    ROOT = cached_import("ROOT")
    if sys.stdout != sys.__stdout__:
        sys.stdout.close()
    sys.stdout = sys.__stdout__
    ROOT.gROOT.ProcessLine('gSystem->RedirectOutput(0);')

def redirect_stdout_test(func):
    """Redirect stdout to a log file"""
    from quickstats import cached_import
    ROOT = cached_import("ROOT")
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        logfile_path = kwargs.get('logfile_path', None)
        if logfile_path is not None:
            sys.stdout = open(logfile_path, 'w')
            ROOT.gSystem.RedirectOutput(logfile_path)
            value = func(*args, **kwargs)
            sys.stdout.close()
            sys.stdout = sys.__stdout__
            ROOT.gROOT.ProcessLine('gSystem->RedirectOutput(0);')
            return value
        else:
            return func(*args, **kwargs)
    return wrapper_timer

def json_load(fp, *args, **kwargs):
    try:
        data = json.load(fp, *args, **kwargs)
    except Exception:
        raise RuntimeError(f"broken json input: {fp}")
    return data

def parse_config(source:Optional[Union[Dict, str]]=None):
    if source is None:
        return {}
    elif isinstance(source, str):
        with open(source, 'r') as f:
                config = json.load(f)
        return config
    elif isinstance(source, dict):
        return source
    else:
        raise ValueError("invalid config input")
        
class NpEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder for handling NumPy data types in JSON serialization.

    This custom JSONEncoder subclass is designed to handle NumPy data types 
    (such as np.integer, np.floating, and np.ndarray) during JSON serialization. 
    
    Note:
        To use this custom encoder, you can pass it as the 'cls' argument when 
        calling the json.dumps() function or json.dump() method.

    Example:
        import json
        import numpy as np

        # Create a dictionary with NumPy data types
        data = {
            'integer': np.int64(42),
            'floating': np.float64(3.14),
            'array': np.array([1, 2, 3])
        }

        # Serialize the dictionary using the NpEncoder
        json_string = json.dumps(data, cls=NpEncoder)

        # Deserialize the JSON string
        decoded_data = json.loads(json_string)

        # The NumPy data types are now properly serialized and deserialized
        print(decoded_data['integer'])  # outputs: 42
        print(decoded_data['floating'])  # outputs: 3.14
        print(decoded_data['array'])  # outputs: [1, 2, 3]
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

    
def update_nested_dict(d: Dict, u: Dict) -> Dict:
    """
    Recursively updates nested dictionaries.

    Parameters
    ----------
    d : Dict
        The dictionary to be updated.
    u : Dict
        The dictionary containing updates.

    Returns
    -------
    Dict
        The updated dictionary.

    Notes
    -----
    If a key exists in `u` but not in `d`, the key-value pair from `u` is added to `d`.
    """
    for k, v in u.items():
        if isinstance(d.get(k, None), collections.abc.Mapping) and isinstance(v, collections.abc.Mapping):
            d[k] = update_nested_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def combine_dict(d: Optional[Dict] = None, u: Optional[Dict] = None) -> Dict:
    """
    Creates a deep copy of two dictionaries and combines their contents.

    Parameters
    ----------
    d : Dict, optional
        The primary dictionary. Default is None.
    u : Dict, optional
        The dictionary containing updates. If `None`, the function returns a 
        deep copy of `d`. Default is None.

    Returns
    -------
    Dict
        The combined dictionary.
    """
    d_copy = copy.deepcopy(d) if d is not None else {}
    if u is None:
        return d_copy

    u_copy = copy.deepcopy(u)
    return update_nested_dict(d_copy, u_copy)
    
def str_list_filter(source:List[str], patterns:List[str], inclusive:bool=True):
    if inclusive:
        result = [s for p in patterns for s in source if fnmatch.fnmatch(s, p)]
        return sorted(list(set(result)))
    else:
        result = set(source)
        for p in patterns:
            result &= set([s for s in source if not fnmatch.fnmatch(s, p)])
        return sorted(list(result))

def get_class_that_defined_method(meth):
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)
    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__', None) is not None and getattr(meth.__self__, '__class__', None)):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
                      None)
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)

def batch_makedirs(dirnames:Union[str, List[str], Dict[str, str]]) -> None:
    """
    Create multiple directories in a batch. 

    This function accepts a single directory name as a string, a list of directory 
    names, or a dictionary where the values are directory names. It then creates 
    these directories if they do not already exist.

    Parameters
    ----------
    dirnames : Union[str, List[str], Dict[str, str]]
        The directory name(s) to be created. 
        - If it's a string, a single directory will be created.
        - If it's a list, each element is treated as a directory name.
        - If it's a dictionary, each value is treated as a directory name.

    Raises
    ------
    ValueError
        If `dirnames` is not a string, a list, or a dictionary.

    Examples
    --------
    >>> batch_makedirs('new_dir')
    >>> batch_makedirs(['new_dir1', 'new_dir2'])
    >>> batch_makedirs({'dir1': 'new_dir1', 'dir2': 'new_dir2'})
    """
    if isinstance(dirnames, str):
        dirnames = [dirnames]
    elif isinstance(dirnames, dict):
        dirnames = list(dirnames.values())

    if isinstance(dirnames, list):
        for dirname in dirnames:
            abs_dirname = os.path.abspath(dirname)
            os.makedirs(abs_dirname, exist_ok=True)
    else:
        raise ValueError('invalid format for "dirnames"')

def set_scripts_path(scripts_path, undo=False):
    if (scripts_path in sys.path) and undo:
        sys.path.remove(scripts_path)
        os.environ["PYTHONPATH"].replace(scripts_path+":","")
        
    if (scripts_path not in sys.path) and (not undo):
        sys.path.insert(0, scripts_path)
        os.environ["PYTHONPATH"] = scripts_path + ":" + os.environ.get("PYTHONPATH", "")
        
def is_valid_file(filename: Optional[str]) -> bool:
    """
    Check if a given file is valid based on the following criteria:
    
    1. The filename is not empty or None.
    2. The file exists at the specified path.
    3. In case of a ROOT file (with ".root" extension), check if the file is corrupt.
    4. For non-ROOT files, check if the file is a regular file and is not empty.
    
    Parameters:
    ----------
    filename : Optional[str]
        The path to the file to validate.
    
    Returns:
    -------
    bool
        True if the file is valid based on the criteria above, False otherwise.
    """
    if not filename:
        return False
    
    if not os.path.exists(filename):
        return False
    
    ext = os.path.splitext(filename)[-1].lower()  # Lowercase the extension to handle case insensitivity
    
    if ext == ".root":
        try:
            from quickstats.utils.root_utils import is_corrupt
            return not is_corrupt(filename)
        except ImportError:
            # Handle the case where the is_corrupt function or module cannot be imported
            raise ImportError("Could not import is_corrupt from quickstats.utils.root_utils")
    
    # Check if the file is a regular file and has a non-zero size
    return os.path.isfile(filename) and os.path.getsize(filename) > 0

def remove_list_duplicates(seq: List[Any], keep_order: bool = True) -> List[Any]:
    """
    Remove duplicates from a list while optionally preserving the order of elements.
    
    Parameters:
    ----------
    seq : List[Any]
        The list from which to remove duplicates.
    keep_order : bool, optional
        If True (default), the order of elements in the original list is preserved.
        If False, the order is not preserved, which may result in a faster operation.
    
    Returns:
    -------
    List[Any]
        A new list with duplicates removed.
        If keep_order is True, the original order of elements is preserved.
        If keep_order is False, the order is not guaranteed.
    """
    # taken from https://stackoverflow.com/questions/480214/how-do-i-remove-duplicates-from-a-list-while-preserving-order
    if keep_order:
        seen = set()
        seen_add = seen.add
        # List comprehension to filter out duplicates while preserving order
        return [x for x in seq if not (x in seen or seen_add(x))]
    else:
        # Convert to a set to remove duplicates, then back to a list
        return list(set(seq))
    
def format_delimiter_enclosed_text(text:str, delimiter:str, width:int=10, indent_str:str="\t",
                                   upper_margin:int=1, lower_margin:int=1):
    full_line_width = 2 * width + ( len(text) if (len(text) > 2 * width) else (2 * width) ) + 2
    full_line = delimiter * full_line_width
    line = delimiter * width
    result = "\n"*upper_margin + f"{indent_str} {full_line}\n"
    if len(text) > 2 * width:
        result += f"{indent_str} {line} {text} {line}\n"
    else:
        result += f"{indent_str} {line}{text.center(2*width+2)}{line}\n"
    result += f"{indent_str} {full_line}" + "\n"*lower_margin
    return result

def insert_periodic_substr(s:str, every:int=64, substr:str='\n'):
    return substr.join(s[i:i+every] for i in range(0, len(s), every))
        
def format_display_string(s:str, indent:str="", linebreak:int=80, skipfirst:bool=False):
    if len(indent) >= linebreak:
        raise RuntimeError("size of indentation is greater linebreak")
    substr = "\n" + indent
    every = linebreak - len(indent)
    ss = insert_periodic_substr(s, every, substr)
    if not skipfirst:
        return indent + ss
    return ss

def itemize_dict(d:Dict, separator:str=": ", leftmargin:int=0, linebreak:int=100):
    max_key_size = max([len(k) for k in d.keys()])
    bullet_size = max_key_size + len(separator)
    indent_size = leftmargin + bullet_size
    text_size = linebreak - indent_size
    if text_size <= 0:
        raise RuntimeError("size of indentation is greater linebreak")
    texts = []
    substr = "\n" + " " * indent_size
    for k, v in d.items():
        v = v.replace("\n", "")
        text = "{0:>{1}}".format(k + separator, indent_size) + insert_periodic_substr(v, text_size, substr)
        texts.append(text)
    return "\n".join(texts) + "\n"

def filter_by_wildcards(targets: List[str], conditions: Optional[Union[str, List[str]]] = None, exclusion: bool = False) -> List[str]:
    """
    Filters a list of string targets based on wildcard conditions.

    This method filters a list of targets based on provided wildcard patterns.
    It can either return targets that match the conditions or exclude them.

    Parameters
    ----------
    targets : List[str]
        A list of string targets to be filtered.
    conditions : Union[str, List[str]], optional
        Wildcard patterns used for filtering. If a string is provided,
        it is split by commas into individual conditions.
    exclusion : bool
        If True, the method returns targets that do not match the 
        conditions. If False, it returns targets that match the conditions.
        Defaults to False.

    Returns
    -------
    List[str]
        A filtered list of string targets based on the provided conditions.

    Examples
    --------
    >>> filter_by_wildcards(['apple', 'banana', 'cherry'], 'a*')
    ['apple']

    >>> filter_by_wildcards(['apple', 'banana', 'cherry'], 'a*', exclusion=True)
    ['banana', 'cherry']

    >>> filter_by_wildcards(['apple', 'banana', 'cherry'], ['a*', '*rr*'])
    ['apple', 'cherry']

    """
    if not conditions:
        return targets

    if isinstance(conditions, str):
        conditions = conditions.split(',')
    
    if exclusion:
        return [target for target in targets if not any(fnmatch.fnmatch(target, condition) for condition in conditions)]
    
    return [target for target in targets if any(fnmatch.fnmatch(target, condition) for condition in conditions)]

def set_unlimited_stacksize():
    import resource
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    
def in_notebook() -> bool:
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except ImportError:
        return False
    except AttributeError:
        return False
    except NameError:
        return False      # Probably standard Python interpreter    
    return True

def reindex_dataframe(df, index_values:Union[Tuple[List], List],
                      index_levels:Optional[Union[Tuple[str], Tuple[int], str, int]]=None):
    if not isinstance(index_values, tuple):
        index_values = tuple([index_values])
    if index_levels is None:
        index_levels = tuple(range(len(index_values)))
    if isinstance(index_levels, (str, int)):
        index_levels = (index_levels,)
    for values, level in zip(index_values, index_levels):
        mask = np.in1d(values, df.index.get_level_values(level))
        df = df.reindex(np.array(values)[mask], level=level)
    return df

def filter_dataframe_by_index_values(df, index_values:Union[Tuple[List], List],
                                     index_levels:Optional[Union[Tuple[str], Tuple[int], str, int]]=None):
    if not isinstance(index_values, tuple):
        index_values = tuple([index_values])
    if index_levels is None:
        index_levels = tuple(range(len(index_values)))
    if isinstance(index_levels, (int, str)):
        index_levels = (index_levels,)
    for values, level in zip(index_values, index_levels):
        df = df.loc[df.index.get_level_values(level).isin(values)]
    return df

def parse_config_dict(expr:Optional[Union[str, Dict]]=None):
    from .string_utils import parse_as_dict
    if expr is None:
        return {}
    if isinstance(expr, str):
        return parse_as_dict(expr)
    if isinstance(expr, dict):
        return expr
    raise ValueError(f'expr of type "{type(expr)}" is not convertible to a config dict')

def update_config_dict(orig_dict, new_dict, allow_overlap_keys:bool=True):
    orig_dict = parse_config_dict(orig_dict)
    new_dict = parse_config_dict(new_dict)
    if not allow_overlap_keys:
        overlap_keys = list(set(orig_dict.keys()) & set(new_dict.keys()))
        if overlap_keys:
            raise RuntimeError(f'found overlap keys between two config dict: {", ".join(overlap_keys)}')
    return combine_dict(orig_dict, new_dict)

def list_of_dict_to_dict_of_list(source:List[Dict], use_first_keys:bool=True):
    if not source:
        return {}
    if use_first_keys:
        return {k: [item[k] for item in source] for k in source[0]}
    common_keys = set.intersection(*map(set, source))
    return {k: [item[k] for item in source] for k in common_keys}

def dict_of_list_to_list_of_dict(source:Dict[str, List]):
    return [dict(zip(source, t)) for t in zip(*source.values())]

def save_json(data: Dict, outname: str, indent: int = 2, truncate: bool = False) -> None:
    """
    Serializes a dictionary to a JSON file.

    Parameters:
    data (Dict): The dictionary object to serialize to JSON.
    outname (str): The file path where the JSON output will be saved.
    indent (int): The number of spaces to use for indentation in the JSON file. Default is 2.
    truncate (bool): If True, the file will be truncated at the end of the JSON data. Default is False.
                     Typically not needed unless dealing with file updates where the new data might
                     be shorter than the old data.
    """
    with open(outname, "w") as file:
        json.dump(data, file, indent=indent)
        # truncate the file if the flag is True; this might be useful in case the new JSON data is shorter
        # than any existing data in the file to prevent old data from remaining at the end of the file.
        if truncate:
            file.truncate()

def save_json(data:Dict, outname:str,
                 indent:int=2, truncate:bool=True):
    with open(outname, "w") as file:
        json.dump(data, file, indent=indent)
        if truncate:
            file.truncate()
        
def filter_dataframe_by_column_values(df:"pd.DataFrame", attributes:Dict):
    for attribute, value in attributes.items():
        if (value is None):
            continue
        if (attribute not in df.columns) or len(df) == 0:
            df = df.loc[[]]
            break
        if isinstance(value, (list, tuple)):
            df = df[df[attribute].isin(value)]
        elif isinstance(value, str):
            df = df[df[attribute].str.fullmatch(value)]
        elif isinstance(value, Callable):
            df = df[df[attribute].apply(value)]
        else:
            df = df[df[attribute] == value]
    df = df.reset_index(drop=True)
    return df

class IndentDumper(yaml.Dumper):
    """
    A custom YAML Dumper that allows for increased indentation control.
    """

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        super().increase_indent(flow, False)

def save_yaml(obj: Any, filename: str, indent: int = 2) -> None:
    """
    Saves a Python object to a YAML file with custom indentation.

    Parameters:
    obj (Any): The Python object to serialize and save to YAML.
    filename (str): The path to the file where the YAML output should be written.
    indent (int): The number of spaces to use for indentation. Default is 2.
    """
    with open(filename, 'w') as f:
        yaml.dump(obj, f, Dumper=IndentDumper,
                  default_flow_style=False,
                  sort_keys=False, indent=indent)

def remove_duplicates(lst):
    """
    Removes duplicates from a list while preserving the original order of elements.

    Parameters:
    lst (list): The list from which duplicates are to be removed.

    Returns:
    list: A new list containing the unique elements of the original list in the order they first appeared.
    """
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]
    
def list_diff(list1: List, list2: List) -> List:
    """
    Computes the multiset difference between two lists, considering the frequency of elements.
    
    Args:
        list1 (List[int]): The primary list from which elements will be subtracted.
        list2 (List[int]): The secondary list whose elements are subtracted from the first.
    
    Returns:
        List[int]: A list containing elements from list1 with the counts reduced by the elements in list2.
    """
    # Calculate the difference using Counter, which accounts for element frequencies
    difference_counter = Counter(list1) - Counter(list2)
    return list(difference_counter.elements())


def load_json_or_yaml_file(filepath):
    """
    Load a JSON or YAML file based on the filename extension or content.

    Parameters
    ----------
    filepath : str
        Path to the file to be loaded.

    Returns
    -------
    dict
        Parsed data from the file.

    Examples
    --------
    >>> data = load_json_or_yaml_file('path/to/your/file.json')
    >>> data = load_json_or_yaml_file('path/to/your/file.yaml')
    """
    def is_json(content):
        try:
            json.loads(content)
            return True
        except ValueError:
            return False

    def is_yaml(content):
        try:
            yaml.safe_load(content)
            return True
        except yaml.YAMLError:
            return False

    with open(filepath, 'r') as file:
        content = file.read()

        # Determine file format by extension
        if filepath.endswith('.json'):
            return json.loads(content)
        elif filepath.endswith('.yaml') or filepath.endswith('.yml'):
            return yaml.safe_load(content)
        else:
            # Determine file format by content
            if is_json(content):
                return json.loads(content)
            elif is_yaml(content):
                return yaml.safe_load(content)
            else:
                raise ValueError("File format not recognized or content is invalid.")


def save_dict_to_h5(h5file: Union["h5py.File", str], data: Dict[str, Any], path: str = '') -> None:
    """
    Save a nested dictionary to an HDF5 file.

    Each key in the dictionary is stored as a group or a dataset in the file.
    Nested dictionaries become groups, and non-dictionary values are converted
    to numpy arrays and stored as datasets.

    Parameters:
        h5file (h5py.File): An open HDF5 file.
        data (dict): A dictionary with string keys. Nested dictionaries will be
                     stored as groups; other values will be stored as datasets.
        path (str): The current path in the HDF5 file (used internally for recursion).
    """
    
    if isinstance(h5file, str):
        import h5py
        with h5py.File(h5file, 'w') as file:
            save_dict_to_h5(file, data, path)
        return
        
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError(f"Key {key} is not a string.")

        current_path = f"{path}/{key}" if path else key
        if isinstance(value, dict):
            h5file.create_group(current_path)
            save_dict_to_h5(h5file, value, path=current_path)
        else:
            try:
                arr = np.array(value)
                h5file.create_dataset(current_path, data=arr)
            except Exception as e:
                raise ValueError(f"Failed to save dataset at {current_path}: {e}") from e

def load_dict_from_h5(h5file: Union["h5py.File", str], path: str = '') -> Dict[str, Any]:
    """
    Load a nested dictionary of arrays from an HDF5 file.

    If h5file is a string, it is interpreted as a filename and the file is opened in read mode.
    The function recursively reads groups as nested dictionaries and datasets as numpy arrays.

    Parameters:
        h5file (h5py.File or str): An open HDF5 file or a filename.
        path (str): The current path within the HDF5 file (used internally for recursion).

    Returns:
        dict: A nested dictionary with keys corresponding to groups/datasets.
              Groups are represented as dictionaries; datasets are returned as numpy arrays.
    """
    import h5py
    
    if isinstance(h5file, str):
        with h5py.File(h5file, 'r') as file:
            result = load_dict_from_h5(file, path)
        return result
    
    node = h5file[path] if path else h5file

    if isinstance(node, h5py.Group):
        result: Dict[str, Any] = {}
        for key in node.keys():
            subpath = f"{path}/{key}" if path else key
            result[key] = load_dict_from_h5(h5file, subpath)
        return result

    elif isinstance(node, h5py.Dataset):
        return node[()]
    else:
        raise ValueError(f"Unsupported HDF5 node type at path: {path}")