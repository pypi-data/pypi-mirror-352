from typing import Any, List, Optional, Union

from pydantic import Field, BaseModel, ConfigDict, model_validator

from quickstats import Logger, check_type, FlexibleDumper, get_type_hint_str
from quickstats.utils.string_utils import format_aligned_dict
from .alias_generators import to_pascal

__all__ = ['DefaultModel']

_dumper : FlexibleDumper = FlexibleDumper(max_depth=2, max_iteration=3, max_line=100, max_len=100)
_stdout : Logger = Logger('INFO')

class DefaultModel(BaseModel):
    """Default configurable class"""

    verbosity : Union[int, str] = Field(default='INFO', description='The verbosity level.')
    
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True,
                              validate_default=True, alias_generator=to_pascal,
                              arbitrary_types_allowed=True)

    _stdout : Logger = Logger('INFO')
    _parent : "DefaultModel" = None

    def __repr__(self) -> str:
        return _dumper.dump(self.model_dump())

    def __setattr__(self, name: str, value: Any):
        if hasattr(self, f'_validate_{name}'):
            validator_func = getattr(self, validator_name)
            value = validator_func(value=value)
        super().__setattr__(name, value)

    @property
    def parent(self) -> Optional["DefaultModel"]:
        return self._parent

    @property
    def attached(self) -> bool:
        return self.parent is not None

    @property
    def stdout(self) -> Logger:
        return self._stdout

    def model_post_init(self, __context: Any) -> None:
        for field_name in self.model_fields:
            validator_name = f'_validate_{field_name}'
            if hasattr(self, validator_name):
                field_value = getattr(self, field_name)
                getattr(self, validator_name)(field_value)

    def _validate_verbosity(self, value: Union[int, str]) -> Union[int, str]:
        self._stdout = Logger(self.verbosity)
        return value

    def configure_dumper(self, **kwargs) -> None:
        _dumper.configure(**kwargs)

    @classmethod
    def generate_help_text(cls, linebreak: int = 100) -> str:
        """
        Generate help text for the class, displaying the class name and field info.
        """
        # Start with the class name
        help_text = f"{cls.__name__}\n\n"

        # Add information about each field
        for field_name, field_info in cls.__fields__.items():
            field_type = get_type_hint_str(field_info.annotation)
            field_default = field_info.default if field_info.default is not None else "None"
            field_description = field_info.description if field_info.description else "No description provided."
    
            attributes = {
                'Type': field_type,
                'Default': field_default,
                'Description': field_description
            }
            attributes_text = format_aligned_dict(attributes, left_margin=4, linebreak=linebreak)
            help_text += f'  {field_name}:\n'
            help_text += f'{attributes_text}\n'

        return help_text

    @classmethod
    def help(cls, linebreak: int = 100):
        """
        Prints out the help message for the class.
        """
        print(cls.generate_help_text(linebreak=linebreak))