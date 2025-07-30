from typing import Dict, Union, List, Optional, Tuple

from quickstats import AbstractObject

class RooDataHist(AbstractObject):

    @staticmethod
    def get_datahist_map(dataset_dict: Dict[str, "ROOT.RooDataHist"]):
        from quickstats.interface.cppyy.basic_methods import get_std_object_map
        datahist_map = get_std_object_map(dataset_dict, 'RooDataHist')
        return datahist_map