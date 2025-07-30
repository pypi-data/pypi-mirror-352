from typing import List, Optional, Union, Literal

from pydantic import Field

from quickstats.core.typing import Scalar
from quickstats.workspace.settings import (
    COUNTING_MODEL,
    USERDEF_MODEL,
    HISTOGRAM_MODEL,
    EXTERNAL_MODEL,
    EXT_MODEL_ACTION_ITEM,
    EXT_MODEL_ACTION_FIX,
    EXT_MODEL_ACTION_RENAME,
    EXT_MODEL_ACTION_EXTSYST
)
from quickstats.workspace.translation import (
    get_object_name_type
)
from .base_element import BaseElement

MODEL_DESCRIPTIONS = {
    'type': 'Type of the model. It can be one of "userdef" (user-defined), "external" (imported from external workspaec) or "histogram".',
    'userdefined': {
        'items': 'List of object definitions (in workspace factory syntax) defining the building blocks of the model.',
        'modelitem': 'Expression (in workspace factory syntax) that defines the final pdf of the model. The name of pdf specified in here will be ignored, as the program has internal rules to name the pdf with the physics process and channel names.',
        'cache_binning': 'Not used.'
    },
    'histogram': {
        'filename': 'Name of the root file containing the model histogram.',
        'histname': 'Name of the histogram in the root file.',
        'rebin': 'Rebin the histogram to this binning.'
    },
    'external': {
        'filename': 'Path to the workspace file containing the external model.',
        'workspace': 'Name of the workspace.',
        'model': 'Name of the pdf to be imported.',
        'observable': 'Name of observable for the pdf, which will be renamed to the observable name provided in the category-level config.',
        'actions': 'List of actions to be applied to the external model before importing.'
    }
}

EXT_ACTION_DESCRIPTIONS = {
    'type': 'Type of external pdf action. It can be one of "item", "fix", "rename", "ext_syst".',
    'item': {
        'name': 'A workspace object definition (in workspace factory syntax).',
    },
    'fix': {
        'name': 'Name of the variable to fix.',
        'value': 'If specified, fix the variable to this value.'
    },
    'rename': {
        'old_name': 'Original name of the variable',
        'new_name': 'New name of the variable'
    },
    'ext_syst': {
        'nuis_name': 'Name of the nuisance parameter.',
        'glob_name': 'Name of the global observable.',
        'constr_name': 'Name of the constraint pdf.'
    }
}

class BaseModel(BaseElement):

    @property
    def model_name(self) -> str:
        sample = self.get_sample()
        return sample.model_name

    @property
    def observable_name(self) -> str:
        category = self.get_category()
        return category.observable_name

    def get_sample(self) -> "Sample":
        if self.parent is None:
            raise RuntimeError('Model is not attached to a sample.')
        return self.parent

    def get_category(self) -> "Category":
        sample = self.get_sample()
        return sample.get_category()

class CountingModel(BaseModel):
    type : Literal[COUNTING_MODEL] = Field(alias='Type', description=MODEL_DESCRIPTIONS['type'])

    @property
    def pdf_expr(self) -> str:
        return f"RooUniform::{self.model_name}({self.observable_name})"
    
    def compile(self) -> "Self":
        if not self.attached:
            raise RuntimeError('Counting model not attached to a sample.')
        return super().compile()

class UserDefinedModel(BaseModel):
    type : Literal[USERDEF_MODEL] = Field(alias='Type', description=MODEL_DESCRIPTIONS['type'])
    modelitem : str = Field(alias='ModelItem', description=MODEL_DESCRIPTIONS['userdefined']['modelitem'])
    items : List[str] = Field(alias='Items', default_factory=list, description=MODEL_DESCRIPTIONS['userdefined']['items'])
    cache_binning : int = Field(alias='CacheBinning', default=-1, deprecated=True,
                                description=MODEL_DESCRIPTIONS['userdefined']['cache_binning'])

    @property
    def pdf_expr(self) -> str:
        name_start = self.modelitem.find("::") + 2
        name_end = self.modelitem.find("(")
        return self.modelitem[:name_start] + self.model_name + self.modelitem[name_end:]
        
    def compile(self) -> "Self":
        if not self.attached:
            model_name, _ = get_object_name_type(self.modelitem)
            raise RuntimeError(f'User-defined model "{model_name}" not attached to a sample.')
        return super().compile()

class HistogramModel(BaseModel):
    type : Literal[HISTOGRAM_MODEL] = Field(alias='Type', description=MODEL_DESCRIPTIONS['type'])
    filename : str = Field(alias='FileName', description=MODEL_DESCRIPTIONS['histogram']['filename'])
    histname : str = Field(alias='HistName', description=MODEL_DESCRIPTIONS['histogram']['histname'])
    rebin : int = Field(default=-1, alias='Rebin', description=MODEL_DESCRIPTIONS['histogram']['rebin'])

    def compile(self) -> "Self":
        if not self.attached:
            raise RuntimeError(f'Histogram model (filename = "{self.filename}", '
                               f'histname = "{self.histname}") not attached to a sample.')
        return super().compile()

class ItemExtModelAction(BaseElement):
    type : Literal[EXT_MODEL_ACTION_ITEM] = Field(alias='Type', description=EXT_ACTION_DESCRIPTIONS['type'])
    name : str = Field(alias='Name', description=EXT_ACTION_DESCRIPTIONS['item']['name'])
    
class FixExtModelAction(BaseElement):
    type : Literal[EXT_MODEL_ACTION_FIX] = Field(alias='Type', description=EXT_ACTION_DESCRIPTIONS['type'])
    name : str = Field(alias='Name', description=EXT_ACTION_DESCRIPTIONS['fix']['name'])
    value : Optional[Scalar] = Field(default=None, alias='Value', description=EXT_ACTION_DESCRIPTIONS['fix']['value'])

class RenameExtModelAction(BaseElement):
    type : Literal[EXT_MODEL_ACTION_RENAME] = Field(alias='Type', description=EXT_ACTION_DESCRIPTIONS['type'])
    old_name : str = Field(alias='OldName', description=EXT_ACTION_DESCRIPTIONS['rename']['old_name'])
    new_name : str = Field(alias='NewName', description=EXT_ACTION_DESCRIPTIONS['rename']['new_name'])

class ExtSystExtModelAction(BaseElement):
    type : Literal[EXT_MODEL_ACTION_EXTSYST] = Field(alias='Type', description=EXT_ACTION_DESCRIPTIONS['type'])
    nuis_name : str = Field(alias='NuisName', description=EXT_ACTION_DESCRIPTIONS['ext_syst']['nuis_name'])
    glob_name : Optional[str] = Field(default=None, alias='GlobName', description=EXT_ACTION_DESCRIPTIONS['ext_syst']['glob_name'])
    constr_name : Optional[str] = Field(default=None, alias='ConstrName', description=EXT_ACTION_DESCRIPTIONS['ext_syst']['constr_name'])
    
class ExternalModel(BaseModel):
    type : Literal[EXTERNAL_MODEL] = Field(alias='Type', description=MODEL_DESCRIPTIONS['type'])
    filename : str = Field(alias='FileName', description=MODEL_DESCRIPTIONS['external']['filename'])
    workspace_name : Optional[str] = Field(default=None, alias='WSName', deprecated=True, description=MODEL_DESCRIPTIONS['external']['workspace'])
    ext_model_name : str = Field(alias='ModelName', description=MODEL_DESCRIPTIONS['external']['model'])
    ext_observable_name : str = Field(alias='ObservableName', description=MODEL_DESCRIPTIONS['external']['observable'])    
    actions : List[Union[ItemExtModelAction, FixExtModelAction, RenameExtModelAction,
    ExtSystExtModelAction]] = Field(default_factory=list, alias='Actions', description=MODEL_DESCRIPTIONS['external']['actions'])

    def compile(self) -> "Self":
        if not self.attached:
            raise RuntimeError(f'External model (filename = "{self.filename}", '
                               f'modelname = "{self.model}") not attached to a sample.')
        return super().compile()