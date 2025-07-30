import unittest

from quickstats.core.versions import Version

class TestVersion(unittest.TestCase):
    def test_init_with_string(self):
        v = Version("1.2.3")
        self.assertEqual((v.major, v.minor, v.micro), (1, 2, 3))
        
        v = Version("1.2")
        self.assertEqual((v.major, v.minor, v.micro), (1, 2, 0))
        
        with self.assertRaises(ValueError):
            Version("1.2.3.4")
        
        with self.assertRaises(ValueError):
            Version("1.2.a")
    
    def test_init_with_tuple(self):
        v = Version((1, 2, 3))
        self.assertEqual((v.major, v.minor, v.micro), (1, 2, 3))
        
        v = Version((1, 2))
        self.assertEqual((v.major, v.minor, v.micro), (1, 2, 0))
        
        with self.assertRaises(ValueError):
            Version((1, 2, 3, 4))
        
        with self.assertRaises(ValueError):
            Version((1, 2, 'a'))
    
    def test_comparisons(self):
        v1 = Version("1.2.3")
        v2 = Version("1.2.4")
        v3 = Version("1.3.0")
        v4 = Version((1, 2, 3))
        
        self.assertTrue(v1 == v4)
        self.assertTrue(v1 != v2)
        self.assertTrue(v1 < v2)
        self.assertTrue(v2 > v1)
        self.assertTrue(v3 >= v2)
        self.assertTrue(v1 <= v4)
        
        self.assertTrue(v1 == "1.2.3")
        self.assertTrue(v1 != "1.2.4")
        self.assertTrue(v1 < "1.2.4")
        self.assertTrue(v2 > "1.2.3")
        self.assertTrue(v3 >= "1.2.4")
        self.assertTrue(v1 <= "1.2.3")
        
        self.assertTrue(v1 == (1, 2, 3))
        self.assertTrue(v1 != (1, 2, 4))
        self.assertTrue(v1 < (1, 2, 4))
        self.assertTrue(v2 > (1, 2, 3))
        self.assertTrue(v3 >= (1, 2, 4))
        self.assertTrue(v1 <= (1, 2, 3))
        
    def test_str_and_repr(self):
        v = Version("1.2.3")
        self.assertEqual(str(v), "1.2.3")
        self.assertEqual(repr(v), "Version(major=1, minor=2, micro=3)")

if __name__ == "__main__":
    unittest.main()