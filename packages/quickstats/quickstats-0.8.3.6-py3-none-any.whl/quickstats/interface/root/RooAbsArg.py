from typing import Dict, Union, List, Optional, Sequence

class RooAbsArg:
    
    @staticmethod
    def set_parameter_attributes(parameter:"ROOT.RooAbsArg",
                                 vnom:Optional[float]=None,
                                 vmin:Optional[float]=None,
                                 vmax:Optional[float]=None,
                                 verr:Optional[float]=None,
                                 const:Optional[bool]=None):
        if (const is not None) and hasattr(parameter, "setConstant"):
            parameter.setConstant(const)
        # special case for RooCategory: set index instead
        if parameter.InheritsFrom("RooCategory"):
            if not ((vmin, vmax, verr) == (None, None, None)):
                raise ValueError(f'can not set attributes for {parameter.GetName()}: '
                                 f'only index value can be set for parameter of the type {parameter.ClassName()}')
            if isinstance(vnom, float):
                assert vnom.is_integer()
                vnom = int(vnom)
            assert isinstance(vnom, (int, float))
            parameter.setIndex(vnom)
            return
        if not parameter.InheritsFrom("RooRealVar"):
            if not (vnom, vmin, vmax, verr) == (None, None, None, None):
                raise ValueError(f'can not set attributes for {parameter.GetName()}: '
                                 f'not supported for parameter of the type {parameter.ClassName()}')
            return
        # only set attributes for RooRealVar
        orig_vnom = parameter.getVal()
        if vnom is None:
            vnom = orig_vnom
        # expand parameter range if requested value is outside the requested range
        if (vmin is not None):
            if (vnom < vmin):
                vmin = vnom
            parameter.setMin(vmin)
        elif (vnom < parameter.getMin()):
            parameter.setMin(vnom)
        if (vmax is not None):
            if (vnom > vmax):
                vmax = vnom
            parameter.setMax(vmax)
        elif (vnom > parameter.getMax()):
            parameter.setMax(vnom)
        # set parameter value
        if vnom != orig_vnom:
            parameter.setVal(vnom)
        # set error value
        if verr is not None:
            parameter.setError(verr)