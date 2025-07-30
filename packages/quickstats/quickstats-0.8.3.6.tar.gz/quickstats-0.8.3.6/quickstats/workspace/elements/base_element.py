from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, model_validator

from quickstats import check_type, FlexibleDumper, Logger
from quickstats.interface.pydantic.alias_generators import to_pascal

__all__ = ['BaseElement']

_dumper : FlexibleDumper = FlexibleDumper(max_depth=3, max_iteration=3, max_line=100, max_len=100)
_stdout : Logger = Logger('INFO')

class Counter:
    
    def __init__(self):
        self.counts = {}
        
    def inc(self, name:str):
        if name not in self.counts:
            self.counts[name] = 0
        self.counts[name] += 1
        
_counter = Counter()

class BaseElement(BaseModel):
    
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True, validate_default=True,
                              alias_generator=to_pascal, arbitrary_types_allowed=True)

    _translated : bool = False
    _compiled : bool = False
    _parent : "BaseElement" = None

    def __repr__(self) -> str:
        return _dumper.dump(self.model_dump())

    def __setattr__(self, name: str, value: Any):
        self._inc_count('setattr')
        if hasattr(self, f'_validate_{name}'):
            validator_func = getattr(self, validator_name)
            value = validator_func(value=value)
        super().__setattr__(name, value)
        # use __dict__ to avoid infinite recursion
        if name != '_compiled':
            self.__dict__['_compiled'] = False
        else:
            self.__dict__['_compiled'] = value

    @property
    def parent(self) -> Optional["BaseElement"]:
        return self._parent

    @property
    def attached(self) -> bool:
        return self.parent is not None
        
    @property
    def translated(self) -> bool:
        return self._translated

    @property
    def compiled(self) -> bool:
        return self._compiled 

    @property
    def stdout(self) -> Logger:
        return _stdout

    def model_post_init(self, __context: Any) -> None:
        for field_name in self.model_fields:
            validator_name = f'_validate_{field_name}'
            if hasattr(self, validator_name):
                field_value = getattr(self, field_name)
                getattr(self, validator_name)(field_value)

    def set_verbosity(self) -> None:
        _stdout.verbosity = verbosity

    def configure_dumper(self, **kwargs) -> None:
        _dumper.configure(**kwargs)

    @model_validator(mode='after')
    def validate_base(self) -> None:
        self.update()
        return self

    def _inc_count(self, name:str):
        _counter.inc(name)

    def _get_count(self):
        return _counter.counts

    def _compile_field(self, field: 'BaseElement'):
        if field.parent is not (self):
            raise RuntimeError(f'The validated parent (id = {id(field.parent)}) of the following '
                               f'{type(field).__name__} element does not match the current '
                               f'parent {id(self)}. Please check if the element was added '
                               f'without proper validation.\n {field.__repr__}')
        field.compile()

    def translate(self, *args, **kwargs) -> None:
        self._translate = True    

    def compile(self, *args, **kwargs) -> 'Self':
        self._inc_count('compile')
        self._compiled = True
        return self

    def update(self, *args, **kwargs) -> None:
        self._inc_count('update')
        self._compiled = False