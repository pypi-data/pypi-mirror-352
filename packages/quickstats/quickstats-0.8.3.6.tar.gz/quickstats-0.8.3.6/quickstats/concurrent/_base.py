from typing import Optional, Dict, Iterable

# Cache status
NOCACHE = 'NOCACHE'
VALID_CACHE = 'VALIDCACHE'
BROKEN_CACHE = 'BROKENCACHE'

class CacheStatus(GeneralEnum):
    NOCACHE = -1
    SUCCESS = 0
    BROKEN = 1
    MISSING = 2
    ERROR = 3

class InputIterator:

    def __init__(self,
                 args: Optional[Iterable] = None,
                 kwargs: Optional[Iterable] = None,
                 common_kwargs: Optional[Dict] = None,
                 aux_kwargs: Optional[Dict] = None):
        if args is None and kwargs is None:
            raise ValueError(f'`args` and `kwargs` can not be both None')
        if args is None:
            args = repeat(tuple())
        if kwargs is None:
            kwargs = repeat(dict())
        if not isinstance(args, Iterable):
            raise ValueError(f'`args` must be iterable.')
        if not isinstance(kwargs, Iterable):
            raise ValueError(f'`kwargs` must be iterable.')
        self._args = args
        self._kwargs = kwargs
        if (common_kwargs is not None) and not isinstance(common_kwargs, dict):
            raise TypeError(f'`common_kwargs` must be a dictionary.')
        if (aux_kwargs is not None) and not isinstance(aux_kwargs, dict):
            raise TypeError(f'`aux_kwargs` must be a dictionary.')
        self._common_kwargs = common_kwargs or {}
        self._aux_kwargs = aux_kwargs or {}

    def iterate(self):
        for args, kwargs in zip(self._args, self._kwargs):
            if self._common_kwargs:
                kwargs = {**self._common_kwargs, **kwargs}
            yield args, kwargs