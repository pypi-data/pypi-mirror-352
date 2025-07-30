from typing import Optional, Union, Dict, List, Callable
import os
import re
import copy
import glob
import fnmatch
import itertools
from functools import partial
from collections import ChainMap

import numpy as np

from quickstats import semistaticmethod, DescriptiveEnum
from quickstats.core.typing import Generator
from quickstats.maths.numerics import pretty_float, str_encode_value, str_decode_value, to_string, to_rounded_float
from quickstats.utils.string_utils import remove_whitespace, split_str

signature_regex = {
    'F': r"\d+[.]?\d*",
    'P': r"n?\d+p?\d*",
    'S': r"\w+"
}

signature_parser = {
    'F': pretty_float,
    'P': str_decode_value,
    'S': str
}

signature_regex = {
    'F': r"\d+[.]?\d*",
    'P': r"n?\d+p?\d*",
    'S': r"\w+"
}

signature_parser = {
    'F': pretty_float,
    'P': str_decode_value,
    'S': str
}

values_regex = r"(?:\[(?P<space>[^\]]*)\])?(?P<args>.*)"

class MatchMode(DescriptiveEnum):
    
    Numerical = (0, "Match by value", lambda x, y: to_rounded_float(x) == to_rounded_float(y))
    Wildcard  = (1, "Match by wildcard", lambda x, y: fnmatch.fnmatch(to_string(x), to_string(y)))

    def __new__(cls, value:int, description:str, match_func:Callable):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.match_func = match_func
        return obj

class ParamParser:
    
    DEFAULT_FORMAT_STR = r"[\.\w-]+"
    
    DEFAULT_FILE_EXT = ".root"
    
    @property
    def format_str(self):
        return self._format_str
    
    @format_str.setter
    def format_str(self, val):
        if val is None:
            self._format_str = self.DEFAULT_FORMAT_STR
        else:
            self._format_str = val
        self.filename_regex   = self.get_filename_regex(self._format_str, self.file_ext)
        self.attribute_parser = self.get_attribute_parser(self._format_str)
        
    @property
    def file_ext(self):
        return self._file_ext
    
    @file_ext.setter
    def file_ext(self, val):
        if val is None:
            self._file_ext = self.DEFAULT_FILE_EXT
        else:
            if not val.startswith("."):
                self._file_ext = f".{val}"
            else:
                self._file_ext = val

    def __init__(self, format_str:Optional[str]=None,
                 param_str:Optional[str]=None,
                 file_ext:Optional[str]=None,
                 allow_none:bool=True):
        self.allow_none = allow_none
        self.setup(format_str, param_str, file_ext)
    
    def setup(self, format_str:Optional[str]=None,
              param_str:Optional[str]=None,
              file_ext:Optional[str]=None):
        self.file_ext   = file_ext
        self.format_str = format_str
        self.param_str  = param_str
        self.param_names = self._get_param_names(self.format_str, self.param_str)

    @semistaticmethod
    def _get_param_names(self, format_str:Optional[str]=None,
                        param_str:Optional[str]=None):
        ext_param_names = self._get_format_str_attributes(format_str)
        int_param_names = self._get_param_str_attributes(param_str)
        if set(int_param_names) & set(ext_param_names):
            raise RuntimeError("internal and external parameters are not mutually exclusive")
        return sorted(int_param_names + ext_param_names)
            
    @staticmethod
    def get_signature_map(format_str:str):
        attribute_groups = re.findall(r"<(\w+)\[(\w)\]>", format_str)
        signature_map = {}
        for group in attribute_groups:
            attribute, signature = group[0], group[1]
            signature_map[attribute] = signature
        return signature_map
    
    @staticmethod
    def get_filename_regex(format_str:str, ext:Optional[str]=None):
        if ext is None:
            ext = ParamParser.DEFAULT_FILE_EXT    
        expr = format_str
        signature_map = ParamParser.get_signature_map(format_str)
        for attribute, signature in signature_map.items():
            attribute_expr = signature_regex.get(signature.upper(), None)
            if expr is None:
                raise ValueError(f"unknown signature `{signature}`")
            group_expr = f"(?P<{attribute}>{attribute_expr})"
            expr = expr.replace(f"<{attribute}[{signature}]>", group_expr)
        expr += (ext.replace('.', r'\.') + "$")
        regex = re.compile(expr)
        return regex
   
    @staticmethod
    def sort_param_points(param_points:List, attributes:Optional[List]=None):
        if attributes is None:
            attributes = list(param_points[0]['parameters'])
        key = lambda d: tuple(d['parameters'][attrib] for attrib in attributes)
        return sorted(param_points, key=key)
    
    @semistaticmethod
    def get_attribute_parser(self, format_str:str):
        attribute_parser = {}
        signature_map = self.get_signature_map(format_str)
        for attribute, signature in signature_map.items():
            parser = signature_parser.get(signature, None)
            if parser is None:
                raise ValueError(f"unknown signature `{signature}`")
            attribute_parser[attribute] = parser
        return attribute_parser
    
    @staticmethod
    def _get_param_str_attributes(param_str:Optional[str]=None):
        if param_str is None:
            return []
        attributes = []
        idp_param_strs = split_str(param_str, sep=';', remove_empty=True)
        for idp_param_str in idp_param_strs:
            param_expr_list = split_str(idp_param_str, sep=',', remove_empty=True)
            for expr in param_expr_list:
                tokens = split_str(expr, sep='=')
                if len(tokens) not in [1, 2]:
                    raise ValueError('invalid expression for parameterisation')
                attribute = tokens[0]
                if attribute not in attributes:
                    attributes.append(attribute)
        return attributes
    
    @semistaticmethod
    def _get_format_str_attributes(self, format_str:Optional[str]=None):
        if format_str is None:
            return []
        attribute_parser = self.get_attribute_parser(format_str)
        return list(attribute_parser)

    @staticmethod
    def parse_param_str(param_str: Optional[str] = None,
                        unique: bool = False) -> Generator[dict, None, None]:
        if param_str is None:
            return
        seen = set() if unique else None  # Only use 'seen' set if uniqueness check is enabled
    
        # components separated by ; are subject to independent conditions
        ind_components = split_str(param_str, sep=';', remove_empty=True)
        
        for component in ind_components:
            param_values = {}
            param_expr_list = split_str(component, sep=',', remove_empty=True, use_paranthesis=True)
            for expr in param_expr_list:
                tokens = split_str(expr, sep='=')
                if len(tokens) == 1:
                    param_name = tokens[0]
                    if param_name in param_values:
                        raise RuntimeError(f"profiled parameter {param_name} appeared more than once in the parameter "
                                           f"expression: {param_str}")
                    param_values[param_name] = [None]
                    continue
                if len(tokens) != 2:
                    raise ValueError('invalid expression for parameterisation')
                param_name, values_expr = tokens
                if param_name not in param_values:
                    param_values[param_name] = np.array([])
                if None in param_values[param_name]:
                    raise RuntimeError(f"the parameter {param_name} is being profiled and non-profiled at the same time "
                                       f"in the parameter expression: {param_str}")
                match = re.match(values_regex, values_expr)
                if not match:
                    raise ValueError(f'invalid value expression: {values_expr}')
                space = match.group('space')
                if space is not None:
                    if space == 'ln':
                        log_base = np.e
                    elif space == 'log':
                        log_base = 10
                    elif space.startswith('log'):
                        log_base = float(space.replace('log', ''))
                    else:
                        raise ValueError(f'invalid space expression: {space}')    
                else:
                    log_base = None    
                args = match.group('args')
                if args.startswith('(') and args.endswith(')'):
                    values_expr_list = split_str(args[1:-1], sep=',')
                else:
                    values_expr_list = [args]
                for expr in values_expr_list:
                    tokens = split_str(expr, sep='_')
                    if len(tokens) == 1:
                        if log_base is not None:
                            values = [log_base ** float(tokens[0])]
                        else:
                            values = [float(tokens[0])]
                    elif len(tokens) == 3:
                        if log_base is not None:
                            start = float(tokens[0])
                            stop = float(tokens[1])
                            num = int(tokens[2])
                            values = np.logspace(start, stop, num, base=log_base)
                        else:
                            poi_min = float(tokens[0])
                            poi_max = float(tokens[1])
                            poi_step = float(tokens[2])
                            values = np.arange(poi_min, poi_max + poi_step, poi_step)
                    else:
                        raise ValueError('invalid expression for parameterisation')
                    param_values[param_name] = np.concatenate([param_values[param_name], values])
    
            param_names = list(param_values.keys())
            combinations = [np.array(param_values[param_name]) for param_name in param_names]
            combinations = [(arr.round(decimals=8) + 0.0) if arr[0] is not None else arr for arr in combinations]
            combinations = [np.unique(arr) for arr in combinations]
            
            for combination in itertools.product(*combinations):
                param_point = tuple((k, v) for k, v in zip(param_names, combination))
                if unique:
                    if param_point not in seen:
                        seen.add(param_point)
                        yield {k: v for k, v in zip(param_names, combination)}
                else:
                    yield {k: v for k, v in zip(param_names, combination)}
    
    @staticmethod
    def val_encode_parameters(parameters:Dict):
        tokens = []
        for param, value in parameters.items():
            if value is None:
                token = f"{param}"
            else:
                token = f"{param}={round(value, 8)}"
            tokens.append(token)
        return ",".join(tokens)
    
    @staticmethod
    def str_encode_parameters(parameters:Dict):
        encoded_str_list = []
        for param, value in parameters.items():
            if isinstance(value, float):
                value = str_encode_value(round(value, 8))
            encoded_str = f"{param}_{value}"
            encoded_str_list.append(encoded_str)
        return "_".join(sorted(encoded_str_list))

    def get_external_param_points(self, dirname:str="",
                                  filter_expr:Optional[str]=None,
                                  exclude_expr:Optional[str]=None):
        if os.path.isdir(dirname):
            filenames = glob.glob(os.path.join(dirname, '*'))
        else:
            filenames = glob.glob(dirname)
        param_points = []
        for filename in filenames:
            basename = os.path.basename(filename)
            match = self.filename_regex.match(basename)
            if not match:
                continue
            point = {
                'filename'   : filename,
                'basename'   : os.path.splitext(basename)[0],
                'parameters' : {}
            }
            for key, value in match.groupdict().items():
                parser = self.attribute_parser[key]
                point['parameters'][key] = parser(value)
            param_points.append(point)
        attributes = list(self.attribute_parser)
        param_points = self.sort_param_points(param_points, attributes)
        selected_param_points = self.get_selected_points(param_points, filter_expr,
                                                         exclude_expr, dict_keys="parameters")
        return selected_param_points
    
    def get_internal_param_points(self,
                                  filter_expr:Optional[str]=None,
                                  exclude_expr:Optional[str]=None,
                                  unique: bool = True):
        param_points = self.parse_param_str(self.param_str, unique=unique)
        param_points = list(param_points)
        selected_param_points = self.get_selected_points(param_points,
                                                         filter_expr,
                                                         exclude_expr)
        return selected_param_points
    
    @staticmethod
    def parse_filter_expr(expr:str):
        if expr is None:
            return []
        expr = remove_whitespace(expr)
        match_conditions = []
        # components separated by ; are subject to independent conditions
        ind_components = split_str(expr, sep=';', remove_empty=True)
        for component in ind_components:
            conditions = split_str(component, sep=',', remove_empty=True, use_paranthesis=True)
            match_condition = {}
            for condition in conditions:
                tokens = split_str(condition, sep='=')
                if len(tokens) != 2:
                    raise ValueError(f'invalid sub-expression: {condition}')
                param_name, values_expr = tokens
                if param_name not in match_condition:
                    match_condition[param_name] = []
                if values_expr.startswith('(') and values_expr.endswith(')'):
                    values_expr_list = split_str(values_expr[1:-1], sep=',')
                else:
                    values_expr_list = [values_expr]
                for values_expr in values_expr_list:
                    if "*" in values_expr:
                        match_func = MatchMode.Wildcard.match_func
                    else:
                        match_func = MatchMode.Numerical.match_func
                    match_condition[param_name].append(partial(match_func, y=values_expr))
            match_conditions.append(match_condition)
        return match_conditions

    @semistaticmethod
    def get_selected_points(self, param_points: List,
                            filter_expr:Optional[str]=None,
                            exclude_expr:Optional[str]=None,
                            dict_keys:Optional=None):
        filter_conditions = self.parse_filter_expr(filter_expr)
        exclude_conditions = self.parse_filter_expr(exclude_expr)
        def get_attrib(x):
            if dict_keys is None:
                return x
            if isinstance(dict_keys, str):
                return x[dict_keys]
            if isinstance(dict_keys, list):
                return dict(ChainMap(*[x[k] for k in dict_keys]))
            raise ValueError('invalid value for "dict_keys"')
            
        selected_points = param_points
        if filter_expr is not None:
            selected_points = [point for point in selected_points \
                               if self.is_point_selected(get_attrib(point), filter_conditions)]
        if exclude_expr is not None:
            selected_points = [point for point in selected_points \
                               if not self.is_point_selected(get_attrib(point), exclude_conditions)]
        return selected_points
                    
    @staticmethod
    def is_point_selected(param_point, conditions):
        for condition in conditions:
            selected = True
            for param_name, match_functions in condition.items():
                param_value = param_point[param_name]
                selected &= any(match_func(param_value) for match_func in match_functions)
            if selected:
                return True
        return False
    
    def sanity_check(self, internal_param_points:Dict, external_param_points:Dict):
        if not self.allow_none:
            for int_point in internal_param_points:
                for param_name, param_value in int_point.items():
                    if param_value is None:
                        raise RuntimeError(f"profiled parameter is not allowed ({param_name})")
    
    def get_param_points(self, dirname:str="",
                         filter_expr:Optional[str]=None,
                         exclude_expr:Optional[str]=None):
        external_param_points = self.get_external_param_points(dirname)
        internal_param_points = self.get_internal_param_points()
        self.sanity_check(internal_param_points, external_param_points)
        if len(internal_param_points) == 0:
            internal_param_points = [{}]
        param_points = []
        for ext_point in external_param_points:
            filename = ext_point['filename']
            basename = ext_point['basename']
            ext_params = ext_point['parameters']
            for int_params in internal_param_points:
                param_point = {}
                param_point['filename'] = filename
                param_point['basename'] = basename
                param_point['external_parameters'] = {**ext_params}
                param_point['internal_parameters'] = {**int_params}
                param_points.append(param_point)
        param_points = self.get_selected_points(param_points, filter_expr, exclude_expr,
                                                dict_keys=['internal_parameters', 'external_parameters'])
        return param_points