import unittest
import numpy as np

from quickstats.maths.interpolation import (
    get_intervals,
    get_regular_meshgrid,
    get_x_intersections,
    get_roots,
    get_minimum_1d,
    get_intervals_between_curves,
    interpolate_2d,
)


class TestGetIntervals(unittest.TestCase):
    def test_no_intersection(self):
        """All y < level => expect empty intervals."""
        x = np.array([0, 1, 2])
        y = np.array([0.0, 0.1, 0.2])
        level = 0.5

        intervals = get_intervals(x, y, level, delta=0.1)
        self.assertEqual(len(intervals), 0)

    def test_one_intersection_positive_slope(self):
        """
        One intersection, slope is +1 => intervals ~ [[-inf, x_intersect]].
        Using y = x, intersection with level=1.5 at x=1.5 => [-inf, 1.5].
        """
        x = np.array([0, 1, 2])
        y = np.array([0.0, 1.0, 2.0])  # slope +1
        level = 1.5
    
        intervals = get_intervals(x, y, level, delta=0.1)
        self.assertEqual(len(intervals), 1)
        # Intersection ~ x=1.5
        np.testing.assert_allclose(intervals[0, 1], 1.5, atol=0.2)
        self.assertTrue(np.isinf(intervals[0, 0]))
    
    def test_one_intersection_negative_slope(self):
        """
        One intersection, slope is -1 => intervals ~ [[x_intersect, +inf]].
        Using y = 2 - x, intersection with level=0.5 at x=1.5 => [1.5, inf].
        """
        x = np.array([0, 1, 2])
        y = np.array([2.0, 1.0, 0.0])  # slope -1
        level = 0.5
    
        intervals = get_intervals(x, y, level, delta=0.1)
        self.assertEqual(len(intervals), 1)
        np.testing.assert_allclose(intervals[0, 0], 1.5, atol=0.2)
        self.assertTrue(np.isinf(intervals[0, 1]))

    def test_two_intersections_shape(self):
        """
        Test that two intersections yield an array of shape (n_pairs, 2).
        """
        x = np.array([0, 1, 2, 3])
        y = np.array([0, 1, 2, 3])  # a line
        level = 1.5
        intervals = get_intervals(x, y, level, delta=0.1)
        # With this data, we might see something like [-inf, 1.5] and [1.5, inf]
        # or just a single pair. We'll just confirm shape:
        self.assertEqual(intervals.shape[1], 2)


class TestGetRegularMeshgrid(unittest.TestCase):
    def test_shapes(self):
        x = np.linspace(0, 10, 5)
        y = np.linspace(-5, 5, 5)
        X, Y = get_regular_meshgrid(x, y, n=10)
        # Expect shape (10, 10)
        self.assertEqual(X.shape, (10, 10))
        self.assertEqual(Y.shape, (10, 10))


class TestGetXIntersections(unittest.TestCase):
    def test_simple_line_intersection(self):
        """
        Lines y1=x and y2=2-x intersect at x=1.
        """
        x1 = np.array([0, 1, 2])
        y1 = np.array([0, 1, 2])

        x2 = np.array([0, 1, 2])
        y2 = np.array([2, 1, 0])

        intersections = get_x_intersections(x1, y1, x2, y2)
        self.assertEqual(len(intersections), 1)
        self.assertAlmostEqual(intersections[0], 1.0, delta=0.01)


class TestGetRoots(unittest.TestCase):
    def test_parabolic_roots(self):
        """
        y = x^2 - 1 => roots at x=-1 and x=1.
        """
        x_data = np.linspace(-2, 2, 5)  # [-2, -1, 0, 1, 2]
        y_data = x_data**2 - 1

        roots = get_roots(x_data, y_data, y_ref=0.0, delta=0.1)
        self.assertGreaterEqual(len(roots), 2)  # Might get extras if there's sign jitters
        # Check existence of something near -1 and +1
        # We'll do a sort:
        roots_sorted = np.sort(roots)
        # Just check the first and last
        self.assertTrue(np.isclose(roots_sorted[0], -1.0, atol=0.2))
        self.assertTrue(np.isclose(roots_sorted[-1], 1.0, atol=0.2))


class TestGetMinimum1D(unittest.TestCase):
    def test_simple_parabola(self):
        """
        y = (x-2)^2 => min at x=2, y=0
        """
        x_data = np.linspace(0, 4, 5)
        y_data = (x_data - 2) ** 2
        min_x, min_y = get_minimum_1d(x_data, y_data, kind='linear')
        self.assertAlmostEqual(min_x, 2.0, delta=0.2)
        self.assertAlmostEqual(min_y, 0.0, delta=0.2)


class TestGetIntervalsBetweenCurves(unittest.TestCase):
    def test_no_intersection(self):
        """
        Curves: y1=0, y2=1 => no intersection => empty array.
        """
        x1 = np.array([0, 1])
        y1 = np.array([0, 0])
        x2 = np.array([0, 1])
        y2 = np.array([1, 1])
        intervals = get_intervals_between_curves(x1, y1, x2, y2)
        self.assertEqual(intervals.size, 0)

    def test_one_intersection(self):
        """
        Lines y1=x, y2=1-x => intersect once at x=0.5 => two-element array
        with either [-inf, 0.5] or [0.5, inf].
        """
        x1 = np.array([0, 1])
        y1 = np.array([0, 1])
        x2 = np.array([0, 1])
        y2 = np.array([1, 0])
        intervals = get_intervals_between_curves(x1, y1, x2, y2)
        self.assertEqual(intervals.size, 2)  # shape (2,)

    def test_two_intersections(self):
        """
        Curves with exactly two intersections => returns shape (2,)
        or possibly a 2-element array. We'll confirm the size.
        """
        x1 = np.array([0, 1, 2])
        y1 = np.array([0, 1, 0])
        x2 = np.array([0, 1, 2])
        y2 = np.array([1, 0, 1])
        intervals = get_intervals_between_curves(x1, y1, x2, y2)
        # Should return two intersection points => array of length 2
        self.assertEqual(len(intervals), 2)

class TestInterpolate2D(unittest.TestCase):
    def test_predictable_linear_values(self):
        """
        Interpolate a linear function z=2*x + 3*y using method='linear'
        on a 3x3 grid. Verify the center point matches the expected 3.5.
        """
        x_data = np.array([0, 1, 2, 1])
        y_data = np.array([0, 0, 1, 1])
        # z = 2*x + 3*y
        z_data = 2.0 * x_data + 3.0 * y_data

        # Use 'linear' and a small grid n=3 => x in [0,1,2], y in [0,0.5,1]
        X, Y, Z = interpolate_2d(x_data, y_data, z_data, method='linear', n=3)

        # X, Y, Z each is shape (3, 3).
        # Middle cell [1,1] => X=1, Y=0.5 => expected z=2*1 + 3*0.5=3.5
        self.assertEqual(X.shape, (3, 3))
        self.assertEqual(Y.shape, (3, 3))
        self.assertEqual(Z.shape, (3, 3))

        # Check center of the grid
        z_center = Z[1,1]
        
        # Should be near 3.5 with linear interpolation
        self.assertTrue(np.isfinite(z_center), "Center point should not be NaN or Inf.")
        self.assertAlmostEqual(z_center, 3.5, places=5)

        # Optionally check corners
        # For example, top-right corner [2,2] => X=2, Y=1 => z=2*2 + 3*1=7
        z_corner = Z[2,2]

        # This corner is within the convex hull, so we expect ~7
        self.assertTrue(np.isfinite(z_corner))
        self.assertAlmostEqual(z_corner, 7.0, places=5)


if __name__ == "__main__":
    unittest.main()
