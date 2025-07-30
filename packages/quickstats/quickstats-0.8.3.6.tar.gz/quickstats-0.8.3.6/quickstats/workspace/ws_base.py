from typing import Dict, Any, Optional, List, Union
import os

import quickstats
from quickstats import AbstractObject, cached_import
from quickstats.utils.root_utils import load_macro, get_macro_TClass
from quickstats.utils.common_utils import set_unlimited_stacksize

from .translation import get_object_name_type

class WSBase(AbstractObject):

    def __init__(self, unlimited_stack:bool=True,
                 verbosity: Optional[Union[int, str]] = "INFO"):
        super().__init__(verbosity=verbosity)
        self.custom_classes = {}
        if unlimited_stack:
            set_unlimited_stacksize()
            self.stdout.info("Set stack size to unlimited.") 

    @staticmethod
    def suppress_roofit_message() -> None:
        ROOT = cached_import('ROOT')
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.NumIntegration)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.Fitting)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.Minimization)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.InputArguments)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.Eval)
        ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)

    def load_extension(self):
        ROOT = cached_import('ROOT')
        extensions = quickstats.get_workspace_extensions()
        for extension in extensions:
            result = load_macro(extension)
            if (result is not None) and hasattr(ROOT, extension):
                self.stdout.info(f'Loaded extension module "{extension}"')
            try:
                cls = get_macro_TClass(extension)
            except Exception:
                continue
            self.custom_classes[extension] = cls

    def import_object(self, ws: "ROOT.RooWorkspace", obj, *args, silent: bool = True) -> None:
        if silent:
            ROOT = cached_import('ROOT')
            getattr(ws, "import")(obj, *args, ROOT.RooFit.Silence())
        else:
            getattr(ws, "import")(obj, *args)
    
    def import_expression(self, ws: "ROOT.RooWorkspace", object_expr: str,
                          check_defined: bool = False) -> str:
        object_name, object_type = get_object_name_type(object_expr)
        # throw error when attemping to access undefined object
        if object_type == "defined":
            if not ws.arg(object_name):
                raise RuntimeError(f'Object "{object_name}" does not exist.')
            return object_name
        # throw error? when attemping to define already existing object
        if check_defined and ws.arg(object_name):
            self.stdout.debug(f'Object "{object_name}" already exists.')
            return object_name
        self.stdout.debug(f'Generating {object_type} {object_expr}.')
        status = ws.factory(object_expr)
        if not status:
            raise RuntimeError(f'Object creation from expression "{object_expr}" had failed.')
        return object_name

    def import_expressions(self, ws: "ROOT.RooWorkspace",
                           object_expr_list:List[str],
                           check_defined: bool = False) -> List[str]:
        object_names = []
        for object_expr in object_expr_list:
            object_name = self.import_expression(ws, object_expr, check_defined=check_defined)
            object_names.append(object_name)
        return object_names