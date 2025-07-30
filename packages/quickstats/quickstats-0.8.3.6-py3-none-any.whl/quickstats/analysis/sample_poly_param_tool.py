import json
from typing import List, Dict, Optional, Union, Tuple, Any

from quickstats import AbstractObject, semistaticmethod

from quickstats.maths.numerics import to_rounded_float
from quickstats.utils.common_utils import in_notebook


class SamplePolyParamTool(AbstractObject):
    """
    A tool for polynomial parameterization of data samples.

    This class provides functionality for initializing symbolic representations,
    creating and manipulating formulas, and solving for coefficients in
    polynomial parameterizations.

    Parameters
    ----------
    verbosity : int or str, optional
        Level of verbosity for logging output, default is "INFO"
    """

    def __init__(self, verbosity: Optional[Union[int, str]] = "INFO"):
        super().__init__(verbosity=verbosity)

    def initialize_symbols(
        self,
        parameters: List[str],
        coefficients: List[str],
        bases: List[str],
        latex_map: Optional[Dict[str, str]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Initialize symbolic representations for parameters, coefficients, and bases.

        Parameters
        ----------
        parameters : list of str
            List of parameter names to be symbolized
        coefficients : list of str
            List of coefficient names to be symbolized
        bases : list of str
            List of basis names to be symbolized
        latex_map : dict, optional
            Mapping of variable names to their LaTeX representations

        Returns
        -------
        tuple
            Three dictionaries containing the symbolic representations for
            parameters, coefficients, and bases
        """
        from sympy import Symbol
        if latex_map is None:
            latex_map = {}
        parameter_symbols = {}
        coefficient_symbols = {}
        basis_symbols = {}
        for parameter in parameters:
            parameter_symbols[parameter] = Symbol(latex_map.get(parameter, parameter))
        for coefficient in coefficients:
            coefficient_symbols[coefficient] = Symbol(latex_map.get(coefficient, coefficient))
        basis_symbols = {}
        for basis in bases:
            basis_symbols[basis] = Symbol(basis)
        return parameter_symbols, coefficient_symbols, basis_symbols

    @semistaticmethod
    def initialize_formula(
        self,
        formula_str: str,
        parameters: Dict[str, Any],
        coefficients: Dict[str, Any],
        latex_map: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Initialize a symbolic formula from a string representation.

        Parameters
        ----------
        formula_str : str
            String representation of the formula
        parameters : dict
            Dictionary of parameter symbols
        coefficients : dict
            Dictionary of coefficient symbols
        latex_map : dict, optional
            Mapping of variable names to their LaTeX representations

        Returns
        -------
        sympy.Expr
            Symbolic representation of the formula

        Raises
        ------
        ValueError
            If a variable in the formula is both a parameter and a coefficient,
            or neither a parameter nor a coefficient
        """
        from sympy import simplify
        formula = simplify(formula_str)
        if latex_map is None:
            return formula
        symbols = list(formula.free_symbols)
        subs = []
        for symbol in symbols:
            is_parameter, is_coefficient = False, False
            name = symbol.name
            if name in parameters:
                is_parameter = True
            if name in coefficients:
                is_coefficient = True
            if is_parameter and is_coefficient:
                raise ValueError(
                    f'variable "{name}" in the formula "{formula_str}" can not be both '
                    'a parameter and a coefficient'
                )
            elif (not is_parameter) and (not is_coefficient):
                raise ValueError(
                    f'variable "{name}" in the formula "{formula_str}" is neither a '
                    'parameter or a coefficient'
                )
            elif is_parameter and (name in latex_map):
                subs.append([symbol, parameters[name]])
            elif is_coefficient and (name in latex_map):
                subs.append([symbol, coefficients[name]])
        formula = formula.subs(subs)
        return formula

    def get_basis_symbol_names(
        self,
        basis_values: List[Dict[str, float]],
        parameters: List[str],
        latex_map: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Generate symbolic names for basis elements based on their parameter values.

        Parameters
        ----------
        basis_values : list of dict
            List of dictionaries containing parameter values for each basis element
        parameters : list of str
            List of parameter names
        latex_map : dict, optional
            Mapping of variable names to their LaTeX representations

        Returns
        -------
        list of str
            List of symbolic names for the basis elements
        """
        if latex_map is None:
            latex_map = {}
        symbol_names = []
        for values in basis_values:
            components = []
            for parameter in parameters:
                value = to_rounded_float(values[parameter])
                component = f"{latex_map.get(parameter, parameter)}={value}"
                components.append(component)
            symbol_name = f"Yield({','.join(components)})"
            symbol_names.append(symbol_name)
        return symbol_names

    def display_expression(self, expr: Any) -> None:
        """
        Display a symbolic expression.

        Parameters
        ----------
        expr : sympy.Expr
            Symbolic expression to display
        """
        if not in_notebook():
            self.stdout.info(str(expr), bare=True)
        else:
            from IPython import display
            display.display(expr)

    def display_sets(self, *objects: Any) -> None:
        """
        Display objects as elements of a finite set.

        Parameters
        ----------
        *objects : Any
            Objects to display as set elements
        """
        from sympy import FiniteSet
        self.display_expression(FiniteSet(*objects))

    def display_equation(self, variable: Any, expression: Any) -> None:
        """
        Display an equation with a variable and an expression.

        Parameters
        ----------
        variable : sympy.Symbol
            Variable on the left side of the equation
        expression : sympy.Expr
            Expression on the right side of the equation
        """
        from sympy import Eq
        self.display_expression(Eq(variable, expression))

    def solve_coefficients(
        self,
        formula: Any,
        parameter_symbols: Dict[str, Any],
        coefficient_symbols: Dict[str, Any],
        basis_symbols: Dict[str, Any],
        basis_value_map: Dict[str, Dict[str, float]]
    ) -> List[Dict[Any, Any]]:
        """
        Solve for coefficient values based on the formula and basis samples.

        Parameters
        ----------
        formula : sympy.Expr
            Symbolic formula
        parameter_symbols : dict
            Dictionary of parameter symbols
        coefficient_symbols : dict
            Dictionary of coefficient symbols
        basis_symbols : dict
            Dictionary of basis symbols
        basis_value_map : dict
            Mapping of basis names to their parameter values

        Returns
        -------
        list of dict
            List of solution dictionaries for coefficients
        """
        from sympy import simplify, solve
        equations = []
        for basis_name, basis_values in basis_value_map.items():
            subs = [(parameter_symbols[k], simplify(v)) for k, v in basis_values.items()]
            equation_i = formula.subs(subs) - basis_symbols[basis_name]
            equations.append(equation_i)
        solutions = solve(equations, list(coefficient_symbols.values()), dict=True)
        return solutions

    def _get_inverse_latex_map(self, latex_map: Dict[str, str]) -> Dict[str, str]:
        """
        Invert a LaTeX mapping.

        Parameters
        ----------
        latex_map : dict
            Mapping of variable names to their LaTeX representations

        Returns
        -------
        dict
            Inverted mapping from LaTeX representations to variable names
        """
        return {v: k for k, v in latex_map.items()}

    def get_delatexed_formula(
        self,
        formula: Any,
        inverse_latex_map: Dict[str, str]
    ) -> Any:
        """
        Convert a formula with LaTeX symbols back to ordinary variable names.

        Parameters
        ----------
        formula : sympy.Expr
            Symbolic formula with LaTeX symbols
        inverse_latex_map : dict
            Mapping from LaTeX representations to variable names

        Returns
        -------
        sympy.Expr
            Formula with ordinary variable names
        """
        symbols = list(formula.free_symbols)
        subs = []
        for symbol in symbols:
            name = symbol.name
            if name in inverse_latex_map:
                subs.append([symbol, inverse_latex_map[name]])
        formula = formula.subs(subs)
        return formula

    def run_linear_combination(
        self,
        formula: str,
        parameters: List[str],
        coefficients: List[str],
        basis_samples: Dict[str, Dict[str, float]],
        latex_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, List[Any]]:
        """
        Run linear combination parameterization on basis samples.

        Parameters
        ----------
        formula : str
            String representation of the formula to use
        parameters : list of str
            List of parameter names
        coefficients : list of str
            List of coefficient names
        basis_samples : dict
            Mapping of sample names to their parameter values
        latex_map : dict, optional
            Mapping of variable names to their LaTeX representations

        Returns
        -------
        dict
            Dictionary containing parameterization results

        Raises
        ------
        ValueError
            If the number of basis samples doesn't match the number of coefficients
        RuntimeError
            If the system of equations can't be solved or has non-unique solutions
        """
        if len(coefficients) != len(basis_samples):
            raise ValueError(
                "number of basis samples must equal the number of coefficients in the polynomial"
            )
        param_data = {}
        param_data['sample'] = []
        param_data['expression'] = []
        for parameter in parameters:
            param_data[parameter] = []
        samples = list(basis_samples.keys())
        basis_values = list(basis_samples.values())
        bases = self.get_basis_symbol_names(basis_values, parameters, latex_map=latex_map)
        parameter_symbols, coefficient_symbols, basis_symbols = self.initialize_symbols(
            parameters,
            coefficients,
            bases,
            latex_map=latex_map
        )
        basis_value_map = dict(zip(bases, basis_values))
        basis_sample_map = dict(zip(bases, samples))
        formula_expr = self.initialize_formula(
            formula,
            parameter_symbols,
            coefficient_symbols,
            latex_map=latex_map
        )
        self.stdout.info("Formula:", bare=True)
        self.display_expression(formula_expr)
        self.stdout.info("Parameters:", bare=True)
        self.display_sets(*parameter_symbols.values())
        self.stdout.info("Coefficients:", bare=True)
        self.display_sets(*coefficient_symbols.values())
        solutions = self.solve_coefficients(
            formula_expr,
            parameter_symbols,
            coefficient_symbols,
            basis_symbols,
            basis_value_map
        )
        if len(solutions) == 0:
            raise RuntimeError("unable to solve the system of linear equations")
        elif len(solutions) > 1:
            raise RuntimeError("system of linear equations gives non-unique solutions")
        solution = solutions[0]
        self.stdout.info("Solutions:", bare=True)
        for coefficient in coefficient_symbols.values():
            self.display_equation(coefficient, solution[coefficient])
        subs = [(k, v) for k, v in solution.items()]
        resolved_formula = formula_expr.subs(subs).expand()
        coefficient_map = {
            basis: resolved_formula.coeff(basis_symbols[basis]) for basis in bases
        }
        inverse_latex_map = self._get_inverse_latex_map(latex_map)
        coefficient_map_delatexed = {}
        for basis, coefficient_formula in coefficient_map.items():
            coefficient_map_delatexed[basis] = self.get_delatexed_formula(
                coefficient_formula, inverse_latex_map
            )
        self.stdout.info("Contribution from basis sample:", bare=True)
        for basis, expr in coefficient_map.items():
            self.display_equation(basis_symbols[basis], expr)
        for basis in bases:
            param_data['sample'].append(basis_sample_map[basis])
            for parameter, value in basis_value_map[basis].items():
                param_data[parameter].append(to_rounded_float(value))
            param_data['expression'].append(str(coefficient_map_delatexed[basis]))
        return param_data

    def run_parameterization(
        self,
        formula: str,
        parameters: List[str],
        coefficients: List[str],
        basis_samples: Dict[str, Dict[str, float]],
        method: str = 'linear_combination',
        latex_map: Optional[Dict[str, str]] = None,
        saveas: Optional[str] = None
    ) -> Dict[str, List[Any]]:
        """
        Run a parameterization on basis samples using the specified method.

        Parameters
        ----------
        formula : str
            String representation of the formula to use
        parameters : list of str
            List of parameter names
        coefficients : list of str
            List of coefficient names
        basis_samples : dict
            Mapping of sample names to their parameter values
        method : str, optional
            Parameterization method to use, default is 'linear_combination'
        latex_map : dict, optional
            Mapping of variable names to their LaTeX representations
        saveas : str, optional
            File path to save the results as JSON

        Returns
        -------
        dict
            Dictionary containing parameterization results

        Raises
        ------
        ValueError
            If an unsupported method is specified
        """
        if method == 'linear_combination':
            result = self.run_linear_combination(
                formula,
                parameters,
                coefficients,
                basis_samples,
                latex_map=latex_map
            )
        else:
            raise ValueError(f"unsupported method: {method}")
        if saveas is not None:
            with open(saveas, 'w') as file:
                json.dump(result, file, indent=2)
        return result