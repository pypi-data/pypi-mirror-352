import unittest
import numpy as np

from quickstats.interface.root import RooDataSet

class TestRooDataSet(unittest.TestCase):

    def load_dummy_dataset(self):
        pass
    
    def test_from_numpy(self):
        import ROOT
        import pandas as pd
        import numpy as np
        from quickstats.interface.root import RooDataSet
        from quickstats.interface.root.roofit_extension import get_var_default_value
        arrays = {
            'a': np.random.rand(300),
            'b': np.random.rand(300),
            'c': np.random.rand(300),
            'cat': np.random.choice([0,1,2], 300)
        }
        
        import ROOT
        cat = ROOT.RooCategory('cat', 'cat')
        cat.defineType('cat_a', 0)
        cat.defineType('cat_b', 1)
        cat.defineType('cat_c', 2)
        var_a = ROOT.RooRealVar('a', 'a', 1)
        var_a.setRange(0, 1.5)
        var_a.setBins(15)
        var_b = ROOT.RooRealVar('b', 'b', 1)
        var_b.setRange(0, 1.5)
        var_b.setBins(15)
        var_c = ROOT.RooRealVar('c', 'c', 1)
        var_c.setRange(0, 1.5)
        var_c.setBins(15)
        cat_data = arrays['cat']
        arrays['a'][cat_data != 0] = get_var_default_value(var_a)
        arrays['b'][cat_data != 1] = get_var_default_value(var_b)
        arrays['c'][cat_data != 2] = get_var_default_value(var_c)
        variables = ROOT.RooArgSet(var_a, var_b, var_c, cat)
        dataset = RooDataSet.from_numpy(arrays, variables, apply_ghost=True, blind_range=[0.2, 0.8])

    def test_counting_dataset(self):
        import ROOT
        observable = ROOT.RooRealVar("myy", "myy", 1)
        observable.setRange(120, 130)
        dataset = RooDataSet.from_counting(23, observable=observable)

    def test_txt_dataset(self):
        import ROOT
        filename = "dummy_file_name.txt"
        observable = ROOT.RooRealVar("myy", "myy", 125)
        observable.setRange(105, 160)
        observable.setBins(220)
        dataset = RooDataSet.from_txt(filename, observable, apply_ghost=True, blind_condition=lambda x: x > 110)

    def test_ntuple_dataset(self):
        import ROOT
        filename = "dummy_file_name.root"
        observable = ROOT.RooRealVar("myy", "myy", 125)
        observable.setRange(105, 160)
        observable.setBins(220)
        dataset = RooDataSet.from_ntuples(filename, observable, observable_branchname='myy', blind_condition=lambda x : x > 120)

    def test_bin_dataset(self):
        dataset = self.load_dummy_dataset()
        binned_dataset = RooDataSet.bin_dataset(model.data)

if __name__ == '__main__':
    unittest.main()
