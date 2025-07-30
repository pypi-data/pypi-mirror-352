from typing import Optional, Union, Dict, List, Any, Tuple
import re

from quickstats import GeneralEnum
from quickstats.maths.numerics import to_bool
from quickstats.utils.regex_utils import varname_pattern
from quickstats.utils.string_utils import split_str, replace_with_mapping
from .settings import (
    RESPONSE_KEYWORD,
    RESPONSE_PREFIX,
    SHAPE_SYST_KEYWORD,
    OBSERVABLE_KEYWORD,
    CATEGORY_KEYWORD,
    COMMON_SYST_DOMAIN_KEYWORD,
    COMMON_SYST_DOMAIN_NAME,
    PROCESS_KEYWORD,
    LT_OP, LE_OP, GT_OP, GE_OP, AND_OP, OR_OP,
    GLOBALOBS_PREFIX,
    CONSTRTERM_PREFIX
)

class WSObjectType(GeneralEnum):
    DEFINED    = 0
    FUNCTION   = 1
    VARIABLE   = 2
    CONSTRAINT = 3

class XMLAttribType(GeneralEnum):
    STR        = 0
    BOOL       = 1
    INT        = 2
    FLOAT      = 3
    STR_LIST   = 4
    INT_LIST   = 5
    FLOAT_LIST = 6

class BracketType(GeneralEnum):
    ROUND  = (1, r"(.+)\((.+)\)")
    SQUARE = (2, r"(.+)\[(.+)\]")
    CURLY  = (3, r"(.+){(.+)}")
    ANGLE  = (4, r"(.+)<(.+)>")
    
    def __new__(cls, value:int, regex:str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.regex = re.compile(regex)
        return obj
    
ConversionOperators = {
    XMLAttribType.STR: str,
    XMLAttribType.BOOL: to_bool,
    XMLAttribType.INT: int,
    XMLAttribType.FLOAT: float,
    XMLAttribType.STR_LIST  : lambda s: split_str(s, sep=',', remove_empty=True),
    XMLAttribType.INT_LIST  : lambda s: split_str(s, sep=',', remove_empty=True, cast=int),
    XMLAttribType.FLOAT_LIST: lambda s: split_str(s, sep=',', remove_empty=True, cast=float)
}

arithmetic_keywords_map = {
    LT_OP: "<",
    LE_OP: "<=",
    GT_OP: ">",
    GE_OP: ">=",
    AND_OP: "%%",
    OR_OP: "||"
}

def fetch_xml_node(nodes:List, tag:str, parent_tag:str, filename:str,
                   allow_missing:bool=False, allow_multiple:bool=False) -> Optional[Union[Dict, List[Dict]]]:
    target_nodes = [node for node in nodes if node['tag'] == tag]
    num_nodes = len(target_nodes)
    if (num_nodes > 1) and (not allow_multiple):
        raise RuntimError(f'Multiple "{tag}" nodes found under the root element "{parent_tag}" in the XML file "{filename}".')
    elif (num_nodes == 0) and (not allow_missing):
        raise RuntimError(f'Missing "{tag}" node under the root element "{parent_tag}" in the XML file "{filename}".')
    elif (num_nodes == 1) and (not allow_multiple):
        return target_nodes[0]
    elif (num_nodes == 0) and (not allow_multiple) and allow_missing:
        return None
    return target_nodes

def translate_arithmetic_keywords(expr: str) -> str:
    return replace_with_mapping(expr, arithmetic_keywords_map)

def translate_special_keywords(expr:str, category:str=None, process:str=None, observable:str=None) -> str:
    expr = expr.replace(RESPONSE_KEYWORD, RESPONSE_PREFIX + SHAPE_SYST_KEYWORD + '_')
    expr = expr.replace(COMMON_SYST_DOMAIN_KEYWORD, COMMON_SYST_DOMAIN_NAME)
    if OBSERVABLE_KEYWORD in expr:
        if not observable:
            raise ValueError(f'Failed to translate the keyword "{OBSERVABLE_KEYWORD}": observable name not specified.')
        expr = expr.replace(OBSERVABLE_KEYWORD, observable)
    if CATEGORY_KEYWORD in expr:
        if not category:
            raise ValueError(f'Failed to translate the keyword "{CATEGORY_KEYWORD}": category name not specified.')
        expr = expr.replace(CATEGORY_KEYWORD, category)
    if PROCESS_KEYWORD in expr:
        if not process:
            raise ValueError(f'Failed to translate the keyword "{PROCESS_KEYWORD}": process name not specified.')
    return expr

def get_xml_node_attrib(node:Dict, attrib_names:Union[str, List[str]],
                        required:bool=True, default:Optional[str]=None,
                        dtype:Union[XMLAttribType, str]='str') -> Any:
    attrbiutes = node['attrib']
    if isinstance(attrib_names, str):
        attrib_names = [attrib_names]
    # handle aliases
    attrib_found = False
    attrib_value = default
    for name in attrib_names:
        if name in attrbiutes:
            if attrib_found:
                raise RuntimeError("Values defined for multiple alises of the same attribute: "
                                  f"{', '.join(attrib_names)}")
            attrib_value = attrbiutes[name]
            attrib_found = True
    if (not attrib_found) and required:
        name_aliases = "/".join([f'"{alias}"' for alias in attrib_names])
        tag = node['tag']
        raise RuntimeError(f'Attribute {name_aliases} not found in the  node "{tag}"')
    if not isinstance(attrib_value, str):
        return attrib_value
    # string cleaning
    attrib_value = re.sub(r'\s+', '', attrib_value)
    # type conversion
    dtype = XMLAttribType.parse(dtype)
    attrib_value = ConversionOperators[dtype](attrib_value)
    # translate xml specific syntax
    if isinstance(attrib_value, str):
        return translate_arithmetic_keywords(attrib_value)
    return attrib_value

def translate_xml_node_attrib(node:Dict, attrib_names:Union[str, List[str]],
                              required:bool=True, default:Optional[str]=None,
                              category:str=None, process:str=None, observable:str=None) -> str:
    expr = get_xml_node_attrib(node, attrib_names, required=required, default=default, dtype='str')
    return translate_special_keywords(expr, category=category, process=process, observable=observable)

def extract_observable_name(expr: str) -> str:
    varnames = re.findall(varname_pattern, expr)
    if len(varnames) != 1:
        raise ValueError(f'Failed to extract variable name from the expression: {expr}')
    return varnames[0]

def decompose_function_expr(expr: str) -> List[str]:
    """Extract dependency terms of a functional expression in RooFit
    """
    start = expr.find("(")
    end = expr.rfind(")")
    if (start < 0) or (end < 0):
        raise RuntimeError(f'Invalid function expression: {expr}')
    tokens = expr[start + 1 : end].split(",")
    if ("expr::" in expr) or ("EXPR::" in expr):
        tokens = tokens[1:]
    return tokens
    
def get_object_name_type(expr: str) -> Tuple[str, str]:
    """Extract the object name and type of the object defined by an expression in RooFit
    """
    if ("::" in expr) and ("(" in expr):
        object_type = "function"
        object_name = expr.split("::")[1].split("(")[0]
    elif ("[" in expr):
        object_type = "variable"
        object_name = expr.split("[")[0]
    elif (":" in expr) and ("::" not in expr):
        raise RuntimeError(f'Syntax error for the expression "{expr}": missing colon pair')
    else:
        object_type = "defined"
        object_name = expr
    # sanity check for the object name
    if not len(re.findall(varname_pattern, object_name)) == 1:
        raise RuntimeError(f'Invalid variable name: {object_name}')
    return object_name, object_type

def item_has_dependent(expr: str, reference_list: List[str]) -> bool:
    """Check if a RooFit expression depends on objects from a reference list
    """
    _, item_type = get_object_name_type(expr)
    if item_type in ['variable', 'defined']:
        return False
    item_list = decompose_function_expr(expr)
    for target_name in item_list:
        for reference_expr in reference_list:
            reference_name, _ = get_object_name_type(reference_expr)
            if target_name == reference_name:
                return True
    return False

def get_glob_name(nuis_name: str) -> str:
    return f"{GLOBALOBS_PREFIX}{nuis_name}"

def get_constr_name(nuis_name: str) -> str:
    return f"{CONSTRTERM_PREFIX}{nuis_name}"

def get_nuis_name_from_constr_name(constr_name: str) -> str:
    return constr_name.replace(CONSTRTERM_PREFIX, "")