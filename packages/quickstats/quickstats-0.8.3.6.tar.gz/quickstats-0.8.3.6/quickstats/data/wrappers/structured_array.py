from .core import Wrapper

import numpy as np

class StructuredArray(Wrapper):

    name = 'structured_array'
    
    @classmethod
    def parse(self, data: Any) -> np.ndarray:
        ...


x = np.array([('Rex', 9, 81.0), ('Fido', 3, 27.0)],
             dtype=[('name', 'U10'), ('age', 'i4'), ('weight', 'f4')])