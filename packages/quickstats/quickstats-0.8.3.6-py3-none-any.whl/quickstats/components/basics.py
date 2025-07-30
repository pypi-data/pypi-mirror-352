from typing import Optional
from quickstats import GeneralEnum, DescriptiveEnum

class WSVariables(GeneralEnum):
    VARIABLES                         = 0
    OBSERVABLES                       = 1
    POIS                              = 2
    GLOBAL_OBSERVABLES                = 3
    NUISANCE_PARAMETERS               = 4
    CONSTRAINED_NUISANCE_PARAMETERS   = 5
    UNCONSTRAINED_NUISANCE_PARAMETERS = 6
    CONSTRAINTS                       = 7
    AUXILIARY                         = 8
    CORE                              = 9
    NON_CONSTRAINT_VARIABLES          = 10
    GAUSSIAN_CONSTRAINT_NP            = 11
    POISSON_CONSTRAINT_NP             = 12
    
class ConstraintType(GeneralEnum):
    GAUSSIAN = (0, "RooGaussian")
    POISSON  = (1, "RooPoisson")
    
    def __new__(cls, value:int, classname:str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.classname = classname
        return obj
    
class WSArgument(DescriptiveEnum):
    WORKSPACE                         = (0, "Workspace", False)
    DATASET                           = (1, "Datasets", False)
    SNAPSHOT                          = (2, "Snapshots", False)
    PDF                               = (3, "PDFs", False)
    FUNCTION                          = (4, "Functions", False)
    VARIABLE                          = (5, "Workspace variables", True)
    OBSERVABLE                        = (6, "Observables", True)
    POI                               = (7, "Parameters of Interest (POI)", True)
    GLOBAL_OBSERVABLE                 = (8, "Global observables", True)
    NUISANCE_PARAMETER                = (9, "Nuisance parameters", True)
    CONSTRAINED_NUISANCE_PARAMETER    = (10, "Nuisance parameters with an associated constraint pdf", True)
    UNCONSTRAINED_NUISANCE_PARAMETER  = (11, "Nuisance parameters without an associated constraint pdf", True)
    CONSTRAINT                        = (12, "Tuple of constraint pdf and the associated nuisance parameter and global observable", False)
    AUXILIARY                         = (13, "Auxiliary variables (All variables except POIs, observables, global observables and "
                                             "nuisance parameters)", True)
    CORE                              = (14, "Nuisance parameters, global observables and POIs", True)
    MUTABLE                           = (15, "Mutable parameters (Nuisance parameters, global observables, POIs and floating auxiliary"
                                             " parameters)", True)
    GAUSSIAN_CONSTRAINT_NP            = (16, "Nuisance parameters with Gaussian constraint pdf", True)
    POISSON_CONSTRAINT_NP             = (17, "Nuisance parameters with Poisson constraint Pdf", True)
    
    def __new__(cls, value:int, description:str="", is_variable:bool=False):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.is_variable = is_variable
        return obj

class SetValueMode(GeneralEnum):
    UNCHANGED = (0, None)
    FIX       = (1, True)
    FREE      = (2, False)

    __aliases__ = {
        'FLOAT': 'FREE',
        'PROFILE': 'FREE'
    }
    
    def __new__(cls, value:int, const_state:Optional[bool]=None):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.const_state = const_state
        return obj