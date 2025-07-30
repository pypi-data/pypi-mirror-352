from typing import Dict, Union, List, Optional, Tuple
import os

import numpy as np

from quickstats import semistaticmethod, AbstractObject, cached_import

class RooWorkspace(AbstractObject):
    
    @semistaticmethod
    def create_argset_from_var_names(self, ws:"ROOT.RooWorkspace", var_names:[str, List[str]],
                                     strict:bool=False) -> "ROOT.RooArgSet":
        if isinstance(var_names, str):
            var_names = [var_names]
        ROOT = cached_import('ROOT')
        result = ROOT.RooArgSet()
        for var_name in var_names:
            var = ws.var(var_name)
            if not var:
                if strict:
                    raise RuntimeError(f'The variable "{var_name}" is not defined in the workspace "{ws.GetName()}".')
                continue
            result.add(var)
        return result