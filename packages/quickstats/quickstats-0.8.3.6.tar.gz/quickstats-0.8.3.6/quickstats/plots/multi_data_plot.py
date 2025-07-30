from __future__ import annotations

from typing import Dict, List, Optional, Union, Any, TypeVar

import pandas as pd

from .abstract_plot import AbstractPlot
from .colors import ColorType, ColormapType

T = TypeVar('T')

class MultiDataPlot(AbstractPlot):
    """
    Plot class supporting multiple datasets with customizable styles.

    This class extends AbstractPlot to handle multiple pandas DataFrames,
    allowing separate styling and labeling for each dataset.
    """

    DATA_TYPE: T = pd.DataFrame

    def __init__(
        self,
        data_map: Union[T, Dict[str, T]],
        color_map: Optional[Dict[str, ColorType]] = None,
        color_cycle: Optional[ColormapType] = None,
        color_cycle_map: Optional[Dict[str, ColormapType]] = None,
        label_map: Optional[Dict[str, str]] = None,
        styles: Optional[Dict[str, Any]] = None,
        styles_map: Optional[Dict[str, Union[Dict[str, Any], str]]] = None,
        analysis_label_options: Optional[Union[str, Dict[str, Any]]] = None,
        config: Optional[Dict[str, Any]] = None,
        config_map: Optional[Dict[str, Dict[str, Any]]] = None,
        figure_index: Optional[int] = None,        
        verbosity: Union[int, str] = 'INFO'
    ) -> None:
        """
        Initialize MultiDataPlot.

        Parameters
        ----------
        data_map : Union[pd.DataFrame, Dict[str, T]]
            Input data. Either a single data object or a dictionary mapping
            target names to data objects
        color_map : Optional[Dict[str, ColorType]], default None
            Mapping of targets to colors
        color_cycle : Optional[ColormapType], default None
            Color cycle for automatic color assignment
        label_map : Optional[Dict[str, str]], default None
            Mapping of targets to display labels
        styles : Optional[Dict[str, Any]], default None
            Global plot styles
        styles_map : Optional[Dict[str, Union[Dict[str, Any], str]]], default None
            Target-specific style overrides
        analysis_label_options : Optional[Union[str, Dict[str, Any]]], default None
            Options for analysis labels
        config : Optional[Dict[str, Any]], default None
            Additional configuration parameters
        config_map : Optional[Dict[str, Dict[str, Any]]], default None
            Target-specific configuration updates            

        Raises
        ------
        ValueError
            If data_map is not a DataFrame or valid dictionary
        """
        self.load_data(data_map)
        
        super().__init__(
            color_map=color_map,
            color_cycle=color_cycle,
            color_cycle_map=color_cycle_map,
            label_map=label_map,
            styles=styles,
            styles_map=styles_map,
            analysis_label_options=analysis_label_options,
            config=config,
            config_map=config_map,
            figure_index=figure_index,
            verbosity=verbosity
        )

    def load_data(self, data_map: Union[T, Dict[str, T]]) -> None:
        """
        Load data into plot instance.

        Parameters
        ----------
        data_map : Union[pd.DataFrame, Dict[str, pd.DataFrame]]
            Input data. Single DataFrame will be stored with key None

        Raises
        ------
        ValueError
            If any value in data_map dictionary is not a DataFrame
        """
        if isinstance(data_map, self.DATA_TYPE):
            self.data_map: DataFrameMap = {None: data_map}
        else:
            for key, value in data_map.items():
                if not isinstance(value, self.DATA_TYPE):
                    raise ValueError(
                        f"Value for key '{key}' is not a {self.DATA_TYPE.__name__}"
                    )
            self.data_map = data_map

    def is_single_data(self) -> bool:
        """
        Check if plot contains only a single dataset.

        Returns
        -------
        bool
            True if only one dataset is present with key None
        """
        return len(self.data_map) == 1 and None in self.data_map

    def resolve_targets(
        self,
        targets: Optional[List[str]] = None
    ) -> List[Optional[str]]:
        """
        Resolve target names for plotting.

        Parameters
        ----------
        targets : Optional[List[str]], default None
            Requested target names. If None, uses all available targets

        Returns
        -------
        List[Optional[str]]
            Resolved list of target names

        Raises
        ------
        ValueError
            If targets specified for single dataset or invalid targets provided
        """
        if self.is_single_data():
            if targets and set(targets) != {None}:
                raise ValueError(
                    "Cannot specify targets when only one dataset is present"
                )
            return [None]

        if targets is None:
            return list(self.data_map.keys())

        # Validate all requested targets exist
        invalid_targets = set(targets) - set(self.data_map.keys())
        if invalid_targets:
            raise ValueError(
                f"Invalid targets specified: {sorted(invalid_targets)}"
            )

        return targets