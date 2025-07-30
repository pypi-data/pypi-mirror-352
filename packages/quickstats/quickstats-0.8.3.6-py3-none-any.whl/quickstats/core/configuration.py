import _thread
from collections.abc import Mapping
import copy
import fnmatch
import functools
import inspect
import json
from keyword import iskeyword 
import os
from typing import Optional, Any, Callable, List, TypeVar, Union, Dict
import types
import yaml

from .abstract_object import AbstractObject
from .decorators import semistaticmethod
from .metaclasses import MergeAnnotationsMeta
from .type_validation import get_type_validator, get_type_hint_str
from .typing import NOTSET
from quickstats.utils.string_utils import format_aligned_dict


__all__ = ['ConfigComponent', 'ConfigScheme', 'ConfigFile', 'ConfigurableObject', 'ConfigUnit']

# The name of an attribute on the class where we store the ConfigScheme
# objects.  Also used to check if a class is a ConfigurableObject class.
_CONFIGOBJECTS = '__config_objects__'

# The name of an attribute on the class where we store the ConfigComponent
# objects.  Also used to check if a class is a ConfigScheme class.
_CONFIGCOMPONENTS = '__config_components__'

# taken from stl dataclasses.py
_ATOMIC_TYPES = frozenset({
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

T = TypeVar('T')

def _make_copy(obj: T) -> T:
    if type(obj) in _ATOMIC_TYPES:
        return obj
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[_make_copy(v) for v in obj])
    elif isinstance(obj, (list, tuple, set)):
        return type(obj)(_make_copy(v) for v in obj)
    elif isinstance(obj, dict):
        if hasattr(type(obj), 'default_factory'):
            # obj is a defaultdict, which has a different constructor from
            # dict as it requires the default_factory as its first arg.
            result = type(obj)(getattr(obj, 'default_factory'))
            for k, v in obj.items():
                result[_make_copy(k)] = _make_copy(v)
            return result
        return type(obj)((_make_copy(k),
                          _make_copy(v))
                         for k, v in obj.items())
    elif obj == NOTSET:
        return obj
    raise ValueError(f'copying of object with type {type(obj)} is not allowed')

def update_nested_dict(d: Dict, u: Dict) -> Dict:
    for k, v in u.items():
        if isinstance(d.get(k, None), Mapping) and isinstance(v, Mapping):
            d[k] = update_nested_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def _get_extended_object(old_obj: Any, new_obj: Any):
    if type(old_obj) in _ATOMIC_TYPES:
        return new_obj
    elif isinstance(old_obj, tuple) and hasattr(old_obj, '_fields'):
        if isinstance(new_obj, tuple) and hasattr(new_obj, '_fields'):
            return _make_copy(old_obj)._replace(**_make_copy(new_obj)._asdict())
        elif isinstance(new_obj, dict):
            return _make_copy(old_obj)._replace(**_make_copy(new_obj))
        else:
            raise ValueError(f'can not extend namedtuple with object of type {type(new_obj)}')
    elif isinstance(old_obj, (list, tuple)):
        if isinstance(new_obj, (list, tuple)):
            return _make_copy(old_obj) + _make_copy(type(old_obj)(v for v in new_obj))
        else:
            return _make_copy(old_obj) + type(old_obj)([_make_copy(new_obj)])
    elif isinstance(old_obj, dict):
        if isinstance(new_obj, dict):
            old_obj, new_obj = _make_copy(old_obj), _make_copy(new_obj)
            return update_nested_dict(old_obj, new_obj)
        else:
            raise ValueError(f'can not extend dict with object of type {type(new_obj)}')
    elif isinstance(old_obj, set):
        if isinstance(new_obj, set):
            return _make_copy(old_obj).union(_make_copy(new_obj))
        else:
            return _make_copy(old_obj).union(type(old_obj)([_make_copy(new_obj)]))
    raise ValueError(f'extending of object with type {type(old_obj)} is not allowed')

# Copied from "recursive_repr" function in reprlib module
# Probably not useful before but anyway
def _recursive_repr(user_function):
    # Decorator to make a repr function return "..." for a recursive
    # call.
    repr_running = set()

    @functools.wraps(user_function)
    def wrapper(self):
        key = id(self), _thread.get_ident()
        if key in repr_running:
            return '...'
        repr_running.add(key)
        try:
            result = user_function(self)
        finally:
            repr_running.discard(key)
        return result
    return wrapper

def _is_configscheme_class(obj):
    return inspect.isclass(obj) and issubclass(obj, ConfigScheme)

def _is_configcomponent_class(obj):
    return inspect.isclass(obj) and issubclass(obj, ConfigComponent)

def is_config_scheme(obj):
    """Returns True if obj is a config scheme or an instance of a
    config scheme."""
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, _CONFIGCOMPONENTS)

def _get_annotations(obj, cls:Optional=None):
    if not hasattr(obj, '__annotations__'):
        return {}
    annotations = getattr(obj, '__annotations__')
    if cls is None:
        return annotations
    return {key: annotation for key, annotation in annotations.items()
            if isinstance(annotation, cls)}

def _get_config_component_annotations(obj):
    return _get_annotations(obj, ConfigComponent)

def _get_config_unit_annotations(obj):
    return _get_annotations(obj, ConfigUnit)

# copied from dataclasses.py
def as_dict(obj):
    if not isinstance(obj, ConfigScheme):
        raise TypeError("asdict() should be called on ConfigScheme instances")
    return _asdict_inner(obj)

# copied from dataclasses.py
def _asdict_inner(obj):
    if type(obj) in _ATOMIC_TYPES:
        return obj
    elif isinstance(obj, ConfigScheme):
        return {
            _asdict_inner(key): _asdict_inner(getattr(obj, key))
            for key in obj.get_components(remove_dummy=True)
        }
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        # obj is a namedtuple.
        return type(obj)(*[_asdict_inner(v) for v in obj])
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_asdict_inner(v) for v in obj)
    elif isinstance(obj, dict):
        if hasattr(type(obj), 'default_factory'):
            # obj is a defaultdict, which has a different constructor from
            # dict as it requires the default_factory as its first arg.
            result = type(obj)(getattr(obj, 'default_factory'))
            for k, v in obj.items():
                result[_asdict_inner(k)] = _asdict_inner(v)
            return result
        return type(obj)((_asdict_inner(k),
                          _asdict_inner(v))
                         for k, v in obj.items())
    return _make_copy(obj)

def is_mutable(obj):
    return obj.__class__.__hash__ is None

def _match_components(name:str, components:Dict[str, "ConfigComponent"]):
    matched_components = [component for component in components.values()
                          if component.pattern is not None and
                          fnmatch.fnmatch(name, component.pattern)]
    return matched_components

def is_valid_variable_name(name:str):
    return name.isidentifier() and not iskeyword(name)

class ConfigComponent:
    def __init__(self, dtype: Union[type, str], required: bool = False,
                 default: Optional[Any] = NOTSET,
                 default_factory: Optional[Callable] = NOTSET,
                 description: Optional[str] = None,
                 constraints: Optional[List['BaseConstraint']] = None,
                 name: Optional[str] = None,
                 pattern: Optional[str] = None):
        """
        Args:
            dtype: The data type for the configuration component.
            required: Whether the configuration component is required.
            default: The default value for the component, if not set to NOTSET.
            default_factory: A callable that returns the default value, if not set to NOTSET.
            description: A human-readable description of the component.
            constraints: A list of constraints that the component's value must satisfy.
            name: Name of the component.
            pattern: Name pattern for component with undetermined name.
        """
        
        if default is not NOTSET and default_factory is not NOTSET:
            raise ValueError('Cannot specify both default and default_factory.')
            
        self.name = name
        self.pattern = pattern
        self._dtype = dtype
        self._validator = get_type_validator(dtype)
        self.required = required
        self.default = default
        self.default_factory = default_factory
        self.description = description
        self.constraints = constraints or []

    def __repr__(self) -> str:
        return self.get_explain_text()

    def __copy__(self):
        new_obj = self.__class__(
            dtype=self._dtype,
            required=self.required,
            default=self._default,
            default_factory=self._default_factory, 
            description=self.description,
            constraints=copy.copy(self.constraints),
            name=self.name,
            pattern=self.pattern,
        )
        return new_obj

    def __eq__(self, other):
        if not isinstance(other, ConfigComponent):
            return False
        return self.__dict__ == other.__dict__
    
    @property
    def dtype(self) -> Union[type, str]:
        return self._dtype

    @property
    def validator(self) -> Callable:
        return self._validator

    @property
    def default(self) -> Any:
        return self._default
    
    @default.setter
    def default(self, value):
        if value is not NOTSET:
            if is_mutable(value):
                raise ValueError(f'mutable default {type(value)} is not allowed: use default_factory instead')
            self._validator(value)
        self._default = value
            
    @property
    def default_factory(self) -> Optional[Callable]:
        return self._default_factory
    
    @default_factory.setter
    def default_factory(self, factory: Callable):
        if factory is not NOTSET:
            self._validator(factory())
        elif _is_configscheme_class(self.dtype):
            factory = self.dtype
        self._default_factory = factory

    def get_default(self) -> Any:
        if self.default is not NOTSET:
            # NB: probably not necessary to make a copy
            return _make_copy(self.default)
        if self.default_factory is not NOTSET:
            return self.default_factory()
        return NOTSET

    def type_check(self, value: Any) -> bool:
        return self._validator(value)

    def constraint_check(self, value: Any) -> bool:
        return all(constraint(value) for constraint in self.constraints)

    def validate(self, value: Any) -> None:
        undetermined = self.pattern is not None
        if undetermined:
            name_str = f' "{self.pattern}"'
        else:
            name_str = f' "{self.name}"' if self.name else ""
        
        if value is NOTSET:
            if self.required:
                raise ValueError(f'Missing value for the required config component{name_str}.')
            return None
        
        if not self.type_check(value):
            type_hint_str = get_type_hint_str(self._dtype)
            raise ValueError(f'Type check failed for the config component{name_str}. Allowed type: {type_hint_str}')
        
        if not self.constraint_check(value):
            constr_str = ', '.join(repr(constr) for constr in self.constraints)
            raise ValueError(f'Constraint check failed for the config component{name_str}. Required constraints: {constr_str}')
            
    def has_default(self) -> bool:
        return self._default is not NOTSET or self._default_factory is not NOTSET
    
    def get_explain_text(self, indent_level: int = 0, indent_size: int = 4, linebreak: int = 100,
                         with_default:bool=True, with_description:bool=True) -> str:
        """Generates and returns help text for the configuration component."""
        indent = " " * indent_level * indent_size
        if self.pattern is not None:
            name = self.pattern
        else:
            name = self.name or "UnnamedComponent"
        if _is_configscheme_class(self.dtype):
            scheme_text =  self.dtype.get_explain_text(indent_level=indent_level,
                                                       indent_size=indent_size,
                                                       linebreak=linebreak)
            return f"{indent}{name}\n{scheme_text}"
        components = {
            "Type": get_type_hint_str(self.dtype),
            "Required": str(self.required)
        }
        if with_default:
            components['Default'] = str(self.get_default()) if self.has_default() else "No default"
        if with_description:
            components['Description'] = self.description or "No description provided"
        left_margin = indent_level * indent_size + 2
        attributes_text = format_aligned_dict(components, left_margin=left_margin, linebreak=linebreak)
        # TODO: display level?
        return f"{indent}{name}\n{attributes_text}"

    def explain(self, linebreak: int = 100,
                with_default:bool=True,
                with_description:bool=True) -> None:
        print(self.get_explain_text(linebreak=linebreak,
                                    with_default=with_default,
                                    with_description=with_description))

    def copy(self):
        return self.__copy__()

class MergeConfigAnnotationsMeta(MergeAnnotationsMeta):
    def __new__(cls, name, bases, dct):
        def update_names(annotations):
            for name, annotation in annotations.items():
                if isinstance(annotation, ConfigComponent):
                    if annotation.name is None:
                        annotation.name = name
        for base in bases:
            if hasattr(base, '__annotations__'):
                update_names(base.__annotations__)
        annotations = dct.get('__annotations__', {})
        update_names(annotations)
        dct['__annotations__'] = annotations
        dct[_CONFIGCOMPONENTS] = None
        return super().__new__(cls, name, bases, dct)

class ConfigScheme(AbstractObject, metaclass=MergeConfigAnnotationsMeta):

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value:Optional[str]=None):
        if value is None:
            self._name = self.__class__.__name__
        else:
            self._name = value

    def __init__(self, name:Optional[str]=None,
                 required_components:Optional[List[str]]=None,
                 verbosity:str="INFO"):
        super().__init__(verbosity=verbosity)
        self.name = name
        self._create_components(required_components=required_components)
        self.reset_values()

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        fields = []
        components = self.get_components()
        if not components:
            return "Empty Configuration"
        for key, component in components.items():
            if component.pattern is not None:
                continue
            if key not in self.__dict__:
                continue
            value = getattr(self, key)
            if value is NOTSET:
                value = 'NOTSET'
            elif isinstance(value, str):
                value = f'"{value}"'
            fields.append(f"{key}={value}")
        return f"{class_name}({', '.join(fields)})"

    def __contains__(self, item:str) -> bool:
        return self.has_component(item)

    def __getitem__(self, key:str):
        return self.get_value(key)
    
    def __setitem__(self, key:str, value: Any):
        self.set_value(key, value)

    def __iter__(self):
        components = self.get_components(remove_dummy=True)
        return iter(components)
        
    def _create_components(self, required_components:Optional[List[str]]=None) -> None:
        # create config components based on the class annotations
        annotations = _get_config_component_annotations(type(self))
        if required_components is None:
            required_components = list(annotations)
        components = {}
        for name, component in annotations.items():
            # TODO: extend to wild cards and multi-level
            if name not in required_components:
                continue
            components[name] = component.copy()
        setattr(self, _CONFIGCOMPONENTS, components)

    def reset_values(self) -> None:
        # set all config fields with default values
        components = self.get_components()
        for name, component in components.items():
            self.reset_value(name)

    def reset_value(self, name:str) -> None:
        # set config field with default value
        component = self.get_component(name)
        if component is None:
            return None
        default = component.get_default()
        if isinstance(default, ConfigScheme):
            default.name = name
        setattr(self, name, default)
            
    @semistaticmethod
    def get_explain_text(self, components:Optional[List[str]]=None,
                         indent_level: int = 0, indent_size: int = 4, linebreak: int = 100,
                         with_default:bool=True, with_description:bool=True) -> str:
        if inspect.isclass(self):
            title = self.__name__
            all_components = _get_config_component_annotations(self)
        else:
            title = self.name
            all_components = self.get_components()
        # top level
        if indent_level == 0:
            explain_text = title + '\n'
        else:
            explain_text = ""
        for key, component in all_components.items():
            if (components is not None) and (key not in components):
                continue
            explain_text += component.get_explain_text(indent_level=indent_level+1,
                                                       indent_size=indent_size,
                                                       linebreak=linebreak,
                                                       with_default=with_default,
                                                       with_description=with_description)
        return explain_text

    @semistaticmethod
    def explain(self, components:Optional[List[str]]=None,
                linebreak: int = 100,
                with_default:bool=True,
                with_description:bool=True) -> None:
        print(self.get_explain_text(components=components,
                                    linebreak=linebreak,
                                    with_default=with_default,
                                    with_description=with_description))

    def validate(self):
        components = self.get_components(remove_dummy=True)
        for name, component in components.items():
            if not hasattr(self, name):
                raise RuntimeError(f'config component "{name}" not initialized')
            value = getattr(self, name)
            if (value is NOTSET) and (component.required):
                raise ValueError(f'missing required config component: {name}')
            if isinstance(value, ConfigScheme):
                value.validate()
                continue
            component.validate(value)

    def get_components(self, remove_dummy:bool=False):
        components = getattr(self, _CONFIGCOMPONENTS, {})
        if remove_dummy:
            components = {name: component for name, component in components.items()
                          if component.pattern is None}
        return components

    def add_component(self, name:str, component:ConfigComponent, overwrite:bool=False):
        if not is_valid_variable_name(name):
            raise ValueError(f'invalid variable name (contains invalid characters / reserved keyword): {name}')
        if self.has_component(name) and (not overwrite):
            raise ValueError(f'config component "{name}" already exist')
        component = component.copy()
        if component.name is None:
            component.name = name
        getattr(self, _CONFIGCOMPONENTS)[name] = component
        self.reset_value(name)

    def has_component(self, name:str):
        return name in self.get_components()

    def get_component(self, name:str, strict:bool=True):
        if not self.has_component(name):
            if strict:
                raise RuntimeError(f'config component "{name}" does not exist')
            return None
        return self.get_components()[name]

    def set_value(self, name:str, value: Any) -> None:
        component = self.get_component(name)
        value = _make_copy(value)
        component.validate(value)
        setattr(self, name, value)

    def extend_value(self, name:str, value:Any) -> None:
        component = self.get_component(name)
        current_value = getattr(self, name)
        ext_value = _get_extended_object(current_value, value)
        component.validate(ext_value)
        setattr(self, name, ext_value)

    def get_value(self, name:str, default:Any=NOTSET) -> Any:
        if not self.has_component(name):
            if default is not NOTSET:
                return default
            raise ValueError(f'config component "{name}" does not exist')
        return getattr(self, name)

    def get(self, name:str, default:Any=NOTSET) -> Any:
        return self.get_value(name, default=default)

    def keys(self):
        components = self.get_components(remove_dummy=True)
        return components.keys()
        
    @classmethod
    def create(cls, source:Dict, strict:bool=False) -> "ConfigScheme":
        instance = cls()
        instance.load(source, strict=strict)
        return instnace

    def parse_dict(self, source:Dict, strict:bool=False) -> None:
        if not isinstance(source, dict):
            raise ValueError('input must be a dictionary')
        components = self.get_components()
        for key, value in source.items():
            if key.startswith('+'):
                method = self.extend_value
                key = key[1:]
            else:
                method = self.set_value
            if key not in components:
                matched_components = _match_components(key, components)
                if (not matched_components):
                    if strict:
                        raise ValueError(f'unexpected config component "{key}"')
                    continue
                elif len(matched_components) > 1:
                    patterns = [component.pattern for component in matched_components]
                    raise RuntimeError(f'the key {key} matched patterns of multiple config '
                                       f'components: {", ".join(patterns)}')
                # add the component as a new entry
                component = matched_components[0].copy()
                component.description = None
                component.pattern = None
                self.add_component(key, component)
            else:
                component = components[key]
            if _is_configscheme_class(component.dtype):
                subconfig = self.get_value(key)
                subconfig.parse_dict(value, strict=strict)
                continue
            method(key, value)

    def parse_file(self, filename:str, strict:bool=False):
        source = ConfigFile.read(filename)
        self.parse_dict(source, strict=strict)

    def load(self, source:Union[str, Dict], strict:bool=False):
        if isinstance(source, str):
            self.parse_file(source, strict=strict)
        elif isinstance(source, dict):
            self.parse_dict(source, strict=strict)
        else:
            raise ValueError(f'input with type {type(source)} is not allowed')
        self.validate()

    def merge(self, other:"ConfigScheme", overwrite:bool=True, extend:bool=False) -> None:
        if not isinstance(other, ConfigScheme):
            raise ValueError('only merge with another ConfigSchemeinstance is allowed')
        self_components = self.get_components()
        other_components = other.get_components()
        for name, other_component in other_components.items():
            if name not in self_components:
                if not extend:
                    continue
                self.add_component(name, other_component)
            else:
                this_component = self_components[name]
                if this_component != other_component:
                    raise ValueError(f'can not merge config component "{name}" with '
                                     f'different definitions')
            if _is_configscheme_class(other_component.dtype):
                this_value = self.get_value(name)
                other_value = other.get_value(name)
                this_value.merge(other_value,
                                 overwrite=overwrite)
                continue
            if overwrite:
                other_value = other.get_value(name)
                self.set_value(name, other_value)

    def as_dict(self) -> Dict:
        return as_dict(self)

class ConfigUnit:

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, value:type):
        if not _is_configscheme_class(value):
            raise ValueError(f'not a subclass of ConfigScheme: {value}')
        self._scheme = value
        
    def __init__(self, scheme: type,
                 required_components:Optional[List[str]]=None):
        self.scheme = scheme
        self.required_components = required_components

class ConfigurableObjectMeta(MergeAnnotationsMeta):
    def __new__(cls, name, bases, dct):
        annotations = dct.get('__annotations__', {})
        for key, annotation in annotations.items():
            if isinstance(annotation, ConfigUnit):
                if key in dct:
                    raise ValueError(f'config property "{key}" already set')
                def config_getter(self, key=key):
                    return getattr(self, _CONFIGOBJECTS)[key]
                def config_setter(self, value):
                    raise RuntimeError('can not set config object')
                config_prop = property(config_getter, config_setter)
                dct[key] = config_prop
        dct[_CONFIGOBJECTS] = {}
        return super().__new__(cls, name, bases, dct)

class ConfigurableObject(AbstractObject, metaclass=ConfigurableObjectMeta):
    
    def __init__(self, verbosity:str="INFO"):
        super().__init__(verbosity=verbosity)
        self._create_configs()

    def _create_configs(self):
        # create config objects based on the class annotations
        config_units = _get_config_unit_annotations(type(self))
        configs = {}
        for name, config_unit in config_units.items():
            config_scheme = config_unit.scheme
            required_components = config_unit.required_components
            config = config_scheme(name=name,
                                   required_components=required_components,
                                   verbosity=self.stdout.verbosity)
            configs[name] = config
        setattr(self, _CONFIGOBJECTS, configs)

    def _get_configs(self):
        return getattr(self, _CONFIGOBJECTS)

    def reset_config(self, names:Optional[Union[str , List[str]]]=None):
        configs = self._get_configs()
        if names is None:
            names = list(configs)
        if isinstance(names, str):
            names = [names]
        for name in names:
            if name not in configs:
                raise ValueError(f'undefined config object: {name}')
            configs[name].reset_values()

    @semistaticmethod
    def get_explain_text(self, names:Optional[Union[str , List[str]]]=None,
                         linebreak: int = 100,
                         with_default:bool=True,
                         with_description:bool=True) -> str:
        if inspect.isclass(self):
            configs = {}
            required_components = {}
            for name, annotation in _get_config_unit_annotations(self).items():
                configs[name] = annotation.scheme
                required_components[name] = annotation.required_components
        else:
            configs = self._get_configs()
            required_components = {}
        if not configs:
            return "Empty Configuration"
        if names is None:
            names = list(configs)
        elif isinstance(names, str):
            names = [names]
        explain_text = ""
        for name in names:
            if name not in configs:
                raise ValueError(f'config object not found: {name}')
            config = configs[name]
            components = required_components.get(name, None)
            explain_text += config.get_explain_text(components=components,
                                                    linebreak=linebreak,
                                                    with_default=with_default,
                                                    with_description=with_description)
        return explain_text
        
    @semistaticmethod
    def explain_config(self, names:Optional[Union[str, List[str]]]=None,
                       linebreak: int = 100,
                       with_default:bool=True,
                       with_description:bool=True):
        
        print(self.get_explain_text(names,
                                    linebreak=linebreak,
                                    with_default=with_default,
                                    with_description=with_description))

class ConfigFile:

    JSON_EXT = ('.json',)

    YAML_EXT = ('.yaml', '.yml')

    INCLUDE_SYNTAX = "+include"
    
    @staticmethod
    def read(filename:str):
        dirname = os.path.dirname(filename)
        _, file_extension = os.path.splitext(filename)
        try:
            with open(filename, 'r') as file:
                if file_extension.lower() in ConfigFile.JSON_EXT:
                    content = json.load(file)
                elif file_extension.lower() in ConfigFile.YAML_EXT:
                    content = yaml.safe_load(file)
                else:
                    raise ValueError(f'Unsupported file extension: {file_extension}')
                if isinstance(content, dict):
                    content = ConfigFile.parse_dict(content, dirname)
                return content
        except Exception as e:
            raise IOError(f'Error reading file {filename}: {e}')

    @staticmethod
    def parse_dict(source: Dict, dirname: Optional[str] = None):
        if not isinstance(source, dict):
            raise ValueError('source must be a dictionary')
        if dirname is None:
            dirname = os.getcwd()
        result = {}
        for key, value in source.items():
            if key.startswith(ConfigFile.INCLUDE_SYNTAX) and isinstance(value, str):
                includes = value if isinstance(value, list) else [value]
                for include_path in includes:
                    path = os.path.join(dirname, include_path)
                    included_content = ConfigFile.read(path)
                    if isinstance(included_content, dict):
                        result.update(included_content)
                    else:
                        return included_content
            elif isinstance(value, dict):
                result[key] = ConfigFile.parse_dict(value, os.path.join(dirname, os.path.dirname(key)))
            elif isinstance(value, list):
                result[key] = [ConfigFile.parse_dict(item, dirname) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result

# NestedConfigComponents