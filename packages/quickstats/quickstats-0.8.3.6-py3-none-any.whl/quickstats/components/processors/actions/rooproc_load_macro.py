from typing import Optional

from .rooproc_helper_action import RooProcHelperAction
from .auxiliary import register_action

@register_action
class RooProcLoadMacro(RooProcHelperAction):
    
    NAME = "LOAD_MACRO"
    
    def __init__(self, name:str):
        super().__init__(name=name)

    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        return cls(name=main_text)
    
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        macro_name = params['name']
        from quickstats.interface.cppyy.macros import SUPPLEMENTARY_CPP_MACROS
        if macro_name not in SUPPLEMENTARY_CPP_MACROS:
            raise RuntimeError(f'undefined macro (from cppyy.macros.SUPPLEMENTARY_CPP_MACROS): {macro_name}')
        from quickstats.interface.cppyy.core import cpp_define
        definition = SUPPLEMENTARY_CPP_MACROS[macro_name]
        result = cpp_define(definition, macro_name)
        if not result:
            raise RuntimeError(f'failed to load macro "{macro_name}" '
                               f'(forget to load shared library or missing include paths?)')
        processor.stdout.info(f'Loaded macro "{macro_name}"')
        return processor