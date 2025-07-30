from typing import Union, Any
from abc import abstractmethod, ABC
from pathlib import Path

class Serializer(ABC):
    pass
    

class SerializerMixin(ABC):

    name : str = '_base'

    @abstractmethod
    def load(self, path: Union[str, Path], *args, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    def dump(self, path: str, *args, **kwargs) -> Any:
        raise NotImplementedError