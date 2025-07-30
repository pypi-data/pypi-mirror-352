from typing import Dict, Union, List, Optional, Sequence

from quickstats.utils.common_utils import combine_dict
from quickstats.utils.string_utils import remove_whitespace, split_str

class RooParamSetupParser:
    
    @staticmethod
    def parse_expr(param_setup_expr: str):
        """
        Parse a parameter setup expression into a dictionary format.

        This method interprets parameter configuration strings in a variety of formats. Each format
        specifies the parameter's nominal value, range, and error value in a unique way.

        The accepted formats for `param_setup_expr` are:
        - Set only the nominal value: "<param_name>=<nominal_value>"
        - Set only the range: "<param_name>=<min_value>_<max_value>"
        - Set both nominal value and range: "<param_name>=<nominal_value>_<min_value>_<max_value>"
        - Set nominal value, range, and error: "<param_name>=<nominal_value>_<min_value>_<max_value>_<error_value>"
        If a value is not specified, the parameter's original value will be kept.

        Parameters
            ----------
            param_setup_expr : str
                The expression string containing parameter setups to be parsed.

            Returns
            -------
            dict
                A dictionary containing parsed parameter setup. Each key is a parameter name, 
                and its associated value can be None, a single float, or a list of floats 
                depending on the provided format.

            Raises
            ------
            ValueError
                If the provided `param_setup_expr` doesn't match any of the accepted formats.

            Examples
            --------
            >>> parse_expr("param_1,param_2=0.5,param_3=-1,param_4=1,param_5=_0_100,param_6=__100,param_7=_0_")
            {'param_1': None, 'param_2': 0.5, 'param_3': -1.0, 'param_4': 1.0, 'param_5': [None, 0.0, 100.0], 'param_6': [None, None, 100.0], 'param_7': [None, 0.0, None]}
        """
        param_setup_expr = remove_whitespace(param_setup_expr)
        param_expr_list  = split_str(param_setup_expr, sep=',', remove_empty=True)
        param_setup = {}
        for param_expr in param_expr_list:
            name, *values = param_expr.split('=')
            # case only parameter name is given
            if not values:
                param_setup[name] = None
            # case both parameter name and value is given
            elif len(values) == 1:
                values = [float(v) if v else None for v in split_str(values[0], sep="_")]
                if len(values) == 1:
                    values = values[0]
                param_setup[name] = values
            else:
                raise ValueError(f'invalid parameter setup expression: {param_setup_expr}')
        return param_setup
    
    @staticmethod
    def parse(params: "ROOT.RooArgSet",
              param_setup: Optional[Union[float, Dict, Sequence]] = None,
              fill_missing: bool = False,
              strict_match: bool = True):
        """
        Parses the parameter setup based on the input parameter set.

        Parameters
        ----------
        params : ROOT.RooArgSet
            The input parameter set.
        param_setup : float, dict or sequence, optional
            The setup for the parameters.
        fill_missing : bool, optional
            If True, missing values will be filled. Default is False.
        strict_match : bool, optional
            If True, only strictly matched parameters will be considered. Default is True.

        Returns
        -------
        dict
            Dictionary of parsed parameter setup.
        """
        if not params.ClassName() == "RooArgSet":
            import ROOT
            params = ROOT.RooArgSet(params)
        if isinstance(param_setup, (float, int)):
            param_value = param_setup
            param_setup = {param.GetName(): param_value for param in params}
        elif isinstance(param_setup, Sequence):
            if len(params) != len(param_setup):
                raise ValueError('number of parameters do not match the number of setup values')
            param_names = [param.GetName() for param in params]
            param_setup = {param_name: value for param_name, value in zip(param_names, param_setup)}
        elif isinstance(param_setup, dict):
            if strict_match:
                param_setup_tmp = combine_dict(param_setup)
                param_setup = {}
                for param in params:
                    param_name = param.GetName()
                    if param_name in param_setup_tmp:
                        param_setup[param_name] = param_setup_tmp[param_name]
                    elif fill_missing:
                        # this assumes param is a RooRealVar
                        param_setup[param_name] = param.getVal()
            else:
                param_setup = combine_dict(param_setup)
        elif param_setup is None:
            param_setup = {}
            if fill_missing:
                param_setup = {param.GetName(): param.getVal() for param in params}
        else:
            raise ValueError('invalid parameter setup format')
        return param_setup