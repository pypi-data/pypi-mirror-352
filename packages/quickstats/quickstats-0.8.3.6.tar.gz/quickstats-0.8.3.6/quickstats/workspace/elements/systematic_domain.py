from typing import Optional, Union, List, Dict

from pydantic import Field

from quickstats import cached_import
from quickstats.workspace.settings import (
    RESPONSE_PREFIX,
    GLOBALOBS_PREFIX,
    CONSTRTERM_PREFIX,
    SHAPE_SYST_KEYWORD
)

from .base_element import BaseElement
from .systematic import Systematic

class SystematicDomain(BaseElement):

    name : str = Field(alias='Name')
    systematics : List[Systematic] = Field(default_factory=list, alias='Systematics')

    @property
    def response_name(self):
        return f"{RESPONSE_PREFIX}{self.name}"

    @property
    def is_shape(self):
        result = None
        for systematic in self.systematics:
            syst_is_shape = systematic.is_shape
            if result is None:
                result = syst_is_shape
            elif syst_is_shape != result:
                raise RuntimeError(f'Found mixture of shape and non-shape systematics '
                                   f'in the domain "{self.name}"')
        return result

    def update(self):
        super().update()
        assert self.is_shape is not None