from typing import Optional, Dict, Union
import copy

from quickstats import NamedTreeNode, NestedDict

class Registry(NamedTreeNode[NestedDict]):

    def _validate_data(self, data: Optional[Dict] = None) -> NestedDict:
        if data is None:
            return NestedDict()
        return NestedDict(copy.deepcopy(data))

    @property
    def data(self) -> NestedDict:
        if super().data is None:
            return NestedDict()
        return copy.deepcopy(super().data)
        
    def use(self, name: str) -> None:   
        data = self.get(name, strict=True)
        self._data = data

    def parse(self, source: Optional[Union[str, Dict]] = None) -> NestedDict:
        if source is None:
            return {}
        if isinstance(source, str):
            try:
                return self.get(source, strict=True)
            except KeyError:
                raise KeyError(f'template does not exist: {source}')
        return NestedDict(copy.deepcopy(source))

    def chain(self, *sources) -> NestedDict:
        result = self.data
        for source in sources:
            result &= self.parse(source)
        return result