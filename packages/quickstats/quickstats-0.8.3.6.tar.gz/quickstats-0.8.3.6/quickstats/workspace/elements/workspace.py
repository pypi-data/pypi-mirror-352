import os
from typing import List, Optional, Union

from pydantic import Field, ValidationInfo, field_validator, model_validator

from quickstats.core.typing import Scalar
from quickstats.utils.common_utils import remove_list_duplicates
from quickstats.utils.string_utils import format_aligned_dict
from quickstats.interface.pydantic.helpers import resolve_field_import
from quickstats.workspace.settings import (
    DataStorageType,
    GEN_ASIMOV_ACTION,
    LUMI_NAME,
    COMBINED_PDF_NAME,
    CATEGORY_STORE_NAME,
    RANGE_NAME_SB_LO,
    RANGE_NAME_SB_HI
)
from .base_element import BaseElement
from .category import Category
from .asimov_action import AsimovAction

DESCRIPTIONS = {
    'categories': 'List of analysis category (channel) definitions. If the entry is a string, it is recognized as a json/yaml file from which the category definition is imported.',
    'pois': 'List of parameters of interest in the analysis.',
    'workspace_name': 'Name of the workspace in the output root file.',
    'modelconfig_name': 'Name of the model config in the output root file.',
    'dataset_name': 'Name of the main dataset in the output root file.',
    'asimov_actions': 'List of asimov action definitions. Please check the AsimovAction element for more details.',
    'blind': 'Whether the analysis is blinded. The blind region is defined per-category in the category definition.',
    'generate_binned_data': 'Whether to create a binned dataset.',
    'generate_hist_data': 'Whether to generate a datahist.',
    'binned_fit': 'Whether to use the binned dataset for fitting in asimov actions.',
    'scale_lumi': 'Scale the global luminosity by this factor. A negative value disables the scaling.',
    'integrator': 'Integrator for RooAbsReal variables.',
    'data_storage_type': 'Storage type of dataset in the output root file. Please check the DataStorageType setting for more details.',
    'class_decl_import_dir': 'Directory to which the C++ class macros declarations are stored.',
    'class_impl_import_dir': 'Directory to which the C class macros implementations are stored.',
}

class Workspace(BaseElement):
    categories : List[Category] = Field(default_factory=list, alias='Categories',
                                        description=DESCRIPTIONS['categories'])
    pois : List[str] = Field(default_factory=list, alias='POIs',
                             description=DESCRIPTIONS['pois'])
    workspace_name : str = Field(default='combWS', alias='WorkspaceName',
                                 description=DESCRIPTIONS['workspace_name'])
    modelconfig_name : str = Field(default='ModelConfig', alias='ModelConfigName',
                                   description=DESCRIPTIONS['modelconfig_name'])
    dataset_name : str = Field(default='combData', alias='DatasetName',
                              description=DESCRIPTIONS['dataset_name'])
    asimov_actions : List[AsimovAction] = Field(default_factory=list, alias='AsimovActions',
                                                description=DESCRIPTIONS['asimov_actions'])
    blind : bool = Field(default=False, alias='Blind',
                         description=DESCRIPTIONS['blind'])
    generate_binned_data : bool = Field(default=True, alias='GenBinnedData',
                                        description=DESCRIPTIONS['generate_binned_data'])
    generate_hist_data : bool = Field(default=False, alias='GenHistData',
                                      description=DESCRIPTIONS['generate_hist_data'])
    binned_fit : bool = Field(default=False, alias='BinnedFit',
                              description=DESCRIPTIONS['binned_fit'])
    scale_lumi : Scalar = Field(default=-1., alias='ScaleLumi',
                                description=DESCRIPTIONS['scale_lumi'])
    integrator : Optional[str] = Field(default=None, alias='Integrator',
                                       description=DESCRIPTIONS['integrator'])
    data_storage_type : DataStorageType = Field(default=DataStorageType.Vector, alias='DataStorageType',
                                                description=DESCRIPTIONS['data_storage_type'])
    class_decl_import_dir : Optional[str] = Field(default=None, alias='ClassDeclImportDir',
                                                  description=DESCRIPTIONS['class_decl_import_dir'])
    class_impl_import_dir : Optional[str] = Field(default=None, alias='ClassImplImportDir',
                                                  description=DESCRIPTIONS['class_impl_import_dir'])

    @field_validator('categories', mode='before')
    @classmethod
    def validate_field_imports(cls, v: List[Union[Category, str]], info: ValidationInfo) -> List[Category]:
        return resolve_field_import(v, info)

    @property
    def translated(self) -> bool:
        return self._translated

    @property
    def asimov_names(self) -> List[str]:
        result = []
        for asimov_action in self.asimov_actions:
            if GEN_ASIMOV_ACTION in asimov_action.action:
                result.append(asimov_action.name)
        return result

    @property
    def category_names(self) -> List[str]:
        return [category.name for category in self.categories]

    @property
    def combined_pdf_name(self) -> str:
        return COMBINED_PDF_NAME

    @property
    def category_store_name(self) -> str:
        return CATEGORY_STORE_NAME

    @property
    def binned_dataset_name(self) -> str:
        return f"{self.dataset_name}binned"

    @property
    def datahist_name(self) -> str:
        return f"{self.dataset_name}hist"

    @property
    def fit_range_name(self) -> str:
        if self.blind:
            return f"{RANGE_NAME_SB_LO},{RANGE_NAME_SB_HI}"
        return None

    @property
    def get_lumi_expr(self, category_name: str) -> Optional[str]:
        category = self.get_category(category_name)
        category_lumi = category.lumi
        if category.lumi > 0:
            if self.scale_lumi > 0:
                return f"{LUMI_NAME}[{category.lumi * self.scale_lumi}]"
            else:
                return f"{LUMI_NAME}[{category.lumi}]"
        return None

    @property
    def initial_summary(self) -> str:
        text = ''
        text += '=' * 74 + '\n'
        items = {
            'Workspace name' : self.workspace_name,
            'ModelConfig name' : self.modelconfig_name,
            'Dataset name' : self.dataset_name,
            'Blind analysis': 'True' if self.blind else 'False',
            'Generate hist data': 'True' if self.generate_hist_data else 'False',
            'Scale lumi': str(self.scale_lumi),
            'POIs': ', '.join(self.pois),
            'Categories': ', '.join(self.category_names),
            'Asimov datasets': ', '.join(self.asimov_names)
        }
        text += format_aligned_dict(items, left_margin=2, linebreak=70)
        text += '=' * 74 + '\n'
        return text

    def get_category(self, name: str) -> Category:
        for category in self.categories:
            if category.name == name:
                return category
        raise ValueError(f'No category named "{name}".')

    def get_correlated_terms(self, category_name: str) -> List[str]:
        category = self.get_category(category_name)
        result = []
        result.extend(category.correlate)
        result.extend(self.pois)
        systematics = category.get_systematic_names()
        result.extend(systematics)
        result.append(category.observable_name)
        return remove_list_duplicates(result)

    def update(self) -> None:
        self._inc_count('workspace_update')
        super().update()
        category_names = []
        for category in self.categories:
            if category.name in category_names:
                raise RuntimeError(f'Duplicated category name: {category.name}')
            category_names.append(category.name)
            if category.lumi is None:
                category.lumi = 1 if self.scale_lumi > 0 else -1
            has_lumi = (category.lumi is not None) and (category.lumi > 0)
            for sample in category.samples:
                sample._has_category_lumi = has_lumi
            category._parent = self
        for asimov_action in self.asimov_actions:
            asimov_action._parent = self

    def translate(self, basedir: Optional[str] = None) -> "Workspace":
        if basedir is None:
            basedir = os.getcwd()
        basedir = os.path.abspath(basedir)
        update = {
            'categories': [category.translate(basedir=basedir) for category in self.categories]
        }
        workspace = self.model_copy(update=update, deep=True)
        workspace.update()
        workspace._translated = True
        return workspace

    def compile(self, apply_fix: bool = False) -> "Self":
        for category in self.categories:
            self._compile_field(category)
        for asimov_action in self.asimov_actions:
            self._compile_field(asimov_action)
        # fix sign definition of systematics
        if apply_fix:
            for category in categories:
                for systematic in category.systematics:
                    systematic.apply_fix = True
                for sample in category.samples:
                    for systematic in sample.systematics:
                        systematic.apply_fix = True
        return super().compile()