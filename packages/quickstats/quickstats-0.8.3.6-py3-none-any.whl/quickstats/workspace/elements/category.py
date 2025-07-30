import os
from typing import List, Union, Any, Optional, Dict
from collections import defaultdict

from pydantic import Field, ValidationInfo, model_validator, field_validator

from quickstats.core.typing import Scalar
from quickstats.utils.common_utils import remove_list_duplicates
from quickstats.interface.pydantic.helpers import resolve_field_import, resolve_model_import
from quickstats.workspace.settings import (
    AnalysisType,
    COMMON_SYST_DOMAIN_NAME,
    COMMON_SYST_DOMAIN_KEYWORD,
    RESPONSE_KEYWORD,
    RESPONSE_PREFIX,
    COUNTING_MODEL,
    DATA_SOURCE_COUNTING,
    LUMI_NAME,
    SUM_PDF_NAME,
    FINAL_PDF_NAME,
    SystematicType,
    ConstraintType
)
from quickstats.workspace.translation import (
    get_object_name_type,
    translate_special_keywords,
    item_has_dependent
)
from .base_element import BaseElement
from .data import DataType
from .systematic import Systematic
from .systematic_domain import SystematicDomain
from .sample import Sample

DESCRIPTIONS = {
    'name': 'Name of category (channel).',
    'type': 'Type of category: "shape" or "counting"',
    'data': 'Dataset definition.',
    'lumi': 'Luminosity.',
    'samples': 'List of sample definitions. If the entry is a string, it is recognized as a json/yaml file from which the sample definition is imported.',
    'systematics': 'List of systematics definitions. If the entry is a string, it is recognized as a json/yaml file from which the systematic definition is imported.',
    'correlate': 'List of correlated terms.',
    'items': 'List of workspace object definitions ((in workspace factory syntax).',
    'import_items': 'List of json/yaml file names from which additional category definitions are defined / appended. This usually applies to "systematics".'
}

class Category(BaseElement):
    name : str = Field(alias='Name', description=DESCRIPTIONS['name'])
    type : AnalysisType = Field(default=AnalysisType.Shape, alias='Type',
                                description=DESCRIPTIONS['type'])
    data : DataType = Field(alias='Data', description=DESCRIPTIONS['data'], discriminator='type')
    lumi : Optional[Scalar] = Field(default=None, alias='Lumi', description=DESCRIPTIONS['lumi'])
    samples : List[Sample] = Field(default_factory=list, alias='Samples',
                                   description=DESCRIPTIONS['samples'])
    systematics : List[Systematic] = Field(default_factory=list, alias='Systematics',
                                           description=DESCRIPTIONS['systematics'])
    correlate : List[str] = Field(default_factory=list, alias='Correlate',
                                  description=DESCRIPTIONS['correlate'])
    items : List[str] = Field(default_factory=list, alias='Items',
                              description=DESCRIPTIONS['items'])
    import_items : List[str] = Field(default_factory=list, alias='ImportItems',
                                     description=DESCRIPTIONS['import_items'])

    @model_validator(mode='before')
    @classmethod
    def validate_category_imports(cls, data: Any) -> Any:
        return resolve_model_import(data, ['import_items', 'ImportItems'])

    @field_validator('samples', 'systematics', mode='before')
    @classmethod
    def validate_field_imports(cls, v: List, info: ValidationInfo) -> List:
        return resolve_field_import(v, info)

    def _check_systematic_duplicates(self) -> None:
        systematic_domains = self.systematic_domains
        duplicates = {}
        found = False
        for systematic_domain in systematic_domains:
            domain, systematics = systematic_domain.name, systematic_domain.systematics
            duplicates[domain] = defaultdict(list)
            for syst in systematics:
                duplicates[domain][syst].append(syst)
            duplicates[domain] = [(systs[0], len(systs)) for systs in duplicates[domain].values() if len(systs) > 1]
            if not duplicates[domain]:
                duplicates.pop(domain)
        if duplicates:
            #Found duplicated systematics:\n
            msg = ''
            for domain in duplicates:
                msg += f'[Domain = {domain}]\n'
                for syst, num in duplicates[domain]:
                    msg += (f'Name: {syst.name}, WhereTo: {syst.whereto}, '
                            f'Process: {syst.process} ({num} duplicates)\n')
                msg += '\n'
            raise RuntimeError(f'Found duplicated systematics:\n{msg}')

    @property
    def is_counting(self) -> bool:
        return self.type == AnalysisType.Counting

    @property
    def observable_name(self) -> str:
        return get_object_name_type(self.data.observable)[0]

    @property
    def sum_pdf_name_raw(self) -> str:
        return f"{SUM_PDF_NAME}"    

    @property
    def sum_pdf_name(self) -> str:
        return f"{self.sum_pdf_name_raw}_{self.name}"
        
    @property
    def final_pdf_name(self) -> str:
        return f"{FINAL_PDF_NAME}_{self.name}"

    @property
    def resolved_correlate_terms(self) -> List[str]:
        result = []
        result.extend(self.correlate)
        for sample in self.samples:
            for factor in sample.norm_factors:
                if factor.correlate:
                    result.append(get_object_name_type(factor.name)[0])
            for factor in sample.shape_factors:
                if factor.correlate:
                    result.append(get_object_name_type(factor.name)[0])
        return result
        
    @property
    def item_priority_map(self) -> Dict[str, List[str]]:
        result = {
            'high_priority': [],
            'low_priority': []
        }
        buffer_items = []
        for item in self.items:
            if (RESPONSE_KEYWORD in item) or (RESPONSE_PREFIX in item):
                result['low_priority'].append(item)
            else:
                buffer_items.append(item)
        for item in buffer_items:
            if item_has_dependent(item, result['low_priority']):
                result['low_priority'].append(item)
            else:
                result['high_priority'].append(item)
        return result

    @property
    def systematic_domains(self) -> List[SystematicDomain]:
        buffer = {}
        def add_systematic(syst: "Systematic"):
            if syst.domain not in buffer:
                buffer[syst.domain] = []
            buffer[syst.domain].append(syst)
        systematics = self.get_systematics()
        for systematic in systematics:
            add_systematic(systematic)
        result = []
        for domain, systematics in buffer.items():
            systematic_domain = SystematicDomain(name=domain,
                                                 systematics=systematics)
            result.append(systematic_domain)
        return result

    @property
    def response_function_map(self) -> List[str]:
        result = {}
        systematic_domains = self.systematic_domains
        for systematic_domain in systematic_domains:
            if not systematic_domain.is_shape:
                domain = systematic_domain.name
                result[domain] = systematic_domain.response_name
        return result

    @property
    def sum_pdf_expr(self) -> str:
        components = [f"{sample.norm_name}*{sample.model_name}" for sample in self.samples]
        return f'SUM::{self.sum_pdf_name_raw}({",".join(components)})'
        
    @property
    def lumi_expr(self) -> str:
        workspace = self.get_workspace()
        if self.lumi > 0:
            if workspace.scale_lumi > 0:
                return f"{LUMI_NAME}[{self.lumi * workspace.scale_lumi}]"
            else:
                return f"{LUMI_NAME}[{self.lumi}]"
        return None
    
    def update(self) -> None:
        self._inc_count('category_update')
        super().update()
        sample_names = []
        has_lumi = (self.lumi is not None) and (self.lumi > 0)
        for sample in self.samples:
            sample._has_category_lumi = has_lumi
            if sample.name in sample_names:
                raise RuntimeError(f'Duplicated sample name: {sample.name}')
            sample_names.append(sample.name)
            sample._parent = self
        for systematic in self.systematics:
            systematic._raw_domain = COMMON_SYST_DOMAIN_NAME
            systematic._parent = self
        self.data._parent = self
        self._check_systematic_duplicates()
        if self.is_counting:
            for sample in self.samples:
                if sample.model.type != COUNTING_MODEL:
                    raise RuntimeError(f'Category "{self.name}" is marked is counting analysis but '
                                       f'the sample "{sample.name}" has model type "{sample.model.type}".')
            if self.data.type != DATA_SOURCE_COUNTING:
                raise RuntimeError(f'Category "{self.name}" is marked is counting analysis but '
                                   f'the data source has type "{self.data.type}".')

    def _translate_data(self, basedir: str) -> None:
        if 'filename' in self.data.model_fields:
            self.data.filename = os.path.join(basedir, self.data.filename)
        self.data._translated = True

    def _translate_model(self, basedir: str) -> None:
        for sample in self.samples:
            if 'filename' in sample.model.model_fields:
                sample.model.filename = os.path.join(basedir, sample.model.filename)
            sample.model._translated = True

    def translate(self, basedir: Optional[str] = None) -> "Category":
        if basedir is None:
            basedir = os.getcwd()
        basedir = os.path.abspath(basedir)
        category = self.model_copy(deep=True)
        resolvers = {
            'category': category.name,
            'observable': get_object_name_type(category.data.observable)[0],
        }
        translated_samples = []
        for sample in category.samples:
            process = translate_special_keywords(sample.name, **resolvers)
            sample_json = sample.model_dump_json()
            translated_sample_json = translate_special_keywords(sample_json, **resolvers, process=process)
            translated_sample = Sample.parse_raw(translated_sample_json)
            translated_samples.append(translated_sample)
        category_json = category.model_dump_json()
        translated_category_json = translate_special_keywords(category_json, **resolvers)
        translated_category = Category.model_validate_json(translated_category_json)
        translated_category._translate_data(basedir=basedir)
        translated_category._translate_model(basedir=basedir)
        translated_category._translated = True
        return translated_category

    def compile(self) -> 'Self':
        if not self.attached:
            raise RuntimeError(f'Category "{self.name}" is not attached to a workspace.')
        if not self.translated:
            raise RuntimeError(f'Category "{self.name}" is not translated.')
        for sample in self.samples:
            self._compile_field(sample)
        for systematic in self.systematics:
            self._compile_field(systematic)
        self._compile_field(self.data)
        return super().compile()

    def get_workspace(self) -> "Workspace":
        if self.parent is None:
            raise RuntimeError('Category is not attached to a workspace.')
        return self.parent

    def get_sample(self, name: str) -> Sample:
        for sample in self.samples:
            if sample.name == name:
                return sample
        raise ValueError(f'No sample named "{name}".')

    def get_systematics(self, sample_names:Optional[List[str]] = None,
                        syst_types: Optional[List[str]] = None,
                        constr_types: Optional[List[str]] = None) -> List[Systematic]:
        if syst_types is not None:
            syst_types = [SystematicType.parse(syst_type) for syst_type in syst_types]
        if constr_types is not None:
            constr_types = [ConstraintType.parse(constr_type) for constr_type in constr_types]
        result = []
        if sample_names is None:
            for systematic in self.systematics:
                result.append(systematic)
            for sample in self.samples:
                for systematic in sample.systematics:
                    result.append(systematic)
        else:
            if COMMON_SYST_DOMAIN_KEYWORD in sample_names:
                for systematic in self.systematics:
                    if systematic.is_common_systematic():
                        result.append(systematic)
                sample_names = [name for name in sample_names if name != COMMON_SYST_DOMAIN_KEYWORD]
            for systematic in self.systematics:
                if systematic.process in sample_names:
                    result.append(systematic)
            for sample_name in sample_names:
                sample = self.get_sample(sample_name)
                for systematic in sample.systematics:
                    result.append(systematic)
        if syst_types is not None:
            result = [syst for syst in result if syst.syst_type in syst_types]
        if constr_types is not None:
            result = [syst for syst in result if syst.constr_type in constr_types]
        return result

    def get_systematic_names(self, sample_names:Optional[List[str]] = None,
                             syst_types: Optional[List[str]] = None,
                             constr_types: Optional[List[str]] = None) -> List[str]:
        systematics = self.get_systematics(sample_names=sample_names,
                                           syst_types=syst_types,
                                           constr_types=constr_types)
        return remove_list_duplicates([syst.name for syst in systematics])

    def get_common_systematics(self) -> List[Systematic]:
        result = []
        for systematic in self.systematics:
            if systematic.is_common_systematic():
                result.append(systematic)
        return result

    def get_final_pdf_expr(self, constr_set: "ROOT.RooArgSet") -> str:
        # category pdf is the produt of sample sum pdf and the constraint pdfs
        pdf_components = [self.sum_pdf_name] + [constr.GetName() for constr in constr_set]
        pdf_str = ",".join(pdf_components)
        return f"PROD::{self.final_pdf_name}({pdf_str})"
        