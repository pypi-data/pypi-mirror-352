from typing import Dict, Union, List, Optional, Tuple
import os

import numpy as np

from quickstats import semistaticmethod, AbstractObject
from quickstats import GeneralEnum
from quickstats.interface.cppyy import is_null_ptr
from .RooArgSet import RooArgSet

class ObjectType(GeneralEnum):
    
    PDF = (0, "pdf", "pdf")
    OBS = (1, "observables", "observable")
    POIS = (2, "parameters of interest", "parameter of interest")
    NUIS = (3, "nuisance parameters", "nuisane parameter")
    GLOBS = (4, "global observables", "global observable")
    
    def __new__(cls, value:int, plural_str:str, singular_str:str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.plural_str = plural_str
        obj.singular_str = singular_str
        return obj

class ModelConfig(AbstractObject):
    
    @semistaticmethod
    def sanity_check(self, mc:"ROOT.RooStats.ModelConfig"):
        pass_check = True
        def check_objects(objects, object_type:ObjectType,
                          require_nonempty:bool=True,
                          require_class:Optional[str]=None,
                          require_dependence:Optional["ROOT.RooAbsArg"]=None,
                          dep_object_type:ObjectType=ObjectType.PDF):
            if is_null_ptr(objects):
                self.stdout.error(f'{object_type.plural_str} not defined in model config')
                return False
            if require_nonempty and (not objects):
                self.stdout.error(f'{object_type.plural_str} is empty')
                return False
            if require_class is not None:
                assert objects.InheritsFrom("RooArgSet")
                invalid_objects = RooArgSet.exclude_by_class(objects, require_class)
                if invalid_objects:
                    for invalid_object in invalid_objects:
                        classname = invalid_object.ClassName()
                        name = invalid_object.GetName()
                        self.stdout.error(f'{object_type.singular_str} "{name}" is an instance of '
                                          f'{classname} but not {require_class}')
                    return False
            if require_dependence is not None:
                assert objects.InheritsFrom("RooArgSet")
                assert require_dependence.InheritsFrom("RooAbsArg")
                dependent_objects = RooArgSet.select_dependent_parameters(objects, require_dependence)
                invalid_objects = objects.Clone()
                invalid_objects.remove(dependent_objects)
                if invalid_objects:
                    for invalid_object in invalid_objects:
                        classname = invalid_object.ClassName()
                        name = invalid_object.GetName()
                        self.stdout.error(f'{dep_object_type.singular_str} does not depend on '
                                          f'{object_type.singular_str} "{name}"')
                    return False
            return True
        pdf = mc.GetPdf()
        # check pdf
        pass_check &= check_objects(pdf, ObjectType.PDF)
        # skip subsequent checks if pdf does not exist
        if not pdf:
            self.stdout.error(f'PDF not defined in model config.')
            return False
        # check observables
        pass_check &= check_objects(mc.GetObservables(), ObjectType.OBS)
        # check parameters of interest
        pass_check &= check_objects(mc.GetParametersOfInterest(), ObjectType.POIS,
                                   require_class="RooRealVar", require_dependence=pdf)
        # check nuisance parameters
        pass_check &= check_objects(mc.GetNuisanceParameters(), ObjectType.NUIS,
                                    require_nonempty=False, require_class="RooRealVar",
                                    require_dependence=pdf)
        # check global observables
        pass_check &= check_objects(mc.GetGlobalObservables(), ObjectType.GLOBS,
                                    require_nonempty=False, require_class="RooRealVar",
                                    require_dependence=pdf)
       
        # check factorize pdf (needed?)
        
        return pass_check
    