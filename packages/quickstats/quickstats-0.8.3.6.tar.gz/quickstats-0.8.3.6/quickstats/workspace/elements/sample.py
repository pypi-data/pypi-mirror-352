from typing import List, Union, Optional

from pydantic import Field, computed_field, field_validator, ValidationInfo

from quickstats.core.typing import Scalar
from quickstats.utils.common_utils import remove_list_duplicates
from quickstats.workspace.settings import (
    SELF_SYST_DOMAIN_KEYWORD,
    YIELD_PREFIX,
    PDF_PREFIX,
    LUMI_NAME,
    NORM_PREFIX,
    XS_PREFIX,
    BR_PREFIX,
    EFFICIENCY_PREFIX,
    ACCEPTANCE_PREFIX,
    CORRECTION_PREFIX
)
from .base_element import BaseElement
from .sample_factor import NormFactor, ShapeFactor
from .model import (
    UserDefinedModel,
    HistogramModel,
    ExternalModel,
    CountingModel
)
from .systematic import Systematic

DESCRIPTIONS = {
    'name': 'Name of the sample / physics process.',
    'model': 'Pdf (or histogram) definition that models the sample shape. If the input is a string, it is recognized as a json/yaml file from which the model definition is imported. Optional in case of counting experiment.',
    'import_syst': 'Group(s) of common systematic uncertainties to be multiplied to the yield. Multiple systematic groups can be specified, with their names separated by commas. If not specified, no common yield uncertainties will be applied to current process automatically.',
    'shared_pdf': 'All the physics processes with the same "SharedPdf" name will share a common pdf. If not specified, current physics process will have a unique instead of shared pdf. Please note shape uncertainties on the pdf will be shared together with the pdf.',
    'systematics': 'List of systematic definitions.',
    'norm': 'Constant factor multiplied to the sample yield. Interpreted as the sample normalization.',
    'xsection': 'Constant factor multiplied to the sample yield. Interpreted as the sample cross-section.',
    'selection_eff': 'Constant factor multiplied to the sample yield. Interpreted as the sample selection efficiency.',
    'branching_ratio': 'Constant factor multiplied to the sample yield. Interpreted as the sample branching ratio.',
    'acceptance': 'Constant factor multiplied to the sample yield. Interpreted as the sample acceptance.',
    'correction': 'Constant factor multiplied to the sample yield. Interpreted as the sample correction term.',
    'multiply_lumi': 'Whether to multiply the luminosity to the sample yield. Its default value depends on whether the "Lumi" attribute is provided for current category. If provided, then "True" is default. Otherwise, "False" is default.',
    'norm_factors': 'List of normalization factors which are multiplied to the sampled yield. A normalization factor can define a new object in the workspace or reference an already defined object.',
    'shape_factors': 'List of shape factors. A shape factor is a variable or function that will not be automatically multiplied to the yield. Instead the user needs to define in the config where to put it.'
}

modeltypes = Union[CountingModel, UserDefinedModel, HistogramModel, ExternalModel]

class Sample(BaseElement):
    
    name: str = Field(alias='Name', description=DESCRIPTIONS['name'])
    model: modeltypes = Field(alias='Model', description=DESCRIPTIONS['model'], discriminator='type')
    import_syst: List[str] = Field(default_factory=lambda: [SELF_SYST_DOMAIN_KEYWORD], alias='ImportSyst',
                                   description=DESCRIPTIONS['import_syst'])
    multiply_lumi: Optional[bool] = Field(default=None, alias='MultiplyLumi', description=DESCRIPTIONS['multiply_lumi'])
    shared_pdf: Optional[str] = Field(default=None, alias='SharedPdf', description=DESCRIPTIONS['shared_pdf'])
    norm_factors: List[NormFactor] = Field(default_factory=list, alias='NormFactors', description=DESCRIPTIONS['norm_factors'])
    shape_factors: List[ShapeFactor] = Field(default_factory=list, alias='ShapeFactors', description=DESCRIPTIONS['shape_factors'])
    systematics : List[Systematic] = Field(default_factory=list, alias='Systematics', description=DESCRIPTIONS['systematics'])
    norm: Optional[Scalar] = Field(default=None, alias='Norm', description=DESCRIPTIONS['norm'])
    xsection: Optional[Scalar] = Field(default=None, alias='XSection', description=DESCRIPTIONS['xsection'])
    selection_eff: Optional[Scalar] = Field(default=None, alias='SelectionEff', description=DESCRIPTIONS['selection_eff'])
    branching_ratio: Optional[Scalar] = Field(default=None, alias='BR', description=DESCRIPTIONS['branching_ratio'])
    acceptance: Optional[Scalar] = Field(default=None, alias='Acceptance', description=DESCRIPTIONS['acceptance'])
    correction: Optional[Scalar] = Field(default=None, alias='Correction', description=DESCRIPTIONS['correction'])

    _attached : bool = False
    _has_category_lumi : bool = False

    @property
    def has_category_lumi(self) -> bool:
        return self._has_category_lumi
    
    @property
    def tag_name(self) -> str:
        return self.shared_pdf or self.name

    @property
    def model_name(self) -> str:
        return f"{PDF_PREFIX}{self.tag_name}"

    @property
    def norm_name(self) -> str:
        return f"{YIELD_PREFIX}{self.name}"

    @property
    def syst_domains(self) -> List[str]:
        domains = [domain for domain in self.import_syst]
        if SELF_SYST_DOMAIN_KEYWORD in domains:
            domains = []
        # all the systematics under the process should be included in any case  
        if self.name not in domains:
            domains.append(self.name)
        domains = remove_list_duplicates(domains)
        return domains

    @property
    def resolved_norm_factors(self):
        norm_factors = []
        if self.has_category_lumi and self.multiply_lumi:
            norm_factors.append(LUMI_NAME)
        if self.norm is not None:
            norm_factors.append(f"{NORM_PREFIX}_{self.name}[{self.norm}]")
        if self.xsection is not None:
            norm_factors.append(f"{XS_PREFIX}_{self.name}[{self.xsection}]")
        if self.branching_ratio is not None:
            norm_factors.append(f"{BR_PREFIX}_{self.name}[{self.branching_ratio}]")
        if self.selection_eff is not None:
            norm_factors.append(f"{EFFICIENCY_PREFIX}_{self.name}[{self.selection_eff}]")
        if self.acceptance is not None:
            norm_factors.append(f"{ACCEPTANCE_PREFIX}_{self.name}[{self.acceptance}]")
        if self.correction is not None:
            norm_factors.append(f"{CORRECTION_PREFIX}_{self.name}[{self.correction}]")            
        norm_factors.extend([factor.name for factor in self.norm_factors])
        return norm_factors

    @property
    def resolved_shape_factors(self):
        shape_factors = []    
        shape_factors.extend([factor.name for factor in self.shape_factors])
        return shape_factors

    @field_validator('norm_factors', 'shape_factors', mode='before')
    @classmethod
    def validate_sample_factors(cls, v, info: ValidationInfo) -> List:
        if isinstance(v, list):
            validated = []
            for v_i in v:
                if isinstance(v_i, str):
                    validated.append({'name': v_i, 'correlate': False})
                else:
                    validated.append(v_i)
            return validated
        return v

    def update(self):
        self._inc_count('sample_update')
        super().update()
        for systematic in self.systematics:
            systematic._raw_domain = self.name
            systematic._parent = self
        for factor in self.norm_factors:
            factor._parent = self
        for factor in self.shape_factors:
            factor._parent = self
        self.model._parent = self

    def compile(self) -> 'Self':
        if not self.attached:
            raise RuntimeError(f'Sample "{self.name}" is not attached to a category.')
        for systematic in self.systematics:
            self._compile_field(systematic)
        for factor in self.norm_factors:
            self._compile_field(factor)
        for factor in self.shape_factors:
            self._compile_field(factor)    
        self._compile_field(self.model)
        return super().compile()

    def get_category(self) -> "Category":
        if self.parent is None:
            raise RuntimeError('Sample is not attached to a category.')
        return self.parent

    def get_norm_factor_expr(self, norm_names: List[str]) -> str:
        return f'prod::{self.norm_name}({",".join(norm_names)})'