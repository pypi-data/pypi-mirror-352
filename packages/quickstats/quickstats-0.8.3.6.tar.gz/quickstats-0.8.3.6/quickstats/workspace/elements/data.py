from typing import Optional, Literal, Tuple, Any, Union

import numpy as np
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    field_serializer,
    ValidationInfo,
    SerializationInfo,
)

from quickstats.core.typing import Scalar
from quickstats.workspace.settings import (
    DATA_SOURCE_COUNTING,
    DATA_SOURCE_ASCII,
    DATA_SOURCE_HISTOGRAM,
    DATA_SOURCE_NTUPLE,
    DATA_SOURCE_ARRAY,
    OBS_DATASET_NAME,
)
from quickstats.workspace.translation import get_object_name_type
from .base_element import BaseElement

# (python 3.10+) could use annotated with Field(discriminator='...')

DESCRIPTIONS = {
    'type': 'Type of data source. Choice from "counting", "ascii", "histogram" or "root".',
    'observable': 'Observable definition (in workspace factory syntax).',
    'binning': 'Number of bins to be applied on the observable (uniform spacing defined as (range of observable)/(# of bins)). It defines the granularity of the Asimov and also the pseudo-binned dataset.',
    'inject_ghost': 'Whether to inject ghost data.',
    'scale_data': 'Scale the data by this factory.',
    'blind_range': 'Blind the data in the given range.',
    'counting': {
        'num_data': 'Number of data.'
    },   
    'ascii': {
        'filename': 'Path to the input text file.',
        'has_weight': 'Whether the data is weighted.',
    },
    'histogram': {
        'filename': 'Path to the input root file containing the histogram.',
        'histname': 'Name of the histogram in the file.'
    },
    'ntuple': {
        'filename': 'Path to the input root file containing the ntuple.',
        'treename': 'Name of the tree in the ntuple.',
        'varname': 'Name of the observable variable in the tree.',
        'weightname': 'Name of the weight variable in the tree.',
        'selection': 'Selection applied to the ntuple'
    },
    'array': {
        'x': 'Data values.',
        'y': 'Weight values.'
    }
}

class BaseData(BaseElement):

    type: Literal[
    DATA_SOURCE_COUNTING, DATA_SOURCE_ASCII,
    DATA_SOURCE_HISTOGRAM, DATA_SOURCE_NTUPLE,
    DATA_SOURCE_ARRAY
    ] = Field(alias='Type', description=DESCRIPTIONS['type'])
    observable: str = Field(alias='Observable', description=DESCRIPTIONS['observable'])
    inject_ghost: bool = Field(default=False, alias='InjectGhost', description=DESCRIPTIONS['inject_ghost'])
    scale_data: Scalar = Field(default=1., alias='ScaleData', description=DESCRIPTIONS['scale_data'])
    blind_range: Optional[Tuple[float, float]] = Field(default=None, alias='BlindRange', description=DESCRIPTIONS['blind_range'])

    @property
    def combined_scale_factor(self) -> float:
        workspace = self.get_workspace()
        if workspace.scale_lumi > 0:
            return workspace.scale_lumi * self.scale_data
        return self.scale_data

    @property
    def default_dataset_name(self) -> str:
        return OBS_DATASET_NAME

    @property
    def default_binned_dataset_name(self) -> str:
        return f"{self.default_dataset_name}binned"

    @property
    def default_hist_dataset_name(self) -> str:
        return f"{self.default_dataset_name}hist"    

    def get_category(self) -> "Category":
        if self.parent is None:
            raise RuntimeError('Data is not attached to a category.')
        return self.parent

    def get_workspace(self) -> "Workspace":
        category = self.get_category()
        return category.get_workspace()

class CountingData(BaseData):
    
    type: Literal[DATA_SOURCE_COUNTING] = Field(alias='Type', description=DESCRIPTIONS['type'])
    num_data: int = Field(alias='NumData', gt=0, description=DESCRIPTIONS['counting']['num_data'])

    def compile(self) -> "Self":
        if not self.attached:
            observable_name, _ = get_object_name_type(self.observable)
            raise RuntimeError(f'Counting data (observable = {observable_name}, '
                               f'num_data = {num_data}) not attached to a category.')
        return super().compile()
                        
class ASCIIData(BaseData):
    
    type: Literal[DATA_SOURCE_ASCII] = Field(alias='Type', description=DESCRIPTIONS['type'])
    binning: int = Field(alias='Binning', description=DESCRIPTIONS['binning'])
    filename: str = Field(alias='FileName', description=DESCRIPTIONS['ascii']['filename'])
    has_weight: bool = Field(default=False, alias='HasWeight', description=DESCRIPTIONS['ascii']['has_weight'])

    def compile(self) -> "Self":
        if not self.attached:
            observable_name, _ = get_object_name_type(self.observable)
            raise RuntimeError(f'ASCII data (observable = {observable_name}, '
                               f'filename = {self.filename}) not attached to a category.')
        return super().compile()

class HistogramData(BaseData):
    
    type: Literal[DATA_SOURCE_HISTOGRAM] = Field(alias='Type', description=DESCRIPTIONS['type'])
    binning: int = Field(alias='Binning', description=DESCRIPTIONS['binning'])
    filename: str = Field(alias='FileName', description=DESCRIPTIONS['histogram']['filename'])
    histname: str = Field(alias='HistName', description=DESCRIPTIONS['histogram']['histname'])

    def compile(self) -> "Self":
        if not self.attached:
            observable_name, _ = get_object_name_type(self.observable)
            raise RuntimeError(f'Histogram data (observable = {observable_name}, '
                               f'filename = {self.filename}, histname = {self.histname}) '
                               f'not attached to a category.')
        return super().compile()

class NTupleData(BaseData):
    
    type: Literal[DATA_SOURCE_NTUPLE] = Field(alias='Type', description=DESCRIPTIONS['type'])
    binning: int = Field(alias='Binning', description=DESCRIPTIONS['binning'])
    filename: str = Field(alias='FileName', description=DESCRIPTIONS['ntuple']['filename'])
    treename: Optional[str] = Field(default=None, alias='TreeName', description=DESCRIPTIONS['ntuple']['treename'])
    varname: str = Field(alias='VarName', description=DESCRIPTIONS['ntuple']['varname'])
    weightname: Optional[str] = Field(default=None, alias='WeightName', description=DESCRIPTIONS['ntuple']['weightname'])
    selection: Optional[str] = Field(default=None, alias='Selection', description=DESCRIPTIONS['ntuple']['selection'])

    def compile(self) -> "Self":
        if not self.attached:
            observable_name, _ = get_object_name_type(self.observable)
            raise RuntimeError(f'NTuple data (observable = {observable_name}, '
                               f'filename = {self.filename}, treename = {self.treename}, '
                               f'varname = {self.varname}) not attached to a category.')
        return super().compile()

class ArrayData(BaseData):
    
    type: Literal[DATA_SOURCE_ARRAY] = Field(alias='Type', description=DESCRIPTIONS['type'])
    binning: int = Field(alias='Binning', description=DESCRIPTIONS['binning'])    
    x: np.ndarray = Field(alias='X', description=DESCRIPTIONS['array']['x'])
    y: Optional[np.ndarray] = Field(
        default=None, 
        alias='Y', 
        description=DESCRIPTIONS['array']['y']
    )

    @field_validator('x', 'y', mode='before')
    @classmethod
    def validate_data(cls, v: Any, info: ValidationInfo) -> Optional[np.ndarray]:
        if v is None:
            if info.field_name == 'x':
                raise ValueError("x cannot be None")            
            return None
        return np.asarray(v)

    @field_serializer('x', 'y')
    def serialize_array(
        self, 
        v: Optional[np.ndarray], 
        _info: SerializationInfo
    ) -> Optional[list]:
        if v is None:
            return None
        return v.tolist()
        
    def compile(self) -> "Self":
        if not self.attached:
            observable_name, _ = get_object_name_type(self.observable)
            raise RuntimeError(f'Array data (observable = {observable_name}) '
                               f'not attached to a category.')
        return super().compile()

DataType = Union[CountingData, ASCIIData, HistogramData, NTupleData, ArrayData]