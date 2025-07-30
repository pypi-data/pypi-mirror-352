# SPDX-FileCopyrightText: 2025 Florian Obersteiner / KIT
# SPDX-FileContributor: Florian Obersteiner <f.obersteiner@kit.edu>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

"""Tests for plottools.py module."""

import unittest

import numpy as np
import numpy.ma as ma

# Add the parent directory to the path so we can import pyfuppes
from pyfuppes.plottools import get_plot_range, nticks_yrange


class TestPlotTools(unittest.TestCase):
    """Test class for plottools.py functions."""

    def test_get_plot_range_basic(self):
        """Test basic functionality of get_plot_range."""
        # Test with a simple list
        v = [1, 2, 3, 4, 5]
        result = get_plot_range(v)
        self.assertEqual(len(result), 2)
        self.assertLess(result[0], 1)  # Lower bound should be less than min value
        self.assertGreater(result[1], 5)  # Upper bound should be greater than max value

    def test_get_plot_range_numpy_array(self):
        """Test get_plot_range with numpy array."""
        v = np.array([1, 2, 3, 4, 5])
        result = get_plot_range(v)
        expected_offset = (abs(1) + abs(5)) / 2 * 5 / 100  # 5% of the range
        self.assertAlmostEqual(result[0], 1 - expected_offset)
        self.assertAlmostEqual(result[1], 5 + expected_offset)

    def test_get_plot_range_masked_array(self):
        """Test get_plot_range with masked array."""
        v = ma.array([1, 2, 3, 4, 5, 6], mask=[0, 0, 0, 0, 0, 1])
        result = get_plot_range(v)
        expected_offset = (abs(1) + abs(5)) / 2 * 5 / 100
        self.assertAlmostEqual(result[0], 1 - expected_offset)
        self.assertAlmostEqual(result[1], 5 + expected_offset)

    def test_get_plot_range_with_limits(self):
        """Test get_plot_range with min and max limits."""
        v = [1, 2, 3, 4, 5]
        result = get_plot_range(v, v_min_lim=1.5, v_max_lim=4.5)
        self.assertEqual(result[0], 1.5)  # Should be clamped to min limit
        self.assertEqual(result[1], 4.5)  # Should be clamped to max limit

    def test_get_plot_range_with_xrange(self):
        """Test get_plot_range with x range filtering."""
        x = [1, 2, 3, 4, 5]
        v = [10, 20, 30, 40, 50]
        result = get_plot_range(v, xrange=[2, 4], x=x)
        expected_offset = (abs(20) + abs(40)) / 2 * 5 / 100
        self.assertAlmostEqual(result[0], 20 - expected_offset)
        self.assertAlmostEqual(result[1], 40 + expected_offset)

    def test_get_plot_range_with_nan(self):
        """Test get_plot_range with NaN values."""
        v = np.array([1, 2, np.nan, 4, 5])
        result = get_plot_range(v)
        expected_offset = (v[0] + v[-1]) / 2 * 5 / 100
        self.assertAlmostEqual(result[0], 1 - expected_offset)
        self.assertAlmostEqual(result[1], 5 + expected_offset)

    def test_get_plot_range_empty_or_single(self):
        """Test get_plot_range with empty or single-value arrays."""
        v = np.array([])
        result = get_plot_range(v)
        self.assertEqual(result, (-1, 1))  # Default range for empty arrays

        v = np.array([42])
        result = get_plot_range(v)
        self.assertEqual(result, (-1, 1))  # Default range for single value arrays

    def test_nticks_yrange_basic(self):
        """Test basic functionality of nticks_yrange."""
        yrange = [1.3, 5.7]
        result = nticks_yrange(yrange, nticks=5)
        self.assertEqual(result, (0.0, 20.0))

    def test_nticks_yrange_custom_multiple(self):
        """Test nticks_yrange with custom multiple."""
        yrange = [1.3, 5.7]
        result = nticks_yrange(yrange, nticks=5, range_as_multiple_of=5)
        self.assertEqual(result, (0.0, 20.0))

        yrange = [1.3, 1.7]
        result = nticks_yrange(yrange, nticks=5, range_as_multiple_of=1)
        self.assertEqual(result, (1.0, 5.0))

    def test_nticks_yrange_negative_values(self):
        """Test nticks_yrange with negative values."""
        yrange = [-5.7, 1.3]
        result = nticks_yrange(yrange, nticks=5)
        self.assertEqual(result, (-10.0, 10.0))  # Should handle negative values correctly

    def test_nticks_yrange_exact_multiples(self):
        """Test nticks_yrange with values that are exact multiples."""
        yrange = [10.0, 30.0]
        result = nticks_yrange(yrange, nticks=3)
        self.assertEqual(result, (10.0, 30.0))  # Should keep the range as is


if __name__ == "__main__":
    unittest.main()
