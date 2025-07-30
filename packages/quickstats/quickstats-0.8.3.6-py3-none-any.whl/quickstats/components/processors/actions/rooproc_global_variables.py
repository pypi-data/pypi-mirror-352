from typing import Optional, List, Dict
import re

from .rooproc_helper_action import RooProcHelperAction
from .auxiliary import register_action

@register_action
class RooProcGlobalVariables(RooProcHelperAction):
    
    NAME = "GLOBAL"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def commarepl(matchobj):
        return matchobj.group(0).replace(",", "::COMMA::")
    
    @classmethod
    def _parse(cls, main_text:str, block_text:Optional[str]=None):
        main_text = re.sub(r"\s*", "", main_text)
        main_text = re.sub(r'\[(.*?)\]', cls.commarepl, main_text)
        tokens = [token.replace("::COMMA::", ",") for token in main_text.split(",")]
        global_variables = {}
        for token in tokens:
            result = re.match(r"^(\w+)=(.*)", token)
            if not result:
                raise RuntimeError(f"invalid expression {token}")
            global_variables[result[1]] = result[2]
        return global_variables
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        global_variables = cls._parse(main_text, block_text)
        return cls(**global_variables)
    
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        processor.global_variables.update(params)
        return processor