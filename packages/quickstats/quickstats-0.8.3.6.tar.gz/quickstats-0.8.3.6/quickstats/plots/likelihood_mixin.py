from __future__ import annotations

from typing import Optional, Dict, Union, Tuple

from quickstats.maths.numerics import str_encode_value, is_integer
from quickstats.maths.statistics import sigma_to_chi2, confidence_level_to_chi2
from .abstract_plot import AbstractPlot

class LikelihoodMixin(AbstractPlot):
    """
    Mixin class for likelihood plots providing statistical confidence level handling.
    
    This mixin adds functionality for working with confidence levels and sigma 
    levels in likelihood plots, including chi-square conversion and labeling.
    """

    DOF: int = 1

    LABEL_MAP: Dict[str, str] = {
        'confidence_level': '{level:.0%} CL',
        'sigma_level': r'{level:.0g} $\sigma$',
    }

    CONFIG: Dict[str, Dict[str, str]] = {
        'level_key': {
            'confidence_level': '{level_str}_CL',
            'sigma_level': '{level_str}_sigma',
        }
    }
    
    def get_chi2_value(self, level: Union[int, float], use_sigma: bool = False) -> float:
        """Convert confidence/sigma level to chi-square value."""
        if use_sigma:
            return sigma_to_chi2(level, k=self.DOF)
        return confidence_level_to_chi2(level, self.DOF)
            
    def get_level_label(self, level: Union[int, float], use_sigma: bool = False) -> str:
        """Get formatted label for confidence/sigma level."""
        key = 'sigma_level' if use_sigma else 'confidence_level'
        return self.label_map.get(key, '').format(level=level)

    def get_level_key(self, level: Union[int, float], use_sigma: bool = False) -> str:
        """Get dictionary key for confidence/sigma level."""
        key = 'sigma_level' if use_sigma else 'confidence_level'
        if is_integer(level):
            level_str = str(int(level))
        else:
            level_str = str_encode_value(level)
        return self.config.get('level_key', {}).get(key, '').format(level_str=level_str)

    def get_level_specs(
        self,
        sigma_levels: Optional[Tuple[Union[int, float], ...]] = None,
        confidence_levels: Optional[Tuple[float, ...]] = None
    ) -> Dict[str, Dict[str, Union[float, str]]]:
        """
        Get specifications for all confidence/sigma levels.

        Parameters
        ----------
        sigma_levels : Optional[Tuple[Union[int, float], ...]]
            Sigma levels to include
        confidence_levels : Optional[Tuple[float, ...]]
            Confidence levels to include

        Returns
        -------
        Dict[str, Dict[str, Union[float, str]]]
            Dictionary of level specifications, sorted by chi-square value
        """
        specs = {}
        for levels, use_sigma in [(sigma_levels, True), (confidence_levels, False)]:
            if not levels:
                continue
            for level in levels:
                chi2 = self.get_chi2_value(level, use_sigma)
                label = self.get_level_label(level, use_sigma)
                key = self.get_level_key(level, use_sigma)
                specs[key] = {'chi2': chi2, 'label': label}
                
        # make sure the levels are ordered in increasing chi2
        return dict(sorted(specs.items(), key=lambda x: x[1]['chi2']))