from typing import Optional, Union, List, Dict, Callable

import numpy as np

from quickstats import cached_import
from quickstats.core.typing import ArrayLike

ArrayBlindConditionType = Union[ArrayLike, Callable]
DataBlindConditionType = Union[ArrayBlindConditionType, Dict[str, ArrayBlindConditionType]]

class ArrayBlinder:

    def __init__(self, condition: ArrayBlindConditionType):
        self._condition = self.parse_condition(condition)

    @property
    def condition(self):
        return self._condition
        
    @staticmethod
    def parse_condition(condition: ArrayBlindConditionType):
        if not callable(condition):
            try:
                range_min, range_max = condition
            except Exception:
                raise ValueError(f'Invalid blind condition: {condition}. When condition is not '
                                 f'a callable, it must be an array of the form (range_min, range_max).')
            condition = lambda x: (x >= range_min) & (x <= range_max)
        return condition

    def get_mask(self, array: np.ndarray) -> np.ndarray:
        mask = self.condition(array)
        if mask.dtype != bool:
            raise RuntimeError('Mask condition gives array of non-boolean type.')
        return mask
        
    def get_blinded_array(self, array: np.ndarray) -> np.ndarray:
        mask = self.get_mask(array)
        return array[mask]

class DataBlinder:

    def __init__(self, condition: DataBlindConditionType,
                 axis: int = 0):
        self._condition = self.parse_condition(condition)
        self._axis = axis
        if isinstance(self.condition, dict) and self.axis != 0:
            raise ValueError('Axis must be 0 when condition is a mapping.')
        if self.axis not in [0, 1]:
            raise ValueError('Axis must be either 0 or 1.')
        
    @property
    def condition(self):
        return self._condition

    @property
    def axis(self):
        return self._axis
        
    @staticmethod
    def parse_condition(condition: DataBlindConditionType):
        if isinstance(condition, dict):
            return {key : ArrayBlinder.parse_condition(value) for key, value in condition.items()}
        return ArrayBlinder.parse_condition(condition)

    def get_mask(self, data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        mask = {}
        if self.axis == 0:
            if not isinstance(self.condition, dict):
                condition = {key: self.condition for key in data}
            else:
                condition = {key: self.condition[key] if key in self.condition \
                             else lambda x: np.full(x.shape, True) for key in data}
            for key, array in data.items():
                mask[key] = condition[key](array)
        elif self.axis == 1:
            pd = cached_import('pandas')
            df = pd.DataFrame(data)
            mask_all = df.apply(self.condition, axis=1).values
            mask = {key: mask_all for key in data}
        else:
            raise ValueError('Axis must be either 0 or 1.')
        for key in mask:
            if mask[key].dtype != bool:
                raise RuntimeError(f'Mask condition for the key "{key}" gives array of non-boolean type.')
        return mask
        
    def get_blinded_data(self, data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        mask = self.get_mask(data)
        blinded_data = {}
        for key, array in data.items():
            blinded_data[key] = array[mask[key]]
        return blinded_data