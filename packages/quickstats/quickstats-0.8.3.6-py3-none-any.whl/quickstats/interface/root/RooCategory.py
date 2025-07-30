from typing import Dict, Union, List, Optional, Tuple
import copy

import numpy as np

from quickstats import semistaticmethod, cached_import

class RooCategory:
    
    def __init__(self, category:"ROOT.RooCategory"):
        self.parse(category)
        
    def parse(self, category:"ROOT.RooCategory"):
        if isinstance(category, RooCategory):
            self.__dict__ = copy.deepcopy(category.__dict__)
        else:
            isvalid = hasattr(category, 'ClassName') and (category.ClassName() == 'RooCategory')
            if not isvalid:
                raise ValueError("object must be an instance of ROOT.RooCategory")
            self.name  = category.GetName()
            self.title = category.GetTitle()
            n_cat = len(category)
            self.category_labels = [''] * n_cat
            for category_data in category:
                self.category_labels[category_data.second] = category_data.first

    def new(self):
        ROOT = cached_import("ROOT")
        category = ROOT.RooCategory(self.name, self.title)
        for category_label in self.category_labels:
            category.defineType(category_label)
        ROOT.SetOwnership(category, False)
        return category