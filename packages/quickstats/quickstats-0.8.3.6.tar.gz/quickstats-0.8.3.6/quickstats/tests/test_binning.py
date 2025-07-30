import unittest
import numpy as np

from quickstats.concepts import Binning

class TestBinning(unittest.TestCase):

    def test_binning_with_array(self):
        bins = [0, 1, 2, 3, 4]
        binning = Binning(bins)
        np.testing.assert_array_equal(binning.bin_edges, bins)
        np.testing.assert_array_equal(binning.bin_centers, [0.5, 1.5, 2.5, 3.5])
        np.testing.assert_array_equal(binning.bin_widths, [1, 1, 1, 1])
        self.assertEqual(binning.nbins, 4)
        self.assertTrue(binning.is_uniform())

    def test_binning_with_number(self):
        bins = 4
        bin_range = (0, 4)
        binning = Binning(bins, bin_range)
        np.testing.assert_array_equal(binning.bin_edges, [0, 1, 2, 3, 4])
        np.testing.assert_array_equal(binning.bin_centers, [0.5, 1.5, 2.5, 3.5])
        np.testing.assert_array_equal(binning.bin_widths, [1, 1, 1, 1])
        self.assertEqual(binning.nbins, 4)
        self.assertTrue(binning.is_uniform())

    def test_invalid_bins_array_length(self):
        bins = [0]
        with self.assertRaises(ValueError):
            Binning(bins)

    def test_invalid_bins_number(self):
        bins = 0
        bin_range = (0, 4)
        with self.assertRaises(ValueError):
            Binning(bins, bin_range)

    def test_missing_bin_range(self):
        bins = 4
        with self.assertRaises(ValueError):
            Binning(bins)

    def test_invalid_bin_range(self):
        bins = 4
        bin_range = (4, 0)
        with self.assertRaises(ValueError):
            Binning(bins, bin_range)

    def test_non_uniform_binning(self):
        bins = [0, 1, 3, 4]
        binning = Binning(bins)
        np.testing.assert_array_equal(binning.bin_edges, bins)
        np.testing.assert_array_equal(binning.bin_centers, [0.5, 2, 3.5])
        np.testing.assert_array_equal(binning.bin_widths, [1, 2, 1])
        self.assertEqual(binning.nbins, 3)
        self.assertFalse(binning.is_uniform())

if __name__ == '__main__':
    unittest.main()