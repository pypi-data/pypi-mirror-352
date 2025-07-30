from keyword import iskeyword

from .typing import NOTSET, T

# taken from stl dataclasses.py
ATOMIC_TYPES = frozenset({
    # Common JSON Serializable types
    type(None), #types.NoneType
    bool,
    int,
    float,
    str,
    # Other common types
    complex,
    bytes,
    # Other types that are also unaffected by deepcopy
    type(...),  # types.EllipsisType
    type(NotImplemented), # types.NotImplementedType
    #types.CodeType,
    #types.BuiltinFunctionType,
    #types.FunctionType,
    type,
    range,
    property,
})

def is_mutable(obj) -> bool:
    return obj.__class__.__hash__ is None

def smart_copy(obj: T) -> T:
    if type(obj) in ATOMIC_TYPES:
        return obj
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        # named tuple
        return type(obj)(*[smart_copy(v) for v in obj])
    elif isinstance(obj, (list, tuple, set)):
        return type(obj)(smart_copy(v) for v in obj)
    elif isinstance(obj, dict):
        if hasattr(type(obj), 'default_factory'):
            # obj is a defaultdict, which has a different constructor from
            # dict as it requires the default_factory as its first arg.
            result = type(obj)(getattr(obj, 'default_factory'))
            for k, v in obj.items():
                result[smart_copy(k)] = smart_copy(v)
            return result
        return type(obj)((smart_copy(k),
                          smart_copy(v))
                         for k, v in obj.items())
    elif obj is NOTSET:
        return obj
    raise ValueError(f'copying of object with type {type(obj)} is not allowed')

def is_varname(name: str) -> bool:
    return name.isidentifier() and not iskeyword(name)