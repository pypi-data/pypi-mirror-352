from abc import abstractmethod, ABC
from typing import Any

class Converter(ABC):
    pass
    

class ConverterMixin(ABC):

    name : str = '_base'

    @abstractmethod
    def convert(self, name: str, *args, **kwargs) -> Any:
        raise NotImplementedError