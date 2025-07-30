from typing import Optional, Union

from quickstats import AbstractObject

class TObject(AbstractObject):

    def __init__(self,
                 verbosity:Optional[Union[int, str]]="INFO",
                 **kwargs):
        super().__init__(verbosity=verbosity)
        self.obj = None
        self.initialize(**kwargs)
        
    def initialize(self, **kwargs):
        pass

    def get(self):
        return self.obj