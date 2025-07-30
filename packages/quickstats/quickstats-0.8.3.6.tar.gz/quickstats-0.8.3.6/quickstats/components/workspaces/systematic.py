from typing import Optional, Union, List, Dict

import numpy as np

from quickstats import DescriptiveEnum, AbstractObject, Logger
from quickstats.maths.numerics import is_float

from .settings import (NORM_SYST_KEYWORD, SHAPE_SYST_KEYWORD, COMMON_SYST_DOMAIN_NAME,
                       CONSTR_GAUSSIAN, CONSTR_LOGN, CONSTR_ASYM, CONSTR_DFD, OTHER,
                       UNCERT_HI_PREFIX, UNCERT_LO_PREFIX, UNCERT_SYM_PREFIX)

class SystematicType(DescriptiveEnum):
    Norm  = (0, "Normalization systematic", NORM_SYST_KEYWORD)
    Shape = (1, "Shape systematic", SHAPE_SYST_KEYWORD)
    Other = (2, "Unclassified systematic type", OTHER)
    
    def __new__(cls, value:int, description:str, keyword:str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.keyword = keyword
        return obj

class ErrorType(DescriptiveEnum):
    Upper = (0, "Upper Error", UNCERT_HI_PREFIX)
    Lower = (1, "Lower Error", UNCERT_LO_PREFIX)
    
    def __new__(cls, value:int, description:str, prefix:str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.prefix = prefix
        return obj
        
class ConstraintType(DescriptiveEnum):
    LogN  = (0, "Lognormal constraint", CONSTR_LOGN, 1, 1)
    Asym  = (1, "Asymmetric constraint", CONSTR_ASYM, 4, 5)
    Gaus  = (2, "Gaussian constraint", CONSTR_GAUSSIAN, 0, 0)
    DFD   = (3, "Double Fermi-Dirac constraint", CONSTR_DFD, 0, 0)
    Other = (4, "Unclassified constraint type", OTHER, -1, -1)
    
    def __new__(cls, value:int, description:str, keyword:str,
                resp_func_interp_code:int, piecewise_interp_code: int):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.keyword = keyword
        obj.resp_func_interp_code = resp_func_interp_code
        obj.piecewise_interp_code = piecewise_interp_code
        return obj

class Systematic(AbstractObject):
    
    def __init__(
        self,
        apply_fix: bool = False,
        use_piecewise_interp: bool = True,
        logger: Optional[Logger] = None
    ):
        super().__init__(logger=logger)
        self.name = ""
        self.domain = ""
        self.raw_domain = ""
        self.process = ""
        self.whereto = ""
        self.constr_term = ""
        self.nominal = 0.
        self.beta = 0.
        self.errorlo = None
        self.errorhi = None
        self.apply_fix = apply_fix
        self.use_piecewise_interp = use_piecewise_interp
    
    def __eq__(self, other:"Systematic"):
        return (self.name == other.name) and (self.process == other.process) and (self.whereto == other.whereto)
    
    @staticmethod
    def default_domain():
        return COMMON_SYST_DOMAIN_NAME
    
    @staticmethod
    def common_domain():
        return COMMON_SYST_DOMAIN_NAME

    @property
    def syst_type(self) -> SystematicType:
        return self.get_syst_type()

    @property
    def constr_type(self) -> ConstraintType:
        return self.get_constr_type()

    @property
    def tag_name(self) -> str:
        return self.get_tag_name()
    
    def is_equal(self, other:"Systematic"):
        return self.__eq__(other)
    
    def is_shape_syst(self):
        return self.get_syst_type() == SystematicType.Shape

    def get_syst_type(self):
        result = SystematicType.get_member_by_attribute("keyword", self.whereto)
        if result is None:
            return SystematicType.Other
        return result
    
    def get_constr_type(self):
        result = ConstraintType.get_member_by_attribute("keyword", self.constr_term)
        if result is None:
            raise ValueError(f'unknown constraint type: {self.constr_term}')
        return result
    
    def is_common_domain(self):
        return self.domain == COMMON_SYST_DOMAIN_NAME
    
    def set_domain(self, domain:str):
        syst_type = self.get_syst_type()
        # systematics defined in the common domain
        if domain == self.common_domain():
            # if a process name is specified, use it as domain name and 
            # remove it from common systematic
            if self.process != "":
                if syst_type == SystematicType.Shape:
                    self.domain = f"{self.whereto}_{self.process}"
                else:
                    self.domain = self.process
            # otherwise consider it as common systematic
            else:
                # for shape uncertainty, use NP name as domain
                if syst_type == SystematicType.Shape:
                    self.domain = f"{self.whereto}_{self.name}"
                # for yield uncertainty, consider it as common systematic
                elif syst_type == SystematicType.Norm:
                    self.domain = domain
                else:
                    raise RuntimeError(f'Unknown systematic loacation {self.whereto} '
                                       f'for NP {self.name}. Choose from "{NORM_SYST_KEYWORD}" (NormSyst) '
                                       f'or "{SHAPE_SYST_KEYWORD}" (ShapeSyst)')
        else:
            # for yield systematics under a sample, the domain name is always the sample name
            # for shape systematics under a sample, we will update it later depending on whether "Process" is specified
            self.domain = domain
            # for yield systematics under a sample, the default process name is the sample name
            # if a process name is provided in addition (e.g. uncertainties on acceptance and correction factor are separately provided in differential xs measurements), it will be <sample_name>_<process_name>
            if self.process == "":
                self.process = domain
                if syst_type == SystematicType.Shape:
                    self.domain = f"{self.whereto}_{self.name}_{self.process}"
            else:
                self.process = f"{domain}_{self.process}"
                if syst_type == SystematicType.Shape:
                    self.domain = f"{self.whereto}_{self.process}"
        self.raw_domain = domain
        
    def set_magnitudes(self, values:Union[float, str, List[float], List[str]]):
        # for asymmetric uncertainty, we need to be careful with the relative sign between the two components
        # if both upper and lower uncertainties are numbers, the lower number will always be forced to have opposite sign of upper
        # if either uncertainty is implemented as formula, the neither component can bear sign. Users need to make sure the sign convention is consistent
        if not isinstance(values, list):
            values = [values]
        if len(values) == 1:
            value = values[0]
            if isinstance(value, str):
                if is_float(value):
                    self.errorhi = float(value)
                    self.errorlo = float(value)
                else:
                    self.errorhi = value
                    self.errorlo = value
            elif isinstance(value, float):
                self.errorhi = value
                self.errorlo = value
            else:
                raise ValueError(f"invalid systematic magnitude: {value}")
        elif len(values) == 2:
            errhi, errlo = values
            # both are numbers, need to handle the relative sign
            if is_float(errhi) and is_float(errlo):
                errlo, errhi = float(errlo), float(errhi)
                if (errlo != 0) and (errhi == 0):
                    errhi = 1e-8 * (-np.sign(errlo))
                elif (errhi != 0) and (errlo == 0):
                    errlo = 1e-8 * (-np.sign(errhi))
                if self.apply_fix and (errlo >= 0) and (errhi <= 0):
                    self.errorhi = -errlo
                    self.errorlo = abs(errhi)
                elif float(errhi) == 0:
                    self.errorhi = errhi
                    self.errorlo = errlo
                elif float(errhi) < 0:
                    self.errorhi = errhi
                    self.errorlo = abs(errlo)
                else:
                    self.errorhi = errhi
                    self.errorlo = -abs(errlo)                   
            else:
                self.errorhi = errhi
                self.errorlo = errlo
            if self.get_constr_type() != ConstraintType.Asym:
                self.stdout.warning(f"The systematic {self.name} under domain {self.domain} "
                                    f"will be implemented as an asymmetric uncertainty for now. Please "
                                    f"double-check your config file and use the keyword "
                                    f"{CONSTR_ASYM} for constraint "
                                    f"term type instead of {self.constr_term} if you intend to implement "
                                    f"asymmetric uncertainties.")
                self.constr_term = CONSTR_ASYM
        # default to positive sign if error is an expression (str)
        self.beta = 1
        if is_float(self.errorhi):
            # default to positive sign if error is zero
            self.beta = np.sign(float(self.errorhi)) or 1
    
    def get_tag_name(self) -> str:
        tag_name = f"{self.whereto}_{self.name}"
        if not self.is_common_domain():
            tag_name += f"_{self.process}"
        return tag_name
            
    def get_interp_code(self) -> int:
        if self.use_piecewise_interp:
            return self.constr_type.piecewise_interp_code
        return self.constr_type.resp_func_interp_code

    def get_uncert_expr(self, err_type: ErrorType) -> str:
        err_type = ErrorType.parse(err_type)
        err_val = self.errorhi if err_type == ErrorType.Upper else self.errorlo
        uncert_prefix = f"{err_type.prefix}{self.tag_name}"
        if self.use_piecewise_interp:
            interp_code = self.constr_type.piecewise_interp_code
            if interp_code not in [0, 1, 5]:
                raise RuntimeError(f'Constraint type {self.constr_type} not supported')
            linear_interp = interp_code == 0
            # for exponential interpolation, lower error will be raise to the power -theta
            exp = -1. if (err_type == ErrorType.Lower) and not linear_interp else 1.
            sign = -1. if (err_type == ErrorType.Lower) and linear_interp else 1.
            offset = 1. if (self.nominal != 0.) else 0.
            if self.nominal == 0. and not linear_interp:
                raise RuntimeError(f'Central value cannot be zero for non-Gaussian constraints')
            scale = 1. if linear_interp else self.nominal
            if is_float(err_val):
                uncert_value = (offset + sign * abs(float(err_val)) / scale) ** exp
                return f"{uncert_prefix}[{uncert_value}]"
            scale_expr = "" if scale == 1. else f"/{scale}"
            sign_expr = "+" if sign > 0 else "-"
            uncert_value_expr = f"{offset}{sign_expr}abs(@0){scale_expr}"
            if exp < 0:
                uncert_value_expr = f"1./({uncert_value_expr})"
            return f"expr::{uncert_prefix}('{uncert_value_expr}', {err_val})"
        # use response function instead
        if is_float(err_val):
            return f"{uncert_prefix}[{err_val}]"
        return err_val

    def validate(self) -> None:
        if (self.nominal < 0.):
            raise RuntimeError(
                f"Failed to parse systematic {self.name}: "
                f"negative central value (= {self.nominal}) is not allowed "
            )
        if (self.nominal == 0.):
            constr_type = self.constr_type
            if constr_type in [ConstraintType.LogN, ConstraintType.Asym]:
                raise RuntimeError(
                    f"Failed to parse systematic {self.name}: "
                    f"{constr_type.description} does not allow zero central value"
                )
        elif (self.nominal != 1.0):
            self.stdout.warning(
                f'Received non-unit or non-zero central value (={self.nominal}) '
                f'for the systematic {self.name}. Will force it to unity during implementation.'
            )
        

        