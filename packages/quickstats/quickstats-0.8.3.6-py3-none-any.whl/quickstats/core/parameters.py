from typing import Union, Optional, List, Any, Callable, Tuple, Type
from functools import lru_cache
import copy

from quickstats.utils.string_utils import (
    format_aligned_dict,
    format_delimited_dict
)
from .type_validation import get_type_validator, get_annotation_str
from .typing import NOTSET, NOTSETTYPE
from .constraints import BaseConstraint

__all__ = ['Parameter']

def is_mutable(obj):
    return obj.__class__.__hash__ is None

def _deprecation_message(deprecated: Optional[Union[bool, str]] = None) -> Optional[str]:
    if deprecated is None:
        return None
    if isinstance(deprecated, bool):
        return 'deprecated' if deprecated else None
    if isinstance(deprecated, str):
        return deprecated
    return f'{deprecated!r}'

def _format_str(name: Union[str, NOTSETTYPE] = NOTSET,
                default: Any = NOTSET,
                default_factory: Union[Callable, NOTSETTYPE] = NOTSET,
                dtype: type = Any,
                tags: Optional[Tuple[str]] = None,
                description: Optional[str] = None,
                constraints: Optional[Tuple[BaseConstraint]] = None,
                deprecated: Union[bool, str] = False,
                aligned: bool = False,
                linebreak: int = 100):
    name = 'Parameter' if name is NOTSET else name
    attribs = {}
    if default is not NOTSET:
        attribs['default'] = f'{default!r}'
    if default_factory is not NOTSET:
        attribs['default_factory'] = f'{default_factory!r}'
    if tags is not None:
        attribs['tags'] = f'{tags!r}'
    if constraints is not None:
        attribs['constraints'] = f'{constraints!r}'
    if description is not None:
        attribs['description'] = description
    message = _deprecation_message(deprecated)
    if (message is not None):
        attribs['deprecation_message'] = message
    if aligned:
        attrib_str = format_aligned_dict(attribs, left_margin=4, linebreak=linebreak)
        return f'{label}\n{attrib_str}'
    f'{name}({",".join([f"{key}={value!r}" for key, value in attribs.items()])},)'

def Parameter(default: Any = NOTSET,
              *,
              default_factory: Union[Callable, NOTSETTYPE] = NOTSET,
              tags: Optional[List[str]] = None,
              description: Optional[str] = None,
              constraints: Optional[List[BaseConstraint]] = None,
              validate_default: bool = False,
              deprecated: bool = False):
    return ParameterInfo(default=default,
                         default_factory=default_factory,
                         tags=tags,
                         description=description,
                         constraints=constraints,
                         validate_default=validate_default,
                         deprecated=deprecated)

class ParameterInfo:

    __slots__ = (
        'default',
        'default_factory',
        'dtype',
        'tags',
        'description',
        'constraints',
        'deprecated',
        'validate_default',
    )
    
    def __init__(self, default: Any = NOTSET,
                 *,
                 default_factory: Union[Callable, NOTSETTYPE] = NOTSET,
                 name: str = NOTSET,
                 annotation: Type = Any,
                 tags: Optional[Tuple[str]] = None,
                 description: Optional[str] = None,
                 constraints: Optional[Tuple[BaseConstraint]] = None,
                 deprecated: Union[bool, str] = False,
                 validate_default: bool = False):

        if default is not NOTSET and default_factory is not NOTSET:
            raise ValueError('cannot specify both default and default_factory')

        if is_mutable(default):
            raise ValueError('mutable default value is not allowed')
            
        self.default = default
        self.default_factory = default_factory
        self.name = name
        self.annotation = annotation
        if (tags is not None) and not isinstance(tags, tuple):
            tags = tuple(tags)
        self.tags = tags
        self.description = description
        if (constraints is not None) and not isinstance(constraints, tuple):
            constraints = tuple(constraints)
        self.constraints = constraints
        self.deprecated = deprecated
        self.validate_default = validate_default

    def __repr__(self) -> str:
        return _format_str(name=self.name,
                           default=self.default,
                           default_factory=self.default_factory,
                           dtype=self.dtype,
                           tags=self.tags,
                           description=self.description,
                           constraints=self.constraints,
                           deprecated=self.deprecated,
                           aligned=False)
                          
    def __str__(self) -> str:
        return _format_str(name=self.name,
                           default=self.default,
                           default_factory=self.default_factory,
                           dtype=self.dtype,
                           tags=self.tags,
                           description=self.description,
                           constraints=self.constraints,
                           deprecated=self.deprecated,
                           aligned=True)

    def __set_name__(self, name:str) -> None:
        self.name = name

    def __set_annotation__(self, annotation: Type) -> None:
        self.annotation = annotation
        
    @classmethod
    def _repr(cls, label: str = 'Parameter',
              default: Any = NOTSET,
              default_factory: Union[Callable, NOTSETTYPE] = NOTSET,
              dtype: Union[type, NOTSETTYPE] = NOTSET,
              tags: Optional[Tuple[str]] = None,
              description: Optional[str] = None,
              constraints: Optional[Tuple[BaseConstraint]] = None,
              deprecated: Union[bool, str] = False):
        
        attribs = {}
        if dtype is not NOTSET:
            attribs['dtype'] = get_annotation_str(dtype)
        if default is not NOTSET:
            attribs['default'] = str(default)
        if default_factory is not NOTSET:
            attribs['default_factory'] = str(default_factory)
        if tags is not None:
            attribs['tags'] = str(tags)
        if constraints is not None:
            attribs['constraints'] = str(constraints)
        if description is not None:
            attribs['description'] = description
        if (deprecated is not None):
            attribs['deprecated'] = str(deprecated)
        attrib_str = format_delimited_dict(attribs)
        return f'{label}({attrib_str})'

    @property
    def label(self) -> str:
        return 'Parameter'
        
    @property
    def required(self) -> bool:
        return (default is NOTSET) and (default_factory is NOTSET)

    @property
    def validator(self) -> Callable:
        return get_type_validator(self.dtype)

    @property
    def has_default(self) -> bool:
        return self.default is not NOTSET or self.default_factory is not NOTSET    

    def get_default(self, evaluate_factory: bool = True) -> Any:
        if self.default is not NOTSET:
            return self.default
        if (self.default_factory is not NOTSET) and evaluate_factory:
            return self.default_factory()
        return NOTSET

    def type_check(self, value: Any) -> bool:
        return self.validator(value)

    def constraint_check(self, value: Any) -> bool:
        return all(constraint(value) for constraint in self.constraints)