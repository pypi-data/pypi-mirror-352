from typing import Dict, List
import copy

from pydantic import ValidationInfo

from quickstats import check_type
from quickstats.utils.common_utils import load_json_or_yaml_file

def resolve_field_import(values: List, info: ValidationInfo) -> List:
    assert isinstance(values, list), f'{info.field_name} must be a list'
    resolved_values = []
    for value in values:
        if isinstance(value, str):
            resolved_values.append(load_json_or_yaml_file(value))
        else:
            resolved_values.append(value)
    return resolved_values

def resolve_model_import(data:Dict, keywords:List[str]):
    resolved_data = {}
    for key, value in data.items():
        value = copy.deepcopy(value)
        if (key not in keywords):
            if key not in resolved_data:
                resolved_data[key] = value
            elif not isinstance(value, list):
                raise ValueError(f'Multiple values found for the "{key}".')
            else:
                resolved_data[key].extend(value)
        else:
            filenames = value
            if not check_type(filenames, List[str]):
                raise ValueError(f'Items to import must be specified by a list of filenames, but got: '
                                 f'{filenames}')
            for filename in filenames:
                imported_data = load_json_or_yaml_file(filename)
                if not isinstance(imported_data, dict):
                    raise ValueError(f'Data imported (from "{filename}") must be a dictionary, but got: '
                                     f'{type(filenames).__name__}')
                for key, value in imported_data.items():
                    if key not in resolved_data:
                        resolved_data[key] = value
                    elif isinstance(resolved_data[key], list) and isinstance(value, list):
                        resolved_data[key].extend(value)
                    else:
                        raise ValueError(f'Cannot override existing value for "{key}" with imported data')
    return resolved_data