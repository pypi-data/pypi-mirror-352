from __future__ import annotations

from typing import Any, Optional, Callable, List, Dict, Container, Union, Tuple
from numbers import Real
import math

import numpy as np

from quickstats import NamedObject
from quickstats.core.typing import is_container, ArrayLike, NOTSET
from quickstats.utils.string_utils import PlainStr
from .binning import Binning
from .arguments import Argument, ArgumentSet
from .ranges import Range, NamedRanges

class Variable(Argument):
    """
    Base class for mathematical variables.

    Attributes
    ----------
    name : str
        The name of the variable.
    value : Any
        The current value of the variable.
    unit : Optional[str]
        The unit of the variable (e.g., meters, seconds).
    domain : Optional[Union[Callable[[Any], bool], Container]]
        A function or container that checks whether the value lies within the domain.
    description : Optional[str]
        A short description or metadata for the variable.
    tags : Optional[List[str]]
        A list of tags for the variable.
    verbosity : str, default='INFO'
        The verbosity level for logging or diagnostics.
    constraints : Optional[List[Callable[[Any], bool]]]
        A list of additional constraints for the variable.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        value: Any = None,
        unit: Optional[str] = None,
        domain: Optional[Union[Callable[[Any], bool], Container]] = None,
        constraints: Optional[List[Callable[[Any], bool]]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        verbosity: Optional[str] = None,
        **kwargs
    ):
        NamedObject.__init__(
            self,
            name=name,
            tags=tags,
            description=description,
            verbosity=verbosity,
            **kwargs
        )
        self.unit = unit
        self.domain = domain
        self.constraints = constraints or []
        self.value = value

    @property
    def unit(self) -> Optional[str]:
        """The unit of the variable."""
        return self._unit

    @unit.setter
    def unit(self, value: Optional[str]) -> None:
        self._unit = value

    @property
    def domain(self) -> Optional[Union[Callable[[Any], bool], Container]]:
        """The domain of the variable."""
        return self._domain

    @domain.setter
    def domain(self, value: Optional[Union[Callable[[Any], bool], Container]]) -> None:
        if value is not None and not is_container(value) and not callable(value):
            raise TypeError("`domain` must be a callable or implement the container protocol.")
        self._domain = value

    def satisfy_domain(self, value: Any) -> bool:
        if self.domain is not None:
            if callable(self.domain) and not self.domain(value):
                return False
            if not callable(self.domain) and value not in self.domain:
                return False
        return True

    def satisfy_constraints(self, value: Any) -> bool:
        if any(not constraint(value) for constraint in self.constraints):
            return False
        return True

    def validate_value(self, value: Any) -> bool:
        if not self.satisfy_domain(value):
            raise ValueError('`value` is outside the domain of the variable')
        if not self.satisfy_constraints(value):
            raise ValueError('`value` does not satisfy one or more of the constraints of the variable')
        return value

    def _repr_dict_(self) -> Dict[str, Optional[str]]:
        repr_items = super()._repr_dict_()
        repr_items.update({
            "value": self.value,
        })
        return repr_items

class RealVariable(Variable):
    """
    A variable representing real numbers with additional properties such as errors and ranges.

    Attributes
    ----------
    errors : Optional[Tuple[float, float]]
        The lower and upper errors of the variable.
    error : Optional[float]
        The maximum error (computed from `errors`).
    errlo : Optional[float]
        The lower error.
    errhi : Optional[float]
        The upper error.
    range : Range
        The range of allowable values for the variable.
    named_ranges : NamedRanges
        A set of named ranges for the variable.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        value: Optional[Real] = None,
        errors: Optional[ArrayLike] = None,
        range: Optional[Union[Range, ArrayLike]] = None,
        named_ranges: Optional[Union[NamedRanges, Dict[str, Any]]] = None,
        unit: Optional[str] = None,
        nbins: Optional[int] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        verbosity: Optional[str] = None,
        **kwargs
    ):
        self._value = NOTSET
        super().__init__(
            name=name,
            value=value,
            domain=range,
            unit=unit,
            description=description,
            tags=tags,
            verbosity=verbosity,
            **kwargs
        )
        self.errors = errors
        self.nbins = nbins
        self.named_ranges = named_ranges

    def validate_value(self, value: Any) -> bool:
        """
        Validate the value against the domain and constraints. If the value is None,
        assign a default value based on the range.
    
        Parameters
        ----------
        value : Any
            The value to validate.
    
        Returns
        -------
        bool
            True if the value is valid.
    
        Raises
        ------
        TypeError
            If the value is not a real number.
        ValueError
            If the value does not satisfy the constraints.
        """
        if value is None:
            value = self.default_value()
    
        if not isinstance(value, Real):
            raise TypeError('`value` of a RealVariable must be a real number')
    
        if not self.satisfy_domain(value):
            fallback = self.fallback_value(self.domain, value)
            self.stdout.warning(
                f"The value {value} is outside the domain {self.domain}. Adjusting to fallback value: {fallback}."
            )
            value = fallback
    
        if not self.satisfy_constraints(value):
            raise ValueError('`value` does not satisfy one or more of the constraints of the variable')
    
        return value

    def fallback_value(self, range: Range, value: Real) -> Real:
        """
        Adjust the given value to the nearest valid value within the specified range.
    
        Parameters
        ----------
        range : Range
            The range object that defines the valid bounds (min and max).
        value : Real
            The value to adjust if it falls outside the range.
    
        Returns
        -------
        Real
            The adjusted value within the valid bounds of the range.
    
        Notes
        -----
        If the provided value is greater than the upper bound (`range.max`), 
        it is clamped to the maximum value of the range. Similarly, if the 
        value is less than the lower bound (`range.min`), it is clamped to 
        the minimum value of the range. If the value is already within the 
        range, it is returned unchanged.

        Override this method to customize the behavior of fallback value adjustment.
        """
        if value > range.max:
            return range.max
        elif value < range.min:
            return range.min
        return value

    def default_value(self) -> Real:
        """
        Compute the default value for the variable based on the range.
    
        Returns
        -------
        Real
            The default value.
    
        Notes
        -----
        The default value is determined as:
        - The midpoint of the range if the range is finite.
        - The minimum of the range if only the lower bound is finite.
        - The maximum of the range if only the upper bound is finite.
        - 0 if the range is completely unbounded.
        """
        if self.range.is_finite():
            return (self.range.min + self.range.max) / 2.0
        elif self.range.is_finite_min():
            return self.range.min
        elif self.range.is_finite_max():
            return self.range.max
        return 0.0

    def _repr_dict_(self) -> Dict[str, Optional[str]]:
        """
        Returns a dictionary of attributes to be shown in the `repr`.

        This implementation includes the range, errors, and value.

        Returns
        -------
        Dict[str, Optional[str]]
            A dictionary of attribute names and their values to be shown in the `repr`.
        """
        repr_items = super()._repr_dict_()
        repr_items.update({
            "range": self._format_range(),
            "errors": self.errors,
            "nbins": self.nbins
        })
        return repr_items

    def _format_range(self) -> Optional[str]:
        """
        Format the range for representation.

        Returns
        -------
        Optional[str]
            A string representing the range in the format (min, max) or [min, max].
        """
        if self.range is None:
            return None

        min_value = self.range.min
        max_value = self.range.max
        left_bracket = "[" if self.range.lbound else "("
        right_bracket = "]" if self.range.rbound else ")"
        return PlainStr(f"{left_bracket}{min_value}, {max_value}{right_bracket}")

    @property
    def errors(self) -> Optional[np.ndarray]:
        """The lower and upper errors of the variable."""
        if self._errors is None:
            return None
        return np.copy(self._errors)

    @errors.setter
    def errors(self, value: Optional[ArrayLike]) -> None:
        if value is None:
            self._errors = None
        else:
            value = np.asarray(value, dtype=float)
            if value.ndim == 0:
                self._errors = np.array([value, value], dtype=float)
            elif value.ndim == 1 and len(value) in (1, 2):
                self._errors = (
                    np.array([value[0], value[0]], dtype=float) if len(value) == 1 else value
                )
            else:
                raise ValueError("`errors` must be a scalar, a 1-element array, or a 2-element array.")

    @property
    def error(self) -> Optional[float]:
        """The maximum error of the variable."""
        return None if self._errors is None else np.max(self._errors)

    @property
    def errorlo(self) -> Optional[float]:
        """The lower error of the variable."""
        return None if self._errors is None else self._errors[0]

    @property
    def errorhi(self) -> Optional[float]:
        """The upper error of the variable."""
        return None if self._errors is None else self._errors[1]

    @property
    def range(self) -> Range:
        """The range of allowable values for the variable."""
        return self._domain

    @range.setter
    def range(self, value: Optional[Union[Range, ArrayLike]]) -> None:
        self.domain = value

    @property
    def domain(self) -> Range:
        return self._domain

    @domain.setter
    def domain(self, value: Optional[Union[Range, ArrayLike]]) -> None:
        """
        Set the domain of the variable. If the current value falls outside the new domain,
        adjust the value using the `fallback_value` method.
    
        Parameters
        ----------
        value : Optional[Union[Range, ArrayLike]]
            The new domain to set. Can be a Range object or an array-like representation.
    
        """
        domain = Range.create(value)
        if self.value is not NOTSET and self.value not in domain:
            fallback = self.fallback_value(domain, self.value)
            self.stdout.warning(
                f"The value {self.value} is outside the new domain {domain}. Adjusting to fallback value: {fallback}."
            )
            self._value = fallback
        self._domain = domain

    @property
    def data(self) -> Dict[str, Any]:
        return {
            'value': self.value,
            'range': (self.range.min, self.range.max),
            'errors': None if self.errors is None else (self.errorlo, self.errorhi)
        }

    @property
    def nbins(self) -> Optional[int]:
        return self._nbins

    @nbins.setter
    def nbins(self, value: Optional[int]):
        if value is None:
            self._nbins = None
        else:
            self._nbins = int(value)

    @property
    def binning(self) -> Optional[Binning]:
        if self.nbins is None:
            return None
        return Binning(self.nbins, self.range)

    @property
    def named_ranges(self) -> NamedRanges:
        """A set of named ranges for the variable."""
        return self._named_ranges

    @named_ranges.setter
    def named_ranges(self, value: Any) -> None:
        value = value or {}
        self._named_ranges = NamedRanges.create(value)

    def reset_range(self) -> None:
        """
        Reset the range of the variable to the default range [-inf, inf].
    
        This method sets the range of the variable to its default, which allows 
        the variable to take any real value without restrictions.
    
        Examples
        --------
        >>> var = RealVariable(name="x", value=10, range=(0, 20))
        >>> print(var.range)
        Range(min=0, max=20, lbound=True, rbound=True)
        >>> var.reset_range()
        >>> print(var.range)
        Range(min=-inf, max=inf, lbound=True, rbound=True)
        """
        self.range = None

    def set_data(
        self,
        value: Optional[Real] = NOTSET,
        range: Optional[Union[Range, ArrayLike]] = NOTSET,
        errors: Optional[ArrayLike] = NOTSET
    ):
        """
        Update the data properties of the RealVariable.
    
        Parameters
        ----------
        value : Optional[Real], default=NOTSET
            The new value for the variable. Must be a real number.
        range : Optional[Union[Range, ArrayLike]], default=NOTSET
            The new range for the variable. Can be a Range object or an array-like 
            object specifying [min, max] or (min, max).
        errors : Optional[ArrayLike], default=NOTSET
            The new errors for the variable. Can be a scalar, 1-element array, 
            or 2-element array specifying lower and upper errors.
        """
        # bypass range check
        if value is not NOTSET:
            self._value = NOTSET
        if range is not NOTSET:
            self.range = range
        if value is not NOTSET:
            self.value = value
        if errors is not NOTSET:
            self.errors = errors

    def randomize(self, size: int = 1, seed: Optional[int] = None, code: int = 4):
        if self.errors is None:
            raise RuntimeError(
                f'Cannot randomize variable "{self.name}": '
                f'variable does not have error values defined')
        if seed is not None:
            np.random.seed(seed)
        x = np.random.normal(size=size)
        from quickstats.maths.interpolation import piecewise_interpolate
        result = self.value + piecewise_interpolate(
            x,
            nominal=self.value,
            low=self.value - self.errorlo,
            high=self.value + self.errorhi,
            boundary=1.,
            code=code
        )
        return result

class RealVariableSet(ArgumentSet):
    """
    A specialized ArgumentSet for managing a collection of RealVariable objects.
    """

    def __init__(
        self,
        components: Optional[Union[
            RealVariable,
            List[RealVariable],
            Tuple[RealVariable, ...],
            ArgumentSet,
            Dict[str, Union[float, ArrayLike]]
        ]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        verbosity: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            components=components,
            name=name,
            type=RealVariable,
            description=description,
            tags=tags,
            verbosity=verbosity,
            **kwargs
        )

    @classmethod
    def from_dict(cls, source: Dict[str, Any], **kwargs) -> RealVariableSet:
        components = []
        for name, data in source.items():
            component = RealVariable(name=name, **data)
            components.append(component)
        return cls(components, **kwargs)
        
    def _clone(
        self,
        components: Optional[Union[List[Argument], Tuple[Argument, ...], ArgumentSet]] = None,
        name: Optional[str] = None
    ):
        return type(self)(
            components=components,
            name=name or self.name,
            description=self.description,
            tags=list(self.tags),
            verbosity=self.init_verbosity,
        )

    def _parse_component(
        self,
        name: str,
        data: Union[float, ArrayLike]
    ) -> RealVariable:
        """
        Parse input data into a RealVariable.
    
        Parameters
        ----------
        name : str
            The name of the RealVariable to create.
        data : Union[float, ArrayLike]
            The value of the variable, which can be:
            - A single float value.
            - A 1D numpy array or list/tuple of size 3 in the format [value, min, max].
    
        Returns
        -------
        RealVariable
            A new RealVariable object initialized with the provided data.
        """
        if isinstance(data, np.ndarray):
            if data.ndim == 0:
                data = float(data)
            elif data.ndim == 1:
                data = data.tolist()
            else:
                raise ValueError('`data` of a RealVariable must be a real number or a 1D-array of real numbers')
        if isinstance(data, Real):
            return RealVariable(name, data)
        if isinstance(data, (list, tuple)):
            if not len(data) == 3:
                raise ValueError(
                    f"`data` must have size 3 (value, min, max) for a RealVariable. "
                    f"Received: {data} with size {len(data)}."
                )
            return RealVariable(name, data[0], range=(data[1], data[2]))
        raise TypeError(f'Invalid `data` format for a RealVariable')

    @property
    def errors(self) -> Dict[str, Optional[Tuple[float, float]]]:
        return {name: component.errors for name, component in self._components.items()}

    @property
    def data(self) -> Dict[str, Optional[Tuple[float, float]]]:
        return {name: component.data for name, component in self._components.items()}

    def append(
        self,
        value: Union[
            RealVariable,
            List[RealVariable],
            Tuple[RealVariable, ...],
            ArgumentSet,
            Dict[str, Union[float, ArrayLike]]
        ]
    ) -> None:
        """
        Add components to the ArgumentSet.

        Parameters
        ----------
        value : Union[RealVariable, List[RealVariable], Tuple[RealVariable, ...], ArgumentSet, Dict[str, Union[float, ArrayLike]]]
            A single RealVariable, a list/tuple of RealVariables, a ArgumentSet or a
            dictionary that maps the name of the variable to the data in the form 
            <name> : <value> or <name> : (<value, min, max>)

        Raises
        ------
        TypeError
            If a component is not of the allowed type.
        ValueError
            If a component with a duplicate name is found.
        """
        if isinstance(value, dict):
            for name, data in value.items():
                component = self._parse_component(name, data)
                self._add_component(component)
        else:
            super().append(value)
        
    def select(
        self,
        names: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        new_name: Optional[str] = None,
        to_list: bool = False
    ) -> RealVariableSet:
        """
        Select a subset of RealVariable objects based on names or tags.

        Parameters
        ----------
        names : Optional[List[str]], optional
            A list of names to select. Defaults to None.
        tags : Optional[List[str]], optional
            A list of tags to filter by. Defaults to None.
        new_name : Optional[str], optional
            The name of the resulting RealVariableSet. Defaults to None.

        Returns
        -------
        RealVariableSet
            A new RealVariableSet containing the selected RealVariable components.
        """
        return super().select(names=names, tags=tags, new_name=new_name, to_list=to_list)

    def copy_data(self, other: RealVariableSet) -> None:
        if not isinstance(other, RealVariableSet):
            raise TypeError('`other` must be an instance of RealVariableSet')
        for parameter in self:
            if parameter.name in other:
                other_parameter = other[parameter.name]
                parameter.set_data(**other_parameter.data)

#class RandomVariables