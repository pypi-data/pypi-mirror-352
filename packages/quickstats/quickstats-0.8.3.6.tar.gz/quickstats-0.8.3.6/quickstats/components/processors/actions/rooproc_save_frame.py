from typing import Optional

from .rooproc_helper_action import RooProcHelperAction
from .auxiliary import register_action

@register_action
class RooProcSaveFrame(RooProcHelperAction):
    
    NAME = "SAVE_FRAME"
    
    def __init__(self, name:str):
        super().__init__(name=name)

    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        return cls(name=main_text)
    
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        frame_name = params['name']
        if frame_name in processor.rdf_frames:
            processor.stdout.warning(f'Overriding existing rdf frame "{frame_name}"')
        processor.rdf_frames[frame_name] = processor.rdf
        return processor