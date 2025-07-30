from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type, Dict, List

class WrapperMeta(ABCMeta):
    
    _wrappers: Dict[str, Type[Wrapper]] = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        if (not getattr(cls, '__abstractmethods__', False)
                and cls.name != '_base'):
            mcs.register(cls)
        return cls

    @classmethod
    def register(mcs, wrapper_cls: Type[Wrapper]) -> None:
        if wrapper_cls.name in mcs._wrappers:
            raise ValueError(
                f"Wrapper name '{wrapper_cls.name}' is already registered"
            )
        mcs._wrappers[wrapper_cls.name] = wrapper_cls
            
class Wrapper(metaclass=SerializerMeta):

    name = '_base'

    def __init__(self, data: Any, *args, **kwargs):
        self.obj = self.parse(data, *args, **kwargs)

    @classmethod
    @abstractmethod
    def parse(self, data: Any, *args, **kwargs):
        raise NotImplementedError
    