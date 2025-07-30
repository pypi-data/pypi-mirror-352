from typing import Optional, Union, Tuple, Literal

import numpy as np
from pydantic import Field, field_validator

from quickstats import DescriptiveEnum
from quickstats.maths.numerics import is_float
from quickstats.core.typing import Scalar
from quickstats.workspace.translation import (
    get_glob_name,
    get_constr_name
)
from quickstats.workspace.settings import (
    GLOBALOBS_PREFIX,
    CONSTRTERM_PREFIX,
    UNCERT_LO_PREFIX,
    UNCERT_HI_PREFIX,
    CONSTR_GAUSSIAN,
    CONSTR_LOGN,
    CONSTR_ASYM,
    CONSTR_DFD,
    NORM_SYST_KEYWORD,
    SHAPE_SYST_KEYWORD,
    COMMON_SYST_DOMAIN_NAME,
    NORM_SYST_KEYWORD,
    SHAPE_SYST_KEYWORD,
    OTHER,
    SystematicType,
    ConstraintType
)
from .base_element import BaseElement

DESCRIPTIONS = {
    'name': 'Nuisance parameter name.',
    'constr': 'Constraint pdf type. Choose among "gaus" (Gaussian), "logn" (lognormal), "asym" (asymmetric), and "dfd" (double-fermi-dirac).',
    'central_value': 'Nominal value of the response function (usually 1).',
    'magnitude': 'Magnitude of the uncertainty.',
    'whereto': 'Choose between "yield" and "shape". Keyword "yield" means that the response function will be automatically multiplied to the yield of the designated physics process. Keyword "shape", on the other hand, means that the user needs to specify later where to put the response function.',
    'process': 'A label used to classify the systematic uncertainty. When specified for a common uncertainty, it can be used to direct a systematic uncertainty (like luminosity) to several relevant physics processes to simplify the implementation. When specified for a process-specific uncertainty, it can allow constructing multiple uncertainties under the same NP name for different effects (e.g. acceptance and correction factors uncertainties from the same source). By default, process is set to the domain where the systematic is defined, i.e. common domain if it is defined under a category, or the specific sample domain if it is defined under a sample.',
    'beta': 'A scale factor to be multiplied to the uncertainty magnitude.',
    'apply_fix': 'Fix wrong sign convension of magnitudes.'
}

ConstrTypes = Literal[CONSTR_GAUSSIAN, CONSTR_LOGN, CONSTR_ASYM, CONSTR_DFD]
WhereToTypes = Literal[NORM_SYST_KEYWORD, SHAPE_SYST_KEYWORD]
MagnitudeTypes = Union[float, str, Tuple[float, float], Tuple[str, str]]

class Systematic(BaseElement):
    
    name : str = Field(alias='Name', description=DESCRIPTIONS['name'])
    constr : ConstrTypes = Field(alias='Constr', description=DESCRIPTIONS['constr'])
    magnitude : MagnitudeTypes = Field(alias='Magnitude', description=DESCRIPTIONS['magnitude'])
    whereto : WhereToTypes = Field(alias='WhereTo', description=DESCRIPTIONS['whereto'])
    central_value : Scalar = Field(default=1., alias='ContralValue', description=DESCRIPTIONS['central_value'])
    process : Optional[str]  = Field(default=None, alias='Process', description=DESCRIPTIONS['process'])
    beta: Scalar = Field(default=1, alias='Beta', deprecated=True, description=DESCRIPTIONS['beta'])
    apply_fix : bool = Field(default=False, alias='ApplyFix', description=DESCRIPTIONS['apply_fix'])

    _epsilon : float = 1e-8
    _raw_domain : str = COMMON_SYST_DOMAIN_NAME

    _errorlo : Optional[Union[str, Scalar]] = None
    _errorhi : Optional[Union[str, Scalar]] = None

    def __eq__(self, other:"Systematic"):
        return (self.name == other.name) and (self.process == other.process) and (self.whereto == other.whereto)

    def __hash__(self):
        return hash(f'{self.name}_{self.process}_{self.whereto}')
    
    @property
    def errorlo(self) -> Optional[Union[str, Scalar]]:
        return self._errorlo

    @property
    def errorhi(self) -> Optional[Union[str, Scalar]]:
        return self._errorhi
        
    @property
    def syst_type(self) -> SystematicType:
        syst_type = SystematicType.get_member_by_attribute("keyword", self.whereto)
        return syst_type or SystematicType.Other

    @property
    def constr_type(self) -> ConstraintType:
        constr_type = ConstraintType.get_member_by_attribute("keyword", self.constr)
        if not constr_type:
            raise ValueError(f'Unknown constraint: {self.constr}')
        return constr_type

    @property
    def is_shape(self) -> bool:
        return self.whereto == SHAPE_SYST_KEYWORD

    @property
    def full_process(self) -> str:
        if not self.attached:
            raise RuntimeError(f'Systematic "{self.name}" is not attached to a sample or a category.')
        if self._raw_domain == COMMON_SYST_DOMAIN_NAME:
            return self.process
        elif not self.process:
            return self._raw_domain
        else:
            return f'{self._raw_domain}_{self.prcoess}'

    @property
    def domain(self) -> str:
        if not self.attached:
            raise RuntimeError(f'Systematic "{self.name}" is not attached to a sample or a category.')
        syst_type = self.syst_type
        # systematics defined in the common domain
        if self._raw_domain == COMMON_SYST_DOMAIN_NAME:
            # if a process name is specified, use it as domain name and 
            # remove it from common systematic
            if self.process:
                if syst_type == SystematicType.Shape:
                    return f"{self.whereto}_{self.process}"
                else:
                    return self.process
            # otherwise consider it as common systematic
            else:
                # for shape uncertainty, use NP name as domain
                if syst_type == SystematicType.Shape:
                    return f"{self.whereto}_{self.name}"
                # for yield uncertainty, consider it as common systematic
                elif syst_type == SystematicType.Norm:
                    return self._raw_domain
                else:
                    raise RuntimeError(f'Unknown systematic loacation {self.whereto} '
                                       f'for NP {self.name}. Choose from "{NORM_SYST_KEYWORD}" (NormSyst) '
                                       f'or "{SHAPE_SYST_KEYWORD}" (ShapeSyst)')
        else:
            # for yield systematics under a sample, the domain name is always the sample name
            # for shape systematics under a sample, we will update it later depending on whether "Process" is specified
            # for yield systematics under a sample, the default process name is the sample name
            # if a process name is provided in addition (e.g. uncertainties on acceptance and correction factor are 
            # separately provided in differential xs measurements), it will be <sample_name>_<process_name>
            if syst_type == SystematicType.Shape:
                if not self.process:
                    return f"{self.whereto}_{self.name}_{self._raw_domain}"
                else:
                    return f"{self.whereto}_{self._raw_domain}_{self.process}"
            else:
                return self._raw_domain

    @property
    def tag_name(self) -> str:
        if self.domain != COMMON_SYST_DOMAIN_NAME:
            return f"{self.whereto}_{self.name}_{self.full_process}"
        return f"{self.whereto}_{self.name}"

    @property
    def glob_name(self) -> str:
        return get_glob_name(self.name)

    @property
    def constr_name(self) -> str:
        return get_constr_name(self.name)

    @property
    def interp_code(self) -> int:
        return self.constr_type.interp_code

    @property
    def nuis_expr(self) -> str:
        return f"{self.name}[0, -5, 5]"
        
    @property
    def uncert_hi_expr(self) -> str:
        if is_float(self.errorhi):
            return f"{UNCERT_HI_PREFIX}{self.tag_name}[{self.errorhi}]"
        return self.errorhi
    
    @property
    def uncert_lo_expr(self) -> str:
        if is_float(self.errorlo):
            return f"{UNCERT_LO_PREFIX}{self.tag_name}[{self.errorlo}]"
        return self.errorlo

    @property
    def constr_expr(self) -> str:
        constr_type = self.constr_type
        constr_name = self.constr_name
        glob_name = self.glob_name
        nuis_name = self.name
        if constr_type == ConstraintType.DFD:
            constr_expr = (f"EXPR::{constr_name}('1/((1+exp(@2*(@0-@3-@1)))*(1+exp(-1*@2*(@0-@3+@1))))', "
                           f"{nuis_name}, DFD_e[1], DFD_w[500], {glob_name}[0,-5,5])")
        else:
            constr_expr = f"RooGaussian::{constr_name}({nuis_name},{glob_name}[0,-5,5],1)"
        return constr_expr

    def _validate_magnitude(self, _value: MagnitudeTypes) -> MagnitudeTypes:
        self._inc_count('_validate_magnitude')
        magnitude = _value
        if not isinstance(magnitude, (list, tuple)):
            magnitude = [magnitude]
        if len(magnitude) == 1:
            value = magnitude[0]
            if isinstance(value, str):
                if is_float(value):
                    self._errorhi = float(value)
                    self._errorlo = float(value)
                else:
                    self._errorhi = value
                    self._errorlo = value
            elif isinstance(value, float):
                self._errorhi = value
                self._errorlo = value
            else:
                raise ValueError(f"Invalid systematic magnitude: {value}")
        elif len(magnitude) == 2:
            if self.constr != CONSTR_ASYM:
                domain_str = f'under domain {self.domain} ' if self._attached else ''
                self.stdout.warning(f'The systematic {self.name} {domain_str} will be implemented '
                                    f'as an asymmetric uncertainty for now. Please '
                                    f'double-check your config file and use the keyword '
                                    f'{CONSTR_ASYM} for constraint term type instead of '
                                    f'{self.constr} if you intend to implement '
                                    f'asymmetric uncertainties.')
            errorhi, errorlo = magnitude
            # both are numbers, need to handle the relative sign
            if is_float(errorhi) and is_float(errorlo):
                errorlo, errorhi = float(errorlo), float(errorhi)
                if (errorlo != 0) and (errorhi == 0):
                    errorhi = self._epsilon * (-np.sign(errorlo))
                elif (errorhi != 0) and (errorlo == 0):
                    errorlo = self._epsilon * (-np.sign(errorhi))
                if self.apply_fix and (errorlo >= 0) and (errorhi <= 0):
                    self._errorhi = - errorlo
                    self._errorlo = abs(errorhi)
                elif float(errorhi) == 0:
                    self._errorhi = errorhi
                    self._errorlo = errorlo
                elif float(errorhi) < 0:
                    self._errorhi = errorhi
                    self._errorlo = abs(errorlo)
                else:
                    self._errorhi = errorhi
                    self._errorlo = -abs(errorlo)                   
            else:
                self._errorhi = errorhi
                self._errorlo = errorlo
        return _value

    def _validate_central_value(self, value:Scalar) -> Scalar:
        self._inc_count('_validate_central_value')
        if (value <= 0.) and (self.constr in [CONSTR_LOGN, CONSTR_ASYM]):
            raise RuntimeError(f"Systematic {self.name} has constraint term {self.constr} "
                               f"but received negative central value (={self.central_value}).")
        return value

    def is_common_systematic(self) -> bool:
        return self.domain == COMMON_SYST_DOMAIN_NAME

    def compile(self) -> 'Self':
        if not self.attached:
            raise RuntimeError(f'Systematic "{self.name}" is not attached to a sample or a category.')
        return super().compile()